# -*- coding: utf-8 -*-
from resources.lib.plugin import f4mtester
import sys
import re

addonId = re.search('plugin\://(.+?)/',str(sys.argv[0])).group(1)
addon = f4mtester(addonId)

def router(params):
    streamtype = params.get("streamtype", '')
    action = params.get("action")
    name = params.get("name", "")
    iconimage = params.get('iconimage', '')
    if not iconimage:
        iconimage = params.get('iconImage', '')
    if not iconimage:
        iconimage = params.get('thumbnail', '')
    if not iconimage:
        iconimage = params.get('thumb', '')
    url = params.get("url", "")
    if streamtype and streamtype == 'HLSRETRY':
        # if addon.inverter():
        #     addon.tsdownloader_player(url,iconimage)
        # else:
        #     addon.hlsretry_player(url,iconimage)
        addon.hlsretry_player(url,iconimage)
    elif streamtype and streamtype == 'TSDOWNLOADER':
        # if addon.inverter():
        #     addon.hlsretry_player(url,iconimage)
        # else:
        #     addon.tsdownloader_player(url,iconimage)
        addon.hlsretry_player(url,iconimage)
    elif action == None:        
        addon.home()
    elif action == "pvr_settings":
        addon.pvr_settings()
    elif action == "pvr_active":
        addon.pvr_active()
    elif action == "pvr_remove":
        addon.pvr_remove()
    elif action == "settings":
        addon.open_settings()