# -*- coding: utf-8 -*-
from kodi_helper import myAddon, xbmc, xbmcgui, xbmcaddon, xbmcplugin, requests, json, six
from resources.lib import hlsretry, tsdownloader
import os
import sys
import re
import time
import threading
if six.PY3:
    from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus
else:
    from urlparse import urlparse, parse_qs
    from urllib import quote, unquote, unquote_plus  

class MyPlayer(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)

    def play(self, url, listitem):
        #print 'Now im playing... %s' % url
        xbmc.Player().play(url, listitem)
        
    # def onPlayBackEnded( self ):
    #     # Will be called when xbmc stops playing a file
    #     #print "seting event in onPlayBackEnded " 
    #     self.stopPlaying.set();
    #     #print "stop Event is SET" 
    # def onPlayBackStopped( self ):
    #     # Will be called when user stops xbmc playing a file
    #     #print "seting event in onPlayBackStopped " 
    #     self.stopPlaying.set();
    #     #print "stop Event is SET"

class MyPlayer2(xbmc.Player):

    def __init__ (self):
        xbmc.Player.__init__(self)

    def play(self, url, li):
        #print 'Now im playing... %s' % url
        # self.stopPlaying.clear()
        # runningthread=thread.start_new_thread(xbmc.Player().play(item=url, listitem=li),(parar,))
        progress = xbmcgui.DialogProgress()
        # import checkbad
        # checkbad.do_block_check(False)

        #progress.create('Conectando...')
        progress.create('Estabilizador','Conectando...')
        # stream_delay = 1
        #progress.update( 20, "", 'Aguarde...', "" )
        # xbmc.sleep(stream_delay*100)
        #progress.update( 100, "", 'Carregando transmissão...', "" )
        prog=0
        xbmc.sleep(2000)

        xbmc.Player().play(item=url, listitem=li)
        count = 0
        while not xbmc.Player().isPlaying() and not xbmc.Monitor().abortRequested():
            xbmc.sleep(200)
            progress.update(prog+10,'Carregando transmissão...')
            prog=prog+10
            count +=10
            if count == 50 and xbmc.Player().isPlaying():
                break


        progress.close()


    def onPlayBackEnded( self ):
        # Will be called when xbmc stops playing a file
        print("seting event in onPlayBackEnded " )
        threading.Event()

        # self.stopPlaying.set()
        # thread.exit()
        # iniciavideo().stop()

        #print "stop Event is SET" 
    def onPlayBackStopped( self ):
        # Will be called when user stops xbmc playing a file
        print("seting event in onPlayBackStopped ") 
        threading.Event()
        # self.stopPlaying.set()
        # thread.exit()
        # iniciavideo().stop()

        #print "stop Event is SET"
        # 

class iniciavideo():
    
    def tocar(url, li):

        
        # parar=threading.Event()
        # parar.clear()   
        mplayer = MyPlayer2()    
        # iniciavideo().stop()
        # mplayer.stopPlaying = parar

        mplayer.play(url,li)


        # thread.start_new_thread(mplayer.play,(url,li))
        
        # mplayer.play(url,listitem)

        firstTime=True
        played=False

        
        while True:
            # if parar.isSet():            
                # break
            if xbmc.Player().isPlaying():
                played=True
            xbmc.log('Sleeping...')
            xbmc.sleep(1000)
            if firstTime:
                xbmc.executebuiltin('Dialog.Close(all,True)')
                firstTime=False
                # parar.isSet()
                # thread.exit()
                # iniciavideo().stop()


                    #print 'Job done'
        # return played
    
    def stop(self):
        threading.Event()                 
        
def monitor_hlsretry():
    try:
        from kodi_helper import xbmc
        while True:
            xbmc.sleep(1000)
            if not xbmc.Player().isPlaying():
                try:
                    r = requests.head(hlsretry.url_stop,timeout=2)
                    r.close()
                except:
                    pass
                break
    except:
        pass

def monitor_tsdownloader():
    try:
        from kodi_helper import xbmc
        while True:
            xbmc.sleep(1000)
            if not xbmc.Player().isPlaying():
                try:
                    r = requests.head(tsdownloader.url_stop,timeout=2)
                    r.close()
                except:
                    pass
                break
    except:
        pass    


