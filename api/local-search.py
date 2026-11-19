from http.server import BaseHTTPRequestHandler
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server_lib.http import local_search,reply

class handler(BaseHTTPRequestHandler):
 def do_GET(self):local_search(self)
 def do_POST(self):reply(self,405,{'code':'METHOD_NOT_ALLOWED','message':'GET 요청만 지원합니다.'})
 def log_message(self,*args):pass
