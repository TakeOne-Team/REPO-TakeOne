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
from proxy import url_proxy, Server


def infoDialog(message, iconimage='', time=3000, sound=False):
    heading = 'KODI HELPER'
    if iconimage == 'INFO':
        iconimage = xbmcgui.NOTIFICATION_INFO
    elif iconimage == 'WARNING':
        iconimage = xbmcgui.NOTIFICATION_WARNING
    elif iconimage == 'ERROR':
        iconimage = xbmcgui.NOTIFICATION_ERROR
    xbmcgui.Dialog().notification(heading, message, iconimage, time, sound=sound)

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

def check_iptv(url):
    try:
        url = url.split('|')[0]
    except:
        pass
    try:
        url = url.split('%7C')[0]
    except:
        pass     
    if '.m3u8' in url:
        return True
    elif url.count('/') == 5 or url.count('/') == 6:
        return True
    else:
        return False
    
def check_online(url):
    headers_default = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41'}
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
    if headers != {}:
        headers_base = headers
    else:
        headers_base = headers_default
    try:
        url = url.split('|')[0]
    except:
        pass
    try:
        url = url.split('%7C')[0]
    except:
        pass    
    try:
        r = requests.head(url,headers=headers_base)
        if r.status_code == 200:
            return True
    except:
        pass
    return False

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
    if not iconimage:
        if 'iconimage=' in path:
            iconimage = path.split('iconimage=')[1]
            try:
                iconimage = iconimage.split('&')[0]
            except:
                pass
        elif 'thumbnail=' in path:
            iconimage = path.split('thumbnail=')[1]
            try:
                iconimage = iconimage.split('&')[0]
            except:
                pass
        else:
            iconimage = ''
        if iconimage:
            iconimage = unquote_plus(iconimage)
    if not name:
        if 'name=' in path:
            name = path.split('name=')[1]
            try:
                name = name.split('&')[0]
            except:
                pass
        elif 'name=' in url_base:
            name = url_base.split('name=')[1]
            try:
                name = name.split('&')[0]
            except:
                pass
        else:
            name = ''
        if name:
            name = unquote_plus(name)
    if 'plugin' in url:
        path = unquote_plus(url)
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
        if not iconimage:
            if 'iconimage=' in path:
                iconimage = path.split('iconimage=')[1]
                try:
                    iconimage = iconimage.split('&')[0]
                except:
                    pass
            elif 'thumbnail=' in path:
                iconimage = path.split('thumbnail=')[1]
                try:
                    iconimage = iconimage.split('&')[0]
                except:
                    pass
            else:
                iconimage = ''
            if iconimage:
                iconimage = unquote_plus(iconimage)
        if not name:
            if 'name=' in path:
                name = path.split('name=')[1]
                try:
                    name = name.split('&')[0]
                except:
                    pass
            elif 'name=' in url_base:
                name = url_base.split('name=')[1]
                try:
                    name = name.split('&')[0]
                except:
                    pass
            else:
                name = ''
            if name:
                name = unquote_plus(name)       
    description = ''

    #check xtream codes
    if check_iptv(url):
        if check_online(url):
            infoDialog('Starting proxy...', iconimage='INFO')
            url = url_proxy + quote(url)
            Server().start()
            kversion = int(xbmc.getInfoLabel('System.BuildVersion').split(".")[0])
            li=xbmcgui.ListItem(name)
            li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
            if kversion > 19:
                info = li.getVideoInfoTag()
                info.setTitle(name)
                info.setPlot(description)
            else:
                li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
            try:
                li.setPath(url)
            except:
                pass
            xbmc.Player().play(item=url, listitem=li)
        else:
            infoDialog('CHANNEL OFFLINE', iconimage='INFO')
    else:
        infoDialog('INVALID IPTV, USE M3U8', iconimage='INFO') 
    






    
