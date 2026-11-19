import io,json,unittest
from unittest.mock import patch
from server_lib.http import map_config,local_search
from server_lib.places import LocalSearch
class Request:
 def __init__(self,path='/api/map-config',headers=None):self.path=path;self.headers=headers or {'Host':'example.vercel.app'};self.wfile=io.BytesIO();self.status=None
 def send_response(self,status):self.status=status
 def send_header(self,*args):pass
 def end_headers(self):pass
 def payload(self):return json.loads(self.wfile.getvalue())
class ApiTests(unittest.TestCase):
 def test_public_config_never_returns_search_credentials(self):
  with patch.dict('os.environ',{'NAVER_MAP_CLIENT_ID':'map-public','NAVER_SEARCH_CLIENT_SECRET':'private-test-secret'},clear=True):
   r=Request();map_config(r);self.assertEqual(r.payload(),{'map_client_id':'map-public'})
 def test_cross_origin_rejected(self):
  r=Request(headers={'Host':'example.vercel.app','Origin':'https://other.example'});map_config(r);self.assertEqual(r.status,403)
 def test_missing_credentials_not_server_crash(self):
  from server_lib.http import features
  code=features()[0]['properties']['code']
  with patch.dict('os.environ',{},clear=True):
   r=Request('/api/local-search?area='+str(code)+'&q=cafe');local_search(r);self.assertEqual(r.status,503);self.assertEqual(r.payload()['code'],'NOT_CONFIGURED')
 def test_geometry_filter_missing_and_duplicates(self):
  feature={'properties':{'code':'x','name':'테스트'},'geometry':{'type':'Polygon','coordinates':[[[127,37],[127.01,37],[127.01,37.01],[127,37.01],[127,37]]]}}
  good={'title':'<b>카페</b>','address':'서울','mapx':127.005,'mapy':37.005}
  items=[good,good,{'title':'좌표없음'},{'title':'먼곳','mapx':128,'mapy':38}]
  service=LocalSearch([feature],'test-id','test-secret',opener=lambda *a,**k:io.BytesIO(json.dumps({'items':items}).encode()))
  result=service.search('x','카페 검색');self.assertEqual(len(result['items']),1);self.assertEqual(result['items'][0]['name'],'카페');self.assertEqual(result['excluded'],{'missing_coordinates_or_name':1,'outside_radius':1,'duplicates':1})
if __name__=='__main__':unittest.main()
