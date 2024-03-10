# -*- coding: utf-8 -*-
'''
	f4mtester

	@package plugin.video.f4mTester

	@copyright (c) 2024, f4mTester
	@license GNU General Public License, version 3 (GPL-3.0)

'''

from sys import argv

from resources.lib import home
from kodi_helper import parse_qsl

try:
	params = dict(parse_qsl(argv[2].replace('?', '')))
except:
	params = {}

home.router(params)