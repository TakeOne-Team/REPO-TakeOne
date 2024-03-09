# -*- coding: utf-8 -*-
import six
if six.PY3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import urlparse, parse_qs
    from urllib import quote, unquote, unquote_plus
import threading
import time
import requests
import re
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log(msg):
    logger.info(msg)


HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8087

url_proxy = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/?url='

global URL_BASE
global LAST_URL
global HEADERS_BASE
global STOP_SERVER
global CACHE_CHUNKS
global CACHE_M3U8
global DELAY_MODE
DELAY_MODE = True
URL_BASE = ''
LAST_URL = ''
HEADERS_BASE = {}
STOP_SERVER = False
CACHE_CHUNKS = []
CACHE_M3U8 = ''

class ProxyHandler(BaseHTTPRequestHandler):

    def basename(self,p):
        """Returns the final component of a pathname"""
        i = p.rfind('/') + 1
        return p[i:]
    
    def convert_to_m3u8(self,url):
        if '|' in url:
            url = url.split('|')[0]
        elif '%7C' in url:
            url = url.split('%7C')[0]
        if not '.m3u8' in url and not '/hl' in url and int(url.count(":")) == 2 and int(url.count("/")) > 4:
            parsed_url = urlparse(url)
            try:
                host_part1 = '%s://%s'%(parsed_url.scheme,parsed_url.netloc)
                host_part2 = url.split(host_part1)[1]
                url = host_part1 + '/live' + host_part2
                file = self.basename(url)
                if '.ts' in file:
                    file_new = file.replace('.ts', '.m3u8')
                    url = url.replace(file, file_new)
                else:
                    file_new = file + '.m3u8'
                    url = url.replace(file, file_new)
            except:
                pass
        return url    

    def set_headers(self,url):
        global URL_BASE
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
                             
    def base_url(self,url):
        global HEADERS_BASE
        try:
            for i in range(7):
                r = requests.get(url,headers=HEADERS_BASE, timeout=3, verify=False)
                if r.status_code == 200:
                    url = r.url
                    break
        except:
            pass
        filename = url.split('/')[-1]
        if not '.m3u8' in filename:
            url = url.split('?')[0]
            filename = url.split('/')[-1]
            url = url.split(filename)[0]
        else:
            url = url.replace(filename, '')
        return url
    
    def make_m3u8(self,m3u):
        padrao = r'#EXTINF:\d+\.\d+,\n/hl.+?/[^/]+\d+\.ts\?[^#]+'
        padrao2 = r'#EXTINF:\d+\.\d+,\n/hl.+?/[^/]+\d+\.ts'
        resultados = re.findall(padrao, m3u)
        if not resultados:
            resultados = re.findall(padrao2, m3u)
        if resultados:
            base_m3u = m3u.split('#EXTINF')[0]
            duas_ultimas_linhas = resultados[-1:]
            for linha in duas_ultimas_linhas:
                base_m3u += linha
            m3u = base_m3u
        return m3u

    def magical_hls(self,url):
        global DELAY_MODE
        if '/hl' in url and not 'https' in url:
            segment = re.findall('ls/(.*?).ts', url)
            segment2 = re.findall('/(.*?).ts',url)
            if segment and DELAY_MODE:
                try:
                    s = segment[0]
                    file, part = s.split('_')
                    part = int(part) - 2
                    new_s = file + '_' + str(part)
                    url = url.replace(s, new_s)
                except:
                    pass
            elif segment2 and DELAY_MODE:
                try:
                    s = segment2[0]
                    file, part = s.split('_')
                    part = int(part) - 2
                    new_s = file + '_' + str(part)
                    url = url.replace(s, new_s)
                except:
                    pass            
                
        return url      

    def parse_stream(self,url):
        global URL_BASE
        global LAST_URL
        global HEADERS_BASE
        global STOP_SERVER
        global CACHE_CHUNKS
        global CACHE_M3U8
        global DELAY_MODE    
        try:
            url = url.split('|')[0]
        except:
            pass
        try:
            url = url.split('%7C')[0]
        except:
            pass

        if '.html' in url:
            for i in range(4):
                if STOP_SERVER:
                    break
                log('Sending %s'%url)
                try:
                    r = requests.get(url, headers=HEADERS_BASE, allow_redirects=True, stream=True, verify=False)
                    code = r.status_code
                    log('Status Code: %s'%str(code))
                    if code == 200:
                        CACHE_CHUNKS = []
                        self.send_response(200)
                        self.send_header('Content-type','video/mp2t')
                        self.end_headers()
                        for chunk in r.iter_content(300000):                           
                            try:
                                self.wfile.write(chunk)
                                CACHE_CHUNKS.append(chunk)
                            except:
                                pass
                        
                        break
                    else:
                        if CACHE_CHUNKS:
                            self.send_response(200)
                            self.send_header('Content-type','video/mp2t')
                            self.end_headers()
                            try:
                                self.wfile.write(CACHE_CHUNKS[-1])
                            except:
                                pass
                                                 
                except:
                    pass
        elif '.m3u8' in url or '.php' in url:
            try:
                user_agent = self.headers.get('User-Agent', '')
            except:
                user_agent = ''
            if not URL_BASE:
                URL_BASE = self.base_url(url)
                LAST_URL = url
            elif URL_BASE:
                if 'http' in url:
                    last_parse = urlparse(LAST_URL)
                    last_host = '%s://%s'%(last_parse.scheme,last_parse.netloc)
                    url_parse = urlparse(url)
                    url_host = '%s://%s'%(url_parse.scheme,url_parse.netloc)
                    if last_host != url_host:
                        URL_BASE = self.base_url(url)
            if not 'http' in url:
                if url.startswith('/'):
                    url = url[1:]             
                url = URL_BASE + url
            self.send_response(200)
            # if 'Mozilla' in user_agent:
            #     self.send_header('Content-type', 'text/html')
            # else:
            self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
            self.end_headers()                
            for i in range(10):
                if STOP_SERVER:
                    break
                log('Sending %s'%url)
                try:
                    r = requests.get(url,headers=HEADERS_BASE, allow_redirects=True, timeout=4, verify=False)
                    code = r.status_code
                    log('Status Code: %s'%str(code))
                    if code == 200:
                        src = r.text
                        if 'http' in src:
                            url_proxy = 'http://%s:%s/?url=http'%(HOST_NAME,PORT_NUMBER)
                            src = src.replace('http',url_proxy)
                        if '/live/' in url and url.count('/') == 6:
                            CACHE_M3U8 = self.make_m3u8(src)                            
                        src = src.encode('utf-8') if six.PY3 else src
                        self.wfile.write(src)
                        break
                    else:
                        if '/live/' in url and url.count('/') == 6 and CACHE_M3U8:
                            src = CACHE_M3U8
                            src = src.encode('utf-8') if six.PY3 else src
                            self.send_response(200)
                            if 'Mozilla' in user_agent:
                                self.send_header('Content-type', 'text/html')
                            else:
                                self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
                            self.end_headers()
                            self.wfile.write(src)
                            break
                except:
                    pass
                    
        elif '.ts' in url:
            if url.startswith('/') and not '/hl' in url:
                url = url[1:]
                ts = URL_BASE + url
            elif url.startswith('/'):
                url = url[1:]
                if 'https' in URL_BASE:
                    ts = 'https://' + URL_BASE.split('/')[2] + '/' + url
                else:
                    ts = 'http://' + URL_BASE.split('/')[2] + '/' + url
            self.send_response(200)
            self.send_header('Content-type','video/mp2t')
            self.end_headers()
            for i in range(7):
                if STOP_SERVER:
                    break
                ts = self.magical_hls(ts)
                log('Sending %s'%ts)
                try:
                    r = requests.get(ts, headers=HEADERS_BASE, allow_redirects=True, stream=True, verify=False)
                    code = r.status_code
                    log('Status Code: %s'%str(code))
                    if code == 200:
                        CACHE_CHUNKS = []
                        for chunk in r.iter_content(30000):                      
                            try:
                                self.wfile.write(chunk)
                                CACHE_CHUNKS.append(chunk)
                            except:
                                pass
                        break
                    else:
                        if i == 0:
                            DELAY_MODE = False
                        if CACHE_CHUNKS:
                            try:
                                self.wfile.write(CACHE_CHUNKS[-1])
                            except:
                                pass

                except:
                    pass
        elif url == '/':
            content = 'PROXY'
            content = content.encode('utf-8') if six.PY3 else content
            self.send_response(200)
            self.end_headers()
            self.wfile.write(content)
        elif url == '/stop':
            self.send_response(200)
            self.end_headers()
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
            if url.startswith('/') and not '/hl' in url:
                url = url[1:]
                ts = URL_BASE + url
            elif url.startswith('/'):
                url = url[1:]
                if 'https' in URL_BASE:
                    ts = 'https://' + URL_BASE.split('/')[2] + '/' + url
                else:
                    ts = 'http://' + URL_BASE.split('/')[2] + '/' + url
            self.send_response(200)
            self.send_header('Content-type','video/mp2t')
            self.end_headers()            
            for i in range(4):
                if STOP_SERVER:
                    break
                ts = self.magical_hls(ts)
                try:
                    r = requests.get(ts, headers=HEADERS_BASE, allow_redirects=True, stream=True, verify=False)
                    if r.status_code == 200:
                        CACHE_CHUNKS = []
                        for chunk in r.iter_content(30000):                      
                            try:
                                self.wfile.write(chunk)
                                CACHE_CHUNKS.append(chunk)
                            except:
                                pass
                        break
                    else:
                        if i == 0:
                            DELAY_MODE = False                        
                        if CACHE_CHUNKS:
                            try:
                                self.wfile.write(CACHE_CHUNKS[-1])
                            except:
                                pass                            

                except:
                    pass
        
    def do_HEAD(self):
        global STOP_SERVER
        self.send_response(200)
        self.end_headers()
        if self.path == '/stop':
            STOP_SERVER = True
            def shutdown(server):
                server.shutdown()
                try:
                    server.server_close()
                except:
                    pass
            t = threading.Thread(target=shutdown, args=(self.server, ))
            t.start()              


    def do_GET(self):
        global URL_BASE
        global LAST_URL
        global HEADERS_BASE
        global STOP_SERVER
        global CACHE_CHUNKS
        global CACHE_M3U8
        global DELAY_MODE
        if self.path == '/check':
            self.send_response(200)
            self.end_headers()
        elif self.path == '/reset':
            URL_BASE = ''
            LAST_URL = ''
            HEADERS_BASE = {}
            CACHE_CHUNKS = []
            CACHE_M3U8 = ''
            DELAY_MODE = True
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
                url = self.convert_to_m3u8(url)
            else:
                url = url_path
            log('acesssando url: %s'%url)
            self.parse_stream(url)

def monitor():
    try:
        try:
            from kodi_six import xbmc
        except:
            import xbmc
        monitor = xbmc.Monitor()
        while not monitor.waitForAbort(3):
            pass
        url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/stop'
        try:
            r = requests.head(url,timeout=3)
        except:
            pass
    except:
        pass 

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
    
    def reset(self):
        url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/reset'
        try:
            r = requests.get(url,timeout=3)
        except:
            pass
        

    def start(self):
        if not self.in_use():
            if self.server_thread:
                self.server.start()
                t = threading.Thread(target=monitor)
                t.start()
        else:
            self.reset()
        time.sleep(3)               

    def stop(self):
        url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/stop'
        try:
            r = requests.head(url,timeout=3)
        except:
            pass 
