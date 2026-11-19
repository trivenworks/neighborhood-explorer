"""Vercel request adapters; credentials never go to browser responses or logs."""
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import json,os,re
from .places import LocalSearch,SearchError

def reply(request,status,payload):
 data=json.dumps(payload,ensure_ascii=False).encode('utf-8')
 request.send_response(status);request.send_header('Content-Type','application/json; charset=utf-8');request.send_header('Cache-Control','no-store');request.send_header('X-Content-Type-Options','nosniff');request.send_header('Content-Length',str(len(data)));request.end_headers();request.wfile.write(data)

def same_origin(request):
 host=(request.headers.get('X-Forwarded-Host') or request.headers.get('Host') or '').split(',')[0].strip().lower()
 origin=request.headers.get('Origin');site=request.headers.get('Sec-Fetch-Site','')
 if site=='cross-site' or (origin and urlsplit(origin).netloc.lower()!=host):
  reply(request,403,{'code':'SAME_ORIGIN_ONLY','message':'같은 웹사이트에서만 요청할 수 있습니다.'});return False
 return True

@lru_cache(maxsize=1)
def features():
 return json.loads((Path(__file__).parent/'areas.json').read_text())

def map_config(request):
 if not same_origin(request):return
 key=os.environ.get('NAVER_MAP_CLIENT_ID','').strip()
 if key and not re.fullmatch(r'[A-Za-z0-9_-]+',key):key=''
 reply(request,200,{'map_client_id':key})  # 지도용 공개 ID만 전달. 검색 키/Secret은 제외.

def local_search(request):
 if not same_origin(request):return
 params=parse_qs(urlsplit(request.path).query)
 service=LocalSearch(features(),os.environ.get('NAVER_SEARCH_CLIENT_ID','').strip(),os.environ.get('NAVER_SEARCH_CLIENT_SECRET','').strip())
 try:reply(request,200,service.search(params.get('area',[''])[0],params.get('q',[''])[0]))
 except SearchError as error:reply(request,error.status,{'code':error.code,'message':error.message})
