# -*- coding: utf-8 -*-
from kodi_six import xbmc as xbmc_, xbmcgui as xbmcgui_, xbmcplugin as xbmcplugin_, xbmcaddon as xbmcaddon_, xbmcvfs as xbmcvfs_
import six as six_
if six_.PY3:
    from urllib.parse import urlparse as urlparse_, parse_qs as parse_qs_, parse_qsl as parse_qsl_, quote as quote_, unquote as unquote_, quote_plus as quote_plus_, unquote_plus as unquote_plus_, urlencode as urlencode_ #python 3
else:
    from urlparse import urlparse as urlparse_, parse_qs as parse_qs_, parse_qsl as parse_qsl_ #python 2
    from urllib import quote as quote_, unquote as unquote_, quote_plus as quote_plus_, unquote_plus as unquote_plus_, urlencode as urlencode_
import sys
import os
import requests as rq
try:
    import json as json_
except ImportError:
    import simplejson as json_
from bs4 import BeautifulSoup as bfs

six = six_
requests = rq
json = json_
BeautifulSoup = bfs
xbmc = xbmc_
xbmcgui = xbmcgui_
xbmcplugin = xbmcplugin_
xbmcaddon = xbmcaddon_
xbmcvfs = xbmcvfs_
urlparse = urlparse_
parse_qs = parse_qs_
parse_qsl = parse_qsl_
quote = quote_
unquote = unquote_
quote_plus = quote_plus_
unquote_plus = unquote_plus_
urlencode = urlencode_


qp = quote_plus
uqp = unquote_plus

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

class Progress_six:
    dp = xbmcgui.DialogProgress()
    @classmethod
    def create(cls,heading,msg):
        if six.PY3:
            cls.dp.create(str(heading),str(msg))
        else:
            cls.dp.create(str(heading),str(msg), '','')
    @classmethod
    def update(cls,update,heading):
        if six.PY3:
            cls.dp.update(int(update), str(heading))
        else:
            cls.dp.update(int(update), str(heading),'', '')

class ProgressBG_six:
    dp = xbmcgui.DialogProgressBG()
    @classmethod
    def create(cls,heading,msg):
        if six.PY3:
            cls.dp.create(str(heading),str(msg))
        else:
            cls.dp.create(str(heading),str(msg), '','')
    @classmethod
    def update(cls,update,heading):
        if six.PY3:
            cls.dp.update(int(update), str(heading))
        else:
            cls.dp.update(int(update), str(heading),'', '')



