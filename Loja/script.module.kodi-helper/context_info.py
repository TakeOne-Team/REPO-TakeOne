# -*- coding: utf-8 -*-
from kodi_six import xbmc, xbmcaddon, xbmcgui
import requests
import six
import sys
if six.PY3:
    from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus
else:
    from urlparse import urlparse, parse_qs
    from urllib import quote, unquote, unquote_plus
from datetime import datetime,timedelta
import re
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log(msg):
    logger.info(msg)

def infoDialog(message, iconimage='', time=3000, sound=False):
    heading = 'KODI HELPER'
    if iconimage == 'INFO':
        iconimage = xbmcgui.NOTIFICATION_INFO
    elif iconimage == 'WARNING':
        iconimage = xbmcgui.NOTIFICATION_WARNING
    elif iconimage == 'ERROR':
        iconimage = xbmcgui.NOTIFICATION_ERROR
    xbmcgui.Dialog().notification(heading, message, iconimage, time, sound=sound)

def check_iptv(url):
    try:
        url = url.split('|')[0]
    except:
        pass
    try:
        url = url.split('%7C')[0]
    except:
        pass
    if url.count('/') == 5:
        return True
    if url.count('/') == 6:
        return True
    else:
        return False
    
def extract_info_dialog(url):
    infoDialog('WAIT INFO...', iconimage='INFO')
    try:
        url = url.split('|')[0]
    except:
        pass
    try:
        url = url.split('%7C')[0]
    except:
        pass    
    if url.count('/') == 5:
        parsed_url = urlparse(url)
        host = parsed_url.scheme + "://" + parsed_url.netloc
        user, password = parsed_url.path.strip("/").split("/")[:-1]
    elif url.count('/') == 6:
        parsed_url = urlparse(url)
        host = parsed_url.scheme + "://" + parsed_url.netloc
        user, password = parsed_url.path.lstrip("/").split("/")[1:-1]
    else:
        host = ''
        user = ''
        password = ''
    if host and user and password:
        fullinfo = False
        api = '{0}/panel_api.php?username={1}&password={2}'.format(host,user,password)
        try:
            info = requests.get(api,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41'}).json()
        except:
            info = {}
        if info !={}:
            expiry = info['user_info']['exp_date']
            if not expiry=="" and not expiry==None:
                expiry	   = datetime.fromtimestamp(int(expiry)).strftime('%d/%m/%Y - %H:%M')
                expreg	   = re.compile('^(.*?)/(.*?)/(.*?)$',re.DOTALL).findall(expiry)
                for day,month,year in expreg:
                    # month	  = tools.MonthNumToName(month)
                    # year	  = re.sub(' -.*?$','',year)
                    # #expiry	  = month+' '+day+' - '+year
                    # expiry	  = day+' de '+month+' de '+year
                    year = re.sub(' -.*?$','',year)
                    expiry_br = '{0}/{1}/{2} BR'.format(day,month,year)
                    expiry_us = '{0}/{1}/{2} US'.format(month,day,year)
                    expiry = '{0} | {1}'.format(expiry_br,expiry_us)
            else:
                expiry = 'Unlimited'
            max_connection = str(info['user_info']['max_connections'])
            if max_connection == 'None':
                max_connection = 'Unlimited'
            connection_use = str(info['user_info']['active_cons'])
            status = info['user_info']['status']
            if fullinfo:
                host_info = host
                user_info = str(info['user_info']['username'])
                user_password = str(info['user_info']['password'])
            else:
                try:
                    if 'https' in host:
                        host_info = host.split('https://')[1]
                        host_info = str(len(host_info) * '*')
                        host_info = 'https://' + host_info
                    else:
                        host_info = host.split('http://')[1]
                        host_info = str(len(host_info) * '*')
                        host_info = 'http://' + host_info
                except:
                    host_info = '***'
                try:
                    user_info = str(len(info['user_info']['username']) * '*')
                except:
                    user_info = '***'
                try:
                    user_password = str(len(info['user_info']['password']) * '*')
                except:
                    user_password = '***'
            text_info = 'Host: {0}\nUsername: {1}\nPassword: {2}\nExpire: {3}\nStatus: {4}\nConnections in use: {5}\nAllowed connections: {6}'.format(host_info,user_info,user_password,expiry,status,connection_use,max_connection)
            dialog = xbmcgui.Dialog()
            dialog.textviewer('Account Info', text_info)
        else:
            infoDialog('IPTV OFFILINE', iconimage='INFO')         

    else:
        infoDialog('INVALID IPTV', iconimage='INFO')

try:
    path = sys.listitem.getfilename()
except AttributeError:
    path = sys.listitem.getPath()

if path:
    if 'url=' in path:
        url = path.split('url=')[1]
        try:
            url = url.split('&')[0]
        except:
            pass
        url_base = unquote_plus(url)
        if 'url=' in url_base:         
            url = url_base.split('url=')[1]
            try:
                url = url.split('&')[0]
            except:
                pass          
        else:
            url = url_base
    else:
        url_base = unquote_plus(path)
        url = url_base
    if 'plugin' in url:
        url = unquote_plus(url)
        if 'url=' in url:
            url = url.split('url=')[1]
            try:
                url = url.split('&')[0]
            except:
                pass
    url = unquote_plus(url)              
    if check_iptv(url):
        extract_info_dialog(url)
    else:
        infoDialog('INVALID IPTV', iconimage='INFO') 
