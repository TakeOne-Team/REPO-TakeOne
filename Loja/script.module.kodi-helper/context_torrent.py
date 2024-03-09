# -*- coding: utf-8 -*-
from kodi_six import xbmc, xbmcaddon, xbmcgui
import six
import sys
import requests
import re
from bs4 import BeautifulSoup
import base64
if six.PY3:
    from urllib.parse import urlparse, parse_qs, quote, unquote, quote_plus, unquote_plus, urlencode #python 3
else:
    from urlparse import urlparse, parse_qs #python 2
    from urllib import quote, unquote, quote_plus, unquote_plus, urlencode
try:
    import json as json
except ImportError:
    import simplejson as json
import re



class Torrent_client:

    def __init__(self,magnet):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.hash = self.find_hash(magnet)
        self.webtor = 'https://webtor.io'
        self.files = None
        if self.hash:        
            k = self.get_info_api()
            if k:                   
                api = k['api']
                apikey = k['apikey']
                token = k['token']
                parsed_url = urlparse(api)
                host = parsed_url.netloc
                status = self.sender_torrent(self.hash,host,token,apikey)
                if status:                   
                    torrents_files = self.get_direct_link(host,api,self.hash,token,apikey)
                    if torrents_files:                     
                        self.files = torrents_files
        else:
            xbmcgui.Dialog().notification('StreamTorrent', 'invalid hash, use elementum for characters below 40', xbmcgui.NOTIFICATION_INFO, 3000, sound=False)

    def find_hash(self,magnet):
        hash_match1 = re.search(r"urn:btih:(.*?)&", magnet)
        hash_match2 = re.search(r"urn:btih:([0-9a-fA-F]+)", magnet)
        if hash_match1: 
            h = hash_match1.group(1)
            if len(h) == 40:
                return h.lower()
        if hash_match2:
            h = hash_match2.group(1)
            if len(h) == 40:
                return h.lower()       
        return None
    
    def get_info_api(self):
        try:
            r = requests.get(self.webtor + '/',headers={'User-Agent': self.user_agent})
            src = r.text
            token = re.findall(r"window.__TOKEN__ = '(.*?)';", src)[-1]
            config = re.findall(r"window.__CONFIG__ = '(.*?)';", src)[-1]
            info = json.loads(base64.b64decode(config).decode('utf-8'))
            api = info['sdk']['apiUrl']
            apikey = info['sdk']['apiKey']
            k = {}
            k['token'] = token
            k['api'] = api
            k['apikey'] = apikey
            return k
        except:
            return {}
        
    def sender_torrent(self,hash,host,token,apikey):
        url_pull = 'https://{0}/store/TorrentStore/Pull'.format(host)
        url_touch = 'https://{0}/store/TorrentStore/Touch'.format(host)
        headers = {
            "User-Agent": self.user_agent,
            "api-key": apikey,
            "Content-Type": "application/grpc-web+proto",
            "token": token
        }
        raw_data = hash.encode()
        response = requests.post(url_pull, data=raw_data, headers=headers,timeout=5)
        if response.status_code == 200:
            response = requests.post(url_touch, data=raw_data, headers=headers,timeout=5)
            if response.status_code == 200:
                return True
        return False
    
    def get_direct_link(self,host,api,hash,token,apikey):
        list_torrents = []
        try:
            r = requests.get('{0}/subdomains.json?infohash={1}&use-bandwidth=false&use-cpu=true&skip-active-job-search=false&pool=seeder&token={2}&api-key={3}'.format(api,hash.lower(),token,apikey), headers={'User-Agent': self.user_agent})
            src = r.json()
            for subdomain in src:
                embed = 'https://{0}.{1}/{2}/?token={3}&api-key={4}'.format(subdomain,host,hash.lower(),token,apikey)
                try:
                    r2 = requests.get(embed,headers={'User-Agent': self.user_agent})
                    if r2.status_code == 200:
                        src2 = r2.text
                        soup = BeautifulSoup(src2, 'html.parser')
                        a_links = soup.find_all('a')
                        if a_links:
                            for i in a_links:
                                href = i.get('href', '')
                                if any(ext in href.lower() for ext in ['.mp4', '.mkv', '.avi']):
                                    try:
                                        name = href.split('?')[0]
                                    except:
                                        pass
                                    try:
                                        name = unquote_plus(name)
                                    except:
                                        pass
                                    name = name.split('/')[-1]
                                    stream = 'https://{0}.{1}/{2}/{3}'.format(subdomain,host,hash.lower(),href)
                                    if not '1xbet' in name.lower():
                                        list_torrents.append((name,stream))
                        break
                                    
                except:
                    pass
            if list_torrents:
                return list_torrents
            return None        
        except:
            return None     
        
    def check_stream(self,stream):
        try:
            r = requests.head(stream)
            if r.status_code == 200:
                return stream
            return None
        except:
            return None


ADDON = xbmcaddon.Addon()

def select(name,items):
    op = xbmcgui.Dialog().select(name, items)
    return op

def progressBG():
    pDialog = xbmcgui.DialogProgressBG()
    return pDialog 

try:
    path = sys.listitem.getfilename()
except AttributeError:
    path = sys.listitem.getPath()
try:
    name = xbmc.getInfoLabel('ListItem.Label')
except:
    name = ''
try:
    iconimage = xbmc.getInfoLabel('ListItem.Thumb')
except:
    try:
        iconimage = xbmc.getInfoLabel('ListItem.Icon')
    except:
        iconimage = ''


url = unquote_plus(path)
if 'playlist' in url:
    new_itens = []
    itens = url.split("['")[1]
    itens = itens.split("']")[0]
    itens = itens.replace('+', ' ')
    itens = itens.split('||')
    for i in itens:
        i = i.replace("'", '').replace('"', '')
        url = i.split('$')[0]
        tag = '$' + re.findall(r'\$(.*?)=', i)[0] + '='
        name = i.split(tag)[1]
        if 'magnet' in url:
            url = 'magnet' + url.split('magnet')[1]
            new_itens.append((name,url)) 
    if new_itens:
        items_options = [name for name,stream_link in new_itens]
        try:
            op = select(name='SELECT A OPTION:',items=items_options)
        except:
            op = -1
        if op >= 0:
            stream = new_itens[op][1]
elif 'magnet' in url:
    stream = 'magnet' + url.split('magnet')[1]
else:
    stream = ''
if stream:    
    try:
        bg = progressBG()
        bg.create('StreamTorrent', 'Loading torrent... .')
    except:
        pass
    client = Torrent_client(stream)
    files_list = client.files
    if files_list:
        items_options = [name for name,stream_link in files_list]
        try:
            op = select(name='SELECT A TORRENT:',items=items_options)
        except:
            op = -1
        if op >= 0:
            stream_link = files_list[op][1]
            try:
                bg.update(1, message='Preparing reproduction ...')
            except:
                pass
            li=xbmcgui.ListItem(name)
            li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
            li.setPath(stream_link)
            xbmc.Player().play(item=stream_link, listitem=li)     
    

