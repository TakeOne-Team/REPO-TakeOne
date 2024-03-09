# -*- coding: utf-8 -*-
import six
import requests
import re
import sys
import os
if six.PY3:
    from urllib.parse import urlencode, quote_plus, unquote_plus
else:
    from urllib import urlencode, quote_plus, unquote_plus
from kodi_six import xbmc, xbmcaddon, xbmcvfs, xbmcgui, xbmcplugin


plugin = sys.argv[0]
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonid = addon.getAddonInfo('id')
icon = addon.getAddonInfo('icon')
translate = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
profile = translate(addon.getAddonInfo('profile')) if six.PY3 else translate(addon.getAddonInfo('profile')).decode('utf-8')
home = translate(addon.getAddonInfo('path')) if six.PY3 else translate(addon.getAddonInfo('path')).decode('utf-8')
fanart_default = os.path.join(home, 'fanart.png')
modulo = os.path.join(home, "lib")
sys.path.append(modulo)

    
def route(f):
    action_f = f.__name__
    params_dict = {}
    param_string = sys.argv[2]
    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
        for command in split_commands:
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = split_command[1]
                    try:
                        key = unquote_plus(key)
                    except:
                        pass
                    try:
                        value = unquote_plus(value)
                    except:
                        pass
                    params_dict[key] = value
                else:
                    params_dict[command] = ""
    url = params_dict.get('url')
    if url is None and action_f == 'main':
        f(params_dict)
    elif url and action_f == 'player':
        f(params_dict)

def get_kversion():
	full_version_info = xbmc.getInfoLabel('System.BuildVersion')
	baseversion = full_version_info.split(".")
	intbase = int(baseversion[0])
	# if intbase > 16.5:
	# 	log('HIGHER THAN 16.5')
	# if intbase < 16.5:
	# 	log('LOWER THAN 16.5')
	return intbase


@route
def main(param):
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Exemplo', 'Exemplo: plugin://plugin.video.resolverurl_player?url=https://dropload.io/f96fql6zfxxy')


@route
def player(param):
    url = param.get('url', '')
    if url:
        import resolveurl
        if resolveurl.HostedMediaFile(url):
            resolved = resolveurl.resolve(url)
            liz = xbmcgui.ListItem()
            liz.setPath(resolved)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
