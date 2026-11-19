"""원본 지역검색·좌표·상권 경계 필터 복제. 키는 환경변수로만 전달합니다."""
from __future__ import annotations
import argparse,getpass,html,json,math,os,re,socket,ssl,sys
from datetime import datetime,timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlencode,urlsplit,unquote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
ENDPOINT='https://naverapihub.apigw.ntruss.com/search/v1/local'
RADIUS=500
def tls_context():
 context=ssl.create_default_context()
 # python.org macOS Python에서 기본 CA 파일이 설치되지 않은 경우 OS CA를 사용합니다.
 # 명시적으로 지정한 인증서 경로는 유지하며 검증/호스트명 확인을 끄지 않습니다.
 if not context.cert_store_stats()['x509_ca'] and not(os.environ.get('SSL_CERT_FILE') or os.environ.get('SSL_CERT_DIR')):
  system_ca=Path('/etc/ssl/cert.pem')
  if sys.platform=='darwin' and system_ca.is_file():context.load_verify_locations(cafile=str(system_ca))
 return context

def verified_urlopen(request,timeout=10):
 return urlopen(request,timeout=timeout,context=tls_context())

class SearchError(Exception):
 def __init__(self,status,code,message):self.status=status;self.code=code;self.message=message
class TextOnly(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.text=[]
 def handle_data(self,data):self.text.append(data)
def clean(value):
 p=TextOnly();p.feed(str(value or '')[:5000]);return ''.join(p.text).strip()
def coords(x,y):
 try:
  lng,lat=float(x),float(y)
  if abs(lng)>180:lng/=10_000_000
  if abs(lat)>90:lat/=10_000_000
  if not(math.isfinite(lng) and math.isfinite(lat) and 124<=lng<=132 and 33<=lat<=39):return None
  return [lng,lat]
 except (TypeError,ValueError,OverflowError):return None
def inside_ring(point,ring):
 x,y=point;inside=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def relation(point,geometry):
 polygons=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates']
 if any(inside_ring(point,p[0]) and not any(inside_ring(point,h) for h in p[1:]) for p in polygons):return 'inside',0.
 # 서울 규모에서 경계 선분까지의 직선거리 근사. 구멍/다중 경계도 포함합니다.
 lng,lat=point;rad=math.pi/180;earth=6371008.8
 def project(p):return ((p[0]-lng)*rad*earth*math.cos(lat*rad),(p[1]-lat)*rad*earth)
 best=math.inf
 for polygon in polygons:
  for ring in polygon:
   for a,b in zip(ring,ring[1:]+ring[:1]):
    ax,ay=project(a);bx,by=project(b);dx,dy=bx-ax,by-ay;length=dx*dx+dy*dy
    t=max(0.,min(1.,-(ax*dx+ay*dy)/length)) if length else 0.
    best=min(best,math.hypot(ax+t*dx,ay+t*dy))
 return 'nearby',best
class LocalSearch:
 def __init__(self,features,client_id='',client_secret='',opener=None):
  self.features={f['properties']['code']:f for f in features};self.client_id=client_id;self.client_secret=client_secret;self.opener=opener or verified_urlopen
 @property
 def configured(self):return bool(self.client_id and self.client_secret)
 def search(self,area,query):
  if area not in self.features:raise SearchError(400,'INVALID_AREA','지도에 있는 상권을 먼저 선택하세요.')
  query=' '.join(query.split())
  if not 2<=len(query)<=100 or any(ord(c)<32 for c in query):raise SearchError(400,'INVALID_QUERY','검색어는 2~100자로 입력하세요.')
  if not self.configured:raise SearchError(503,'NOT_CONFIGURED','지역검색 환경변수가 없습니다. Vercel에 NAVER_SEARCH_CLIENT_ID와 NAVER_SEARCH_CLIENT_SECRET을 설정한 뒤 재배포해 주세요.')
  request=Request(ENDPOINT+'?'+urlencode({'query':query,'display':5,'start':1,'sort':'random','format':'json'}),headers={'X-NCP-APIGW-API-KEY-ID':self.client_id,'X-NCP-APIGW-API-KEY':self.client_secret})
  try:
   with self.opener(request,timeout=10) as response:
    raw=response.read(1_000_001)
   if len(raw)>1_000_000:raise ValueError('size')
   payload=json.loads(raw)
   if not isinstance(payload,dict) or not isinstance(payload.get('items'),list):raise ValueError('schema')
  except HTTPError as e:
   e.close()
   if e.code in (401,403):raise SearchError(502,'AUTH_FAILED','지역검색 인증 또는 권한 확인에 실패했습니다. NAVER API HUB 키와 지역 검색 권한을 확인하세요.') from None
   if e.code==429:raise SearchError(429,'RATE_LIMIT','지역검색 호출 한도를 초과했습니다. 잠시 후 다시 시도하세요.') from None
   raise SearchError(502,'UPSTREAM_ERROR','네이버 지역검색 응답 오류입니다. 잠시 후 다시 시도하세요.') from None
  except URLError as e:
   if isinstance(e.reason,ssl.SSLCertVerificationError):raise SearchError(502,'TLS_ERROR','Python의 HTTPS 인증서 검증에 실패했습니다. 서버를 최신 코드로 다시 시작하고 인증서 설정을 확인하세요.') from None
   if isinstance(e.reason,socket.gaierror):raise SearchError(504,'DNS_ERROR','네이버 API 주소를 찾지 못했습니다. 인터넷·DNS 연결을 확인하세요.') from None
   raise SearchError(504,'NETWORK_ERROR','지역검색 서버 연결에 실패했습니다. 네트워크를 확인하고 다시 시도하세요.') from None
  except ssl.SSLError:raise SearchError(502,'TLS_ERROR','HTTPS 인증서 설정에 문제가 있습니다. 인증서 경로와 서버 실행 환경을 확인하세요.') from None
  except (TimeoutError,socket.timeout):raise SearchError(504,'TIMEOUT','지역검색 서버 응답 시간이 초과됐습니다. 잠시 후 다시 시도하세요.') from None
  except (ValueError,TypeError):raise SearchError(502,'INVALID_RESPONSE','지역검색 응답 형식을 확인하지 못했습니다.') from None
  feature=self.features[area];items=[];seen=set();missing=outside=duplicates=0
  for original in payload['items'][:5]:
   if not isinstance(original,dict):missing+=1;continue
   point=coords(original.get('mapx'),original.get('mapy'))
   if point is None:missing+=1;continue
   location,distance=relation(point,feature['geometry'])
   if distance>RADIUS:outside+=1;continue
   title=clean(original.get('title'));address=clean(original.get('roadAddress') or original.get('address'))
   if not title:missing+=1;continue
   key=(title,address,round(point[0],6),round(point[1],6))
   if key in seen:duplicates+=1;continue
   seen.add(key);link=str(original.get('link') or '')
   try:
    if urlsplit(link).scheme not in ('http','https'):link=''
   except ValueError:link=''
   items.append({'name':title,'address':address or None,'category':clean(original.get('category')) or None,'longitude':point[0],'latitude':point[1],'location':location,'boundary_distance_m':round(distance),'link':link or None})
  return {'source':'NAVER API HUB 지역 검색','area_code':area,'area_name':feature['properties']['name'],'query':query,'radius_m':RADIUS,'fetched_at':datetime.now(timezone.utc).isoformat(),'returned_count':len(payload['items'][:5]),'excluded':{'missing_coordinates_or_name':missing,'outside_radius':outside,'duplicates':duplicates},'items':items,'notice':'검색 상위 최대 5개 중 상권 내부/경계 약 500m 이내만 표시합니다. 영업·독립 브랜드·팝업·제휴 여부는 미확인입니다.'}