class myAddon(object):
    def __init__(self, id):
        self.script = xbmcaddon.Addon('script.module.kodi-helper')
        self.addon = xbmcaddon.Addon(id)
        self.addonName = self.addon.getAddonInfo('name')
        self.addonVersion = self.addon.getAddonInfo('version')
        self.localLang = self.addon.getLocalizedString
        self.homeDir = self.addon.getAddonInfo('path')
        self.translate = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
        self.addonIcon = self.translate(os.path.join(self.homeDir, 'icon.png'))
        self.addonFanart = self.translate(os.path.join(self.homeDir, 'fanart.jpg'))
        self.profile = self.translate(self.addon.getAddonInfo('profile'))
        self.kversion = int(xbmc.getInfoLabel('System.BuildVersion').split(".")[0])
        self.plugin = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.dialog_ = xbmcgui.Dialog()
        self.executebuiltin = xbmc.executebuiltin

    def opensettings(self):
        self.addon.openSettings()

    def getsetting(self,text):
        return self.addon.getSetting(text)
    
    def setsetting(self,key,value):
        return self.addon.setSetting(key, value)

    def exists(self,path):
        return xbmcvfs.exists(path)
    
    def mkdir(self,path):
        try:
            xbmcvfs.mkdir(path)
        except:
            pass

    def dialog(self,msg):
        dialog = xbmcgui.Dialog()
        dialog.ok(self.addonName, msg)

    def progress(self):
        dp = xbmcgui.DialogProgress()
        return dp
    
    def progress_six(self):
        dp = Progress_six()
        return dp    

    def progressBG(self):
        pDialog = xbmcgui.DialogProgressBG()
        return pDialog
    
    def progressBG_six(self):
        pDialog = ProgressBG_six()
        return pDialog     

    def select(self,name,items):
        op = self.dialog_.select(name, items)
        return op              

    def log(self, txt):
            message = ''.join([self.addonName, ' : ', txt])
            xbmc.log(msg=message, level=xbmc.LOGDEBUG)

    def string_utf8(self,string):
        if isinstance(string, bytes):
            return string

        return string.encode("utf-8", errors="ignore")

    def to_unicode(self,text, encoding='utf-8', errors='strict'):
        """Force text to unicode"""
        if isinstance(text, bytes):
            return text.decode(encoding, errors=errors)
        return text

    def get_search_string(self,heading='', message=''):
        """Ask the user for a search string"""
        search_string = None
        keyboard = xbmc.Keyboard(message, heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_string = self.to_unicode(keyboard.getText())
        return search_string 

    def input_text(self,heading='Put text'):
        vq = self.get_search_string(heading=heading, message="")        
        if ( not vq ): return False
        title = quote_plus(vq)
        return title 

    def infoDialog(self,message, iconimage='', time=3000, sound=False):
        heading = self.addonName
        if iconimage == '':
            iconimage = self.addonIcon
        elif iconimage == 'INFO':
            iconimage = xbmcgui.NOTIFICATION_INFO
        elif iconimage == 'WARNING':
            iconimage = xbmcgui.NOTIFICATION_WARNING
        elif iconimage == 'ERROR':
            iconimage = xbmcgui.NOTIFICATION_ERROR
        self.dialog_.notification(heading, message, iconimage, time, sound=sound)

    def notify(self,msg):
        self.infoDialog(msg,iconimage='INFO')                                  

    def addMenuItem(self, params={}, folder=True):
        name = params.get('name', '')
        description = params.get("description", "")
        originaltitle = params.get("originaltitle", "")        
        try:
            params.update({'name': self.string_utf8(name)})
        except:
            pass
        try:
            params.update({'description': self.string_utf8(description)})
        except:
            pass
        try:
            params.update({'originaltitle': self.string_utf8(originaltitle)})
        except:
            pass               
        u = '%s?%s'%(self.plugin, urlencode(params))
        iconimage = params.get("iconimage", "")
        fanart = params.get("fanart", "")
        codec = params.get("codec", "")
        playable = params.get("playable", "")
        duration = params.get("duration", "")
        imdbnumber = params.get("imdbnumber", "")
        if not imdbnumber:
            imdbnumber = params.get("imdb", "")
        aired = params.get("aired", "")
        genre = params.get("genre", "")
        season = params.get("season", "")
        episode = params.get("episode", "")
        year = params.get("year", "")
        mediatype = params.get("mediatype", "video")
        li=xbmcgui.ListItem(name)
        iconimage = iconimage if iconimage else ''
        li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
        if self.kversion > 19:
            info = li.getVideoInfoTag()
            info.setTitle(name)
            info.setPlot(description)
            infotag = True
        else:
            li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
            infotag = False
        if year:
            if infotag:
                info.setYear(int(year))
            else:
                li.setInfo('video', {'year': int(year)})
        if codec:
            if infotag:
                info.addVideoStream(xbmc.VideoStreamDetail(codec='h264'))
            else:
                li.addStreamInfo('video', {'codec': codec})
        if duration:
            if infotag:
                info.setDuration(int(duration))
            else:
                li.setInfo('video', {'duration': int(duration)})
        if originaltitle:
            if infotag:
                info.setOriginalTitle(str(originaltitle))
            else:
                li.setInfo('video', {'originaltitle': str(originaltitle) })
        if imdbnumber:
            if infotag:
                info.setIMDBNumber(str(imdbnumber))
            else:
                li.setInfo('video', {'imdbnumber': str(imdbnumber)})
        if aired:
            if infotag:
                info.setFirstAired(str(aired))
            else:
                li.setInfo('video', {'aired': str(aired)})
        if genre:
            if infotag:
                info.setGenres([str(genre)])
            else:
                li.setInfo('video', {'genre': str(genre)})
        if season:
            if infotag:
                info.setSeason(int(season))
            else:
                li.setInfo('video', {'season': int(season)})
        if episode:
            if infotag:
                info.setEpisode(int(episode))
            else:
                li.setInfo('video', {'episode': int(episode)})
        if mediatype:
            if infotag:
                info.setMediaType(str(mediatype))
            else:
                li.setInfo('video', {'mediatype': str(mediatype)})       
        if playable and folder == False and not playable == 'false':
            li.setProperty('IsPlayable', 'true')        
        if fanart:
            li.setProperty('fanart_image', fanart)
        else:
            li.setProperty('fanart_image', self.addonFanart)
        xbmcplugin.addDirectoryItem(handle=self.handle, url=u, listitem=li, isFolder=folder)

    def play_video(self,params):
        name = params.get('name', '')
        url = params.get('url', '')
        sub = params.get('sub', '')
        description = params.get("description", "")
        originaltitle = params.get("originaltitle", "") 
        iconimage = params.get("iconimage", "")
        fanart = params.get("fanart", "")
        codec = params.get("codec", "")
        playable = params.get("playable", "")
        duration = params.get("duration", "")
        imdbnumber = params.get("imdbnumber", "")
        if not imdbnumber:
            imdbnumber = params.get("imdb", "")
        aired = params.get("aired", "")
        genre = params.get("genre", "")
        season = params.get("season", "")
        episode = params.get("episode", "")
        year = params.get("year", "")
        mediatype = params.get("mediatype", "video")
        li=xbmcgui.ListItem(name)
        iconimage = iconimage if iconimage else ''
        li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
        if self.kversion > 19:
            info = li.getVideoInfoTag()
            info.setTitle(name)
            info.setPlot(description)
            infotag = True
        else:
            li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
            infotag = False
        if year:
            if infotag:
                info.setYear(int(year))
            else:
                li.setInfo('video', {'year': int(year)})
        if codec:
            if infotag:
                info.addVideoStream(xbmc.VideoStreamDetail(codec='h264'))
            else:
                li.addStreamInfo('video', {'codec': codec})
        if duration:
            if infotag:
                info.setDuration(int(duration))
            else:
                li.setInfo('video', {'duration': int(duration)})
        if originaltitle:
            if infotag:
                info.setOriginalTitle(str(originaltitle))
            else:
                li.setInfo('video', {'originaltitle': str(originaltitle) })
        if imdbnumber:
            if infotag:
                info.setIMDBNumber(str(imdbnumber))
            else:
                li.setInfo('video', {'imdbnumber': str(imdbnumber)})
        if aired:
            if infotag:
                info.setFirstAired(str(aired))
            else:
                li.setInfo('video', {'aired': str(aired)})
        if genre:
            if infotag:
                info.setGenres([str(genre)])
            else:
                li.setInfo('video', {'genre': str(genre)})
        if season:
            if infotag:
                info.setSeason(int(season))
            else:
                li.setInfo('video', {'season': int(season)})
        if episode:
            if infotag:
                info.setEpisode(int(episode))
            else:
                li.setInfo('video', {'episode': int(episode)})
        if mediatype:
            if infotag:
                info.setMediaType(str(mediatype))
            else:
                li.setInfo('video', {'mediatype': str(mediatype)})
        if fanart:
            li.setProperty('fanart_image', fanart)
        else:
            li.setProperty('fanart_image', self.addonFanart)                
        li.setPath(url)
        if sub:
            li.setSubtitles([sub])               
        if playable and not playable == 'false':
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
        else:
            xbmc.Player().play(item=url, listitem=li)

    def setcontent(self,name):
        xbmcplugin.setContent(self.handle, name)    

    def end(self):
        xbmcplugin.endOfDirectory(self.handle)

    def setview(self,name):
        mode = {'Wall': '500',
                'List': '50',
                'Poster': '51',
                'Shift': '53',
                'InfoWall': '54',
                'WideList': '55',
                'Fanart': '502'
                }.get(name, '50')
        view = 'Container.SetViewMode(%s)'%mode
        xbmc.executebuiltin(view)

