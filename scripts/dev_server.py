"""로컬 미리보기: Vercel과 같은 API 어댑터 + 정적 파일. 외부 패키지 불필요."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from urllib.parse import urlsplit,unquote
import os,sys,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from server_lib.http import map_config,local_search

def load_env():
 path=ROOT/'.env'
 if not path.is_file():return
 for line in path.read_text().splitlines():
  line=line.strip().removeprefix('export ').strip()
  if not line or line.startswith('#') or '=' not in line:continue
  key,value=line.split('=',1);key=key.strip()
  if key in {'NAVER_MAP_CLIENT_ID','NAVER_SEARCH_CLIENT_ID','NAVER_SEARCH_CLIENT_SECRET'}:os.environ.setdefault(key,value.strip().strip('\"\''))

class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  path=urlsplit(self.path).path
  if path=='/api/map-config':return map_config(self)
  if path=='/api/local-search':return local_search(self)
  if path in ['/index-improved.html','/workspace.html']:self.path='/index.html'
  if path=='/':self.path='/index.html'
  target=(ROOT/'public'/unquote(urlsplit(self.path).path).lstrip('/')).resolve()
  if ROOT/'public' not in target.parents or not target.is_file():return self.send_error(404)
  return super().do_GET()
 def list_directory(self,path):return self.send_error(404)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8767);args=parser.parse_args();load_env()
 from build_static import ROOT as _root
 # Execute the deterministic static copy before serving.
 server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT/'public')))
 print(f'열기: http://localhost:{args.port}/',flush=True);print('종료: Control+C',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