class f4mtester(myAddon):
    def home(self):
        if not self.exists(self.profile):
            self.mkdir(self.profile)
        self.setcontent('videos')
        self.addMenuItem({'name':'[B]Configurar PVR[/B]','action': 'pvr_settings', 'mediatype': 'video', 'iconimage': self.addonIcon})
        self.addMenuItem({'name':'[B]Ajustes[/B]','action': 'settings', 'mediatype': 'video', 'iconimage': self.addonIcon})
        self.end()

    def local_playlist(self):
        return self.translate(os.path.join(self.profile, 'playlist.m3u'))

    def open_settings(self):
        self.opensettings()

    def inverter(self):
        cond_ = False  # Assign a default value before comparison
        cond = str(self.getsetting('changeproxy'))
        if cond == 'true':
            cond_ = True
        return cond_
    
    def input_text(self):
        vq = self.get_search_string(heading='Digite a url', message="")
        if ( not vq ): return False
        return vq

    def json_rpc(self,method,params=None):
        request_data = {'jsonrpc': '2.0', 'method': method, 'id': 1,
                    'params': params or {}}
        request = json.dumps(request_data)
        raw_response = xbmc.executeJSONRPC(request)
        response = json.loads(raw_response)
        return response
    
    def setup_pvr(self,remove=False):
        if remove:
            localpath = ''
        else:
            localpath = self.local_playlist()
        IPTV_SIMPLE_ADDON_ID = "pvr.iptvsimple"
        try:
            IPTV_SIMPLE = xbmcaddon.Addon(id=IPTV_SIMPLE_ADDON_ID)
        except:
            xbmc.executebuiltin('InstallAddon({})'.format(IPTV_SIMPLE_ADDON_ID), True)

            try:
                IPTV_SIMPLE = xbmcaddon.Addon(id=IPTV_SIMPLE_ADDON_ID)
            except:
                pass
        if IPTV_SIMPLE.getSettingInt("epgPathType") != 0:
            IPTV_SIMPLE.setSettingInt("epgPathType", 0)
        if IPTV_SIMPLE.getSettingBool("m3uCache") != True:
            IPTV_SIMPLE.setSettingBool("m3uCache", True)
        if IPTV_SIMPLE.getSettingInt("m3uPathType") != 0:
            IPTV_SIMPLE.setSettingInt("m3uPathType", 0)            
        if IPTV_SIMPLE.getSetting("m3uPath") != localpath:
            IPTV_SIMPLE.setSetting("m3uPath", localpath)
        if IPTV_SIMPLE.getSettingInt("startNum") != 1:
            IPTV_SIMPLE.setSettingInt("startNum", 1)
        if IPTV_SIMPLE.getSettingBool("numberByOrder") != False:
            IPTV_SIMPLE.setSettingBool("numberByOrder", False)
        if IPTV_SIMPLE.getSettingInt("m3uRefreshMode") != 1:
            IPTV_SIMPLE.setSettingInt("m3uRefreshMode", 1)
        if IPTV_SIMPLE.getSettingInt("m3uRefreshIntervalMins") != 120:
            IPTV_SIMPLE.setSettingInt("m3uRefreshIntervalMins", 120) 
        if IPTV_SIMPLE.getSettingInt("m3uRefreshHour") != 4:
            IPTV_SIMPLE.setSettingInt("m3uRefreshHour", 4)

        method = 'Addons.SetAddonEnabled'
        self.json_rpc(method, {"addonid": "pvr.iptvsimple", "enabled": "false"})
        xbmc.sleep(2000)
        self.json_rpc(method, {"addonid": "pvr.iptvsimple", "enabled": "true"})         
    
    def pvr_settings(self):
        self.setcontent('videos')
        self.addMenuItem({'name':'[B]Ativar PVR[/B]','action': 'pvr_active', 'mediatype': 'video', 'iconimage': self.addonIcon})
        self.addMenuItem({'name':'[B]Remover Lista do PVR[/B]','action': 'pvr_remove', 'mediatype': 'video', 'iconimage': self.addonIcon})
        self.end()
    
    def pvr_active(self):
        if 'http' in self.getsetting('pvr_url'):
            url = self.getsetting('pvr_url')
            dp = self.progress_six()
            dp.create('F4mtester', 'Baixando lista, aguarde...')
            dp.update(0, '')
            if six.PY2:
                with open(self.local_playlist(), 'w') as f:
                    with requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}, allow_redirects=True, stream=True) as response:
                        if response.status_code == 200:
                            for linha in response.iter_lines():
                                linha = linha.decode('utf-8')
                                linha = linha.strip()
                                if linha.startswith('http') and '.m3u8' in linha:
                                    linha = 'plugin://plugin.video.f4mTester/?streamtype=HLSRETRY&name=F4MTESTER&url=' + linha
                                elif linha.startswith('http') and not '.m3u8' in linha and not '.mp4' in linha and not '.avi' in linha:
                                    linha = 'plugin://plugin.video.f4mTester/?streamtype=TSDOWNLOADER&name=F4MTESTER&url=' + linha
                                f.write(linha + '\n')
            else:
                with open(self.local_playlist(), 'w', encoding='utf-8') as f:
                    with requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}, allow_redirects=True, stream=True) as response:
                        if response.status_code == 200:
                            for linha in response.iter_lines():
                                linha = linha.decode('utf-8')
                                linha = linha.strip()
                                if linha.startswith('http') and '.m3u8' in linha:
                                    linha = 'plugin://plugin.video.f4mTester/?streamtype=HLSRETRY&name=F4MTESTER&url=' + linha
                                elif linha.startswith('http') and not '.m3u8' in linha and not '.mp4' in linha and not '.avi' in linha:
                                    linha = 'plugin://plugin.video.f4mTester/?streamtype=TSDOWNLOADER&name=F4MTESTER&url=' + linha
                                f.write(linha + '\n')
            dp.update(100, 'Concluido')
            self.setup_pvr()
        else:
            self.dialog('Adicione uma lista nos ajustes do f4mtester')

    def pvr_remove(self):
        try:
            os.remove(self.local_playlist())
        except:
            pass
        self.setup_pvr(remove=True)
        self.dialog('Lista removida com sucesso')

    def check_iptv(self,url):
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
        
    def basename(self,p):
        """Returns the final component of a pathname"""
        i = p.rfind('/') + 1
        return p[i:]        

    def converter_m3u8_tester(self,url):
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
                    url = url + '.m3u8'
                    # file_new = file + '.m3u8'
                    # new_url = url.replace(file, file_new)
            except:
                pass
        return url
    
    def ts_to_m3u8(self,url):
        try:
            url = unquote_plus(url)
        except:
            pass
        try:
            url = unquote(url)
        except:
            pass        
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
                    url = url + '.m3u8'
                    # file_new = file + '.m3u8'
                    # new_url = url.replace(file, file_new)
            except:
                pass
        return url 

    def play_video_thread(self,url,iconimage):
        try:
            name = xbmc.getInfoLabel('ListItem.Label')
        except:
            name = ''
        if not iconimage:
            try:
                iconimage = xbmc.getInfoLabel('ListItem.Thumb')
            except:
                try:
                    iconimage = xbmc.getInfoLabel('ListItem.Icon')
                except:
                    iconimage = ''            
        if not name:        
            name = 'F4M (HLSRETRY)'
        else:
            try:
                name = name + ' - ' + 'F4M (HLSRETRY)'
            except:
                pass
        li=xbmcgui.ListItem(name)
        li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
        li.setProperty("IsPlayable", "true")
        li.setPath(url)
        li.setMimeType('application/x-mpegURL')
        if self.kversion > 19:
            info = li.getVideoInfoTag()
            info.setTitle(name)
            try:
                li.addStreamInfo('video', { 'codec': 'h264' })
            except:
                pass
        else:
            li.setInfo(type="Video", infoLabels={"Title": name, "Plot": ""})
            li.setInfo('video', { 'codec': 'h264'})            
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
        #xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
        mplayer = MyPlayer()
        mplayer.play(url,li)         

    def inputstream_player(self,url,iconImage):
        try:
            url = unquote_plus(url)
        except:
            pass
        try:
            url = unquote(url)
        except:
            pass
        referer = False
        if not '|' in url:
            headers = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36&Connection=keep-alive'
        else:
            try:
                url_split = url.split('|')
                url = url_split[0]
                #headers = '|' + url_split[1]
                try:
                    headers = unquote_plus(url_split[1])
                except:
                    pass
                try:
                    headers = unquote(url_split[1])
                except:
                    pass 
                headers = '|' + headers
                if not '&Connection' in headers:
                    headers = headers + '&Connection=keep-alive'
            except:
                headers = False
        try:
            name = xbmc.getInfoLabel('ListItem.Label')
        except:
            name = ''
        if not name:        
            name = 'F4M (INPUTSTREAM)'
        else:
            try:
                name = name + ' - ' + 'F4M (INPUTSTREAM)'
            except:
                pass
        if not iconImage:
            try:
                iconImage = xbmc.getInfoLabel('ListItem.Thumb')
            except:
                try:
                    iconImage = xbmc.getInfoLabel('ListItem.Icon')
                except:
                    iconImage = ''             
        li=xbmcgui.ListItem(name)
        if iconImage:
            li.setArt({"icon": "DefaultVideo.png", "thumb": iconImage})
        if not '.mp4' in url and not '.mp3' in url and not '.mkv' in url and not '.avi' in url and not '.rmvb' in url:
            url = self.ts_to_m3u8(url)
            url = url + headers
            li.setProperty('inputstream', 'inputstream.ffmpegdirect')
            li.setProperty('IsPlayable', 'true')
            if '.m3u8' in url:
                li.setContentLookup(False)
                li.setMimeType('application/x-mpegURL')
                li.setProperty('inputstream.ffmpegdirect.mime_type', 'application/x-mpegURL')
                li.setProperty('ForceResolvePlugin','false')
            else:
                li.setMimeType('video/mp2t')
                li.setProperty('inputstream.ffmpegdirect.mime_type', 'video/mp2t')
            li.setProperty('inputstream.ffmpegdirect.stream_mode', 'catchup')
            li.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'true')
            li.setProperty('inputstream.ffmpegdirect.is_catchup_stream', 'catchup')
            li.setProperty('inputstream.ffmpegdirect.catchup_granularity', '60')
            li.setProperty('inputstream.ffmpegdirect.catchup_terminates', 'true')
            if self.check_iptv(url):            
                li.setProperty('inputstream.ffmpegdirect.open_mode', 'curl')              
            li.setProperty('inputstream.ffmpegdirect.default_url',url)
            li.setProperty('inputstream.ffmpegdirect.catchup_url_format_string',url)
            li.setProperty('inputstream.ffmpegdirect.programme_start_time','1')
            li.setProperty('inputstream.ffmpegdirect.programme_end_time','19')
            li.setProperty('inputstream.ffmpegdirect.catchup_buffer_start_time','1')
            li.setProperty('inputstream.ffmpegdirect.catchup_buffer_offset','1') 
            li.setProperty('inputstream.ffmpegdirect.default_programme_duration','19')
            li.setPath(url)
            # xbmc.Player().play(item=url, listitem=li)
            if self.kversion > 19:
                info = li.getVideoInfoTag()
                info.setTitle(name)
            else:
                li.setInfo(type="Video", infoLabels={"Title": name, "Plot": ""})
            t_input = threading.Thread(target=iniciavideo.tocar,args=(url,li))
            t_input.start()              


    def hlsretry_player(self,url,iconimage):
        if self.check_iptv(url):
            url_base = url
            if not '.m3u8' in url and not '.mp4' in url and not '.avi' in url:
                url_base = self.ts_to_m3u8(url)
            criptografado = False
            # try:
            #     url_ = url.split('|')[0]
            # except:
            #     pass
            # try:
            #     url_ = url.split('%7C')[0]
            # except:
            #     pass                  
            try:
                r = requests.get(url_base,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'},timeout=4)
                src = r.text
                if 'METHOD=' in src:
                    criptografado = True
                
            except:
                pass
        else:
            url_base = ''
            criptografado = False        
        self.notify('Aguarde...')
        if criptografado:
            self.inputstream_player(url_base,iconimage)
        else:
            new_url = hlsretry.url_proxy + url         
            # try:
            #     r = requests.get(hlsretry.url_stop,timeout=1)
            # except:
            #     pass
            #xbmc.sleep(3000)
            self.notify('Iniciando F4mtester (HLSRETRY)...')
            s = hlsretry.Server()
            s.start()
            t1 = threading.Thread(target=self.play_video_thread, args=(new_url,iconimage))
            t1.start()
            count = 0
            while not xbmc.Player().isPlaying():
                count += 1
                time.sleep(1)
                if count == 12:
                    break
            t2 = threading.Thread(target=monitor_hlsretry)
            t2.start()                

    def tsdownloader_player(self,url,iconimage):
        self.notify('Aguarde...')
        new_url = tsdownloader.url_proxy + url
        # try:
        #     r = requests.get(tsdownloader.url_stop,timeout=1)
        # except:
        #     pass
        # xbmc.sleep(3000)
        self.notify('Iniciando F4mtester (TSDOWNLOADER)...')
        s = tsdownloader.Server()
        s.start()
        t1 = threading.Thread(target=self.play_video_thread, args=(new_url,iconimage))
        t1.start()
        count = 0
        while not xbmc.Player().isPlaying():
            count += 1
            time.sleep(1)
            if count == 12:
                break
        t2 = threading.Thread(target=monitor_tsdownloader)
        t2.start()              

     