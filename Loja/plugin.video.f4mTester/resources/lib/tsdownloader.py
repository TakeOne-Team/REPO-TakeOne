# -*- coding: utf-8 -*-
import os
try:
    from kodi_helper import requests, six
except ImportError:
    import six
    import requests
if six.PY3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import urlparse, parse_qs
    from urllib import quote, unquote, unquote_plus
from collections import deque    
import threading
import time
import re
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log(msg):
    logger.info(msg)

HOST_NAME = '127.0.0.1'
PORT_NUMBER = 55319

global HEADERS_BASE
global STOP_SERVER
HEADERS_BASE = {}
STOP_SERVER = False

url_proxy = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/?url='
url_stop = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/stop'
url_reset = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/reset'

chunks_lock = threading.Lock()
chunk_size = 4096
chunks = deque(maxlen=int(chunk_size))

def ts_download(url,headers):
    global STOP_SERVER
    while True:
        if STOP_SERVER:
            break
        try:
            with requests.get(url, headers=headers, stream=True, timeout=18000) as response:
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if not STOP_SERVER:
                            with chunks_lock:
                                try:
                                    chunks.append(chunk)
                                except:
                                    pass
                        else:
                            break
                else:
                    log('Erro na requisição: %s'%str(response.status_code))
        except requests.exceptions.RequestException as e:
            log('Erro na requisição: %s'%str(e))
        except Exception as e:
            log('Erro geral %s'%str(e))

class ProxyHandler(BaseHTTPRequestHandler):
    def convert_to_ts(self,url):
        if '/live/' in url and url.count('/') == 6 and '.m3u8' in url:
            url = url.replace('/live', '').replace('.m3u8', '')
        return url

    def set_headers(self,url):
        global HEADERS_BASE        
        headers_default = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0', 'Connection': 'keep-alive'}
        headers = {}
        if 'User-Agent' in url:
            try:
                user_agent = url.split('User-Agent=')[1]
                try:
                    user_agent = user_agent.split('&')[0]
                except:
                    pass
                try:
                    user_agent = unquote_plus(user_agent)
                except:
                    pass
                try:
                    user_agent = unquote(user_agent)
                except:
                    pass
                if 'Mozilla' in user_agent:
                    headers['User-Agent'] = user_agent
            except:
                pass
        if 'Referer' in url:
            try:
                referer = url.split('Referer=')[1]
                try:
                    referer = referer.split('&')[0]
                except:
                    pass
                try:
                    referer = unquote_plus(referer)
                except:
                    pass
                try:
                    referer = unquote(referer)
                except:
                    pass                
                headers['Referer'] = referer
            except:
                pass
        if 'Origin' in url:
            try:
                origin = url.split('Origin=')[1]
                try:
                    origin = origin.split('&')[0]
                except:
                    pass
                try:
                    origin = unquote_plus(origin)
                except:
                    pass
                try:
                    origin = unquote(origin)
                except:
                    pass                
                headers['Origin'] = origin
            except:
                pass
        #HEADERS_ = headers if headers else headers_default
        if headers != {}:
            headers.update({'Connection': 'keep-alive'})
            HEADERS_ = headers
        else:
            HEADERS_ = headers_default
        if HEADERS_BASE == {}:
            HEADERS_BASE = HEADERS_

    def parse_stream(self,url):
        global HEADERS_BASE
        global STOP_SERVER
        if '.m3u8' in url or '.mp4' in url or '.avi' in url:
            log('iniciando encerramento')
            STOP_SERVER = True           
            def shutdown(server):
                server.shutdown()
                try:
                    server.server_close()
                except:
                    pass
            t = threading.Thread(target=shutdown, args=(self.server, ))
            t.start()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "video/mp2t")
            self.end_headers()
            # Iniciar a thread se ainda não estiver rodando
            if not threading.active_count() > 2:  # Checa se há threads ativas
                thread = threading.Thread(target=ts_download, args=(url,HEADERS_BASE))
                thread.start()

            while True:
                if not STOP_SERVER:
                    with chunks_lock:
                        if chunks:
                            chunk = chunks.popleft()
                            self.wfile.write(chunk)
                        else:
                            time.sleep(0.1)  # Aguarda um pouco se não houver chunks
                else:
                    break                        

    def do_HEAD(self):
        if self.path == '/check':
            self.send_response(200)
            self.end_headers()             
        elif self.path == '/stop':            
            def shutdown(server):
                server.shutdown()
                try:
                    server.server_close()
                except:
                    pass
            t = threading.Thread(target=shutdown, args=(self.server, ))
            t.start()                           

    def do_GET(self):
        global STOP_SERVER
        global HEADERS_BASE
        if self.path == '/check':
            self.send_response(200)
            self.end_headers() 
        else:                
            url_path = unquote_plus(self.path)
            self.set_headers(url_path)     
            url_parts = urlparse(url_path)
            query_params = parse_qs(url_parts.query)
            if 'url' in query_params:
                # url = query_params['url'][0]
                url = url_path.split('url=')[1]
                try:
                    url = url.split('|')[0]
                except:
                    pass
                try:
                    url = url.split('%7C')[0]
                except:
                    pass
                url = self.convert_to_ts(url)
            else:
                url = url_path
        log('acesssando url: %s'%url)
        self.parse_stream(url)

def serve_forever(httpd):
    httpd.serve_forever()


class Server:
    def __init__(self):
        try:
            self.httpd = HTTPServer((HOST_NAME, PORT_NUMBER), ProxyHandler)
            self.server_instance = True
        except:
            self.server_instance = False
        if self.server_instance:
            try:
                self.server = threading.Thread(target=serve_forever, args=(self.httpd, ))
                self.server_thread = True
            except:
                self.server_thread = False
        else:
            self.server_thread = False

    def in_use(self):
        url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/check'
        use = False
        try:
            r = requests.head(url,timeout=1)
            if r.status_code == 200:
                use = True
        except:
            pass
        return use             

    def start(self):
        if not self.in_use():
            if self.server_thread:
                self.server.start()                        
