# -*- coding: utf-8 -*-

import sys, os, re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import base64
#import hashlib
import json
#import glob
import copy
import time
#import mimetypes
import datetime
import simplecache
import shutil

from threading import Lock
from threading import Thread
from distutils.version import LooseVersion
import threading


# Compatibilidades para kodi 18 y superiores
from six.moves import urllib_parse
from six.moves import reload_module
from six.moves import urllib_request
from six.moves import reduce
import six

if six.PY3:
    import types, importlib
    import queue
    long = int
    LOGINFO = xbmc.LOGINFO
else:
    import imp
    import Queue as queue
    LOGINFO = xbmc.LOGNOTICE

try:
    translatePath = xbmcvfs.translatePath
except:
    translatePath =  xbmc.translatePath
try:
    makeLegalFilename = xbmcvfs.makeLegalFilename
except:
    makeLegalFilename = xbmc.makeLegalFilename


# Globales
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')
HEADING = "%s (%s)" %(ADDON_NAME, ADDON_VERSION)
RUNTIME_PATH = translatePath(ADDON.getAddonInfo('Path'))
DATA_PATH = translatePath(ADDON.getAddonInfo('Profile'))
IMAGE_PATH = os.path.join(RUNTIME_PATH, 'resources', 'media')


# Clases auxiliares
class Item(object):
    defaults = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __contains__(self, item):
        return item in self.__dict__

    def __getattribute__(self, item):
        return object.__getattribute__(self, item)

    def __getattr__(self, item):
        if item.startswith("__"):
            return object.__getattribute__(self, item)
        else:
            return self.defaults.get(item, '')

    def __eq__(self, other):
        return isinstance(other, Item) and self.action == other.action and self.content == other.content and \
               self.tmdb == other.tmdb and self.season == other.season and self.episode == other.episode

    def __str__(self):
        return '{%s}' % (', '.join(['\'%s\': %s' % (k, repr(self.__dict__[k])) for k in sorted(self.__dict__.keys())]))

    def pop(self, attr):
        return self.__dict__.pop(attr, None)

    def getart(self):
        if 'fanart' not in self.__dict__:
            self.__dict__['fanart'] = os.path.join(RUNTIME_PATH, 'fanart.gif')
        d = {k: self.__dict__.get(k) for k in ['poster', 'icon', 'fanart', 'thumb'] if k in self.__dict__}
        if not d.get('thumb'):
            d['thumb'] = d.get('poster') or d.get('icon')
        if not d.get('icon'):
            d['icon'] = d.get('thumb', '')
        if not d.get('poster'):
            d['poster'] = d.get('thumb', '')
        return d

    def tourl(self):
        value = self.__str__()
        if not isinstance(value, six.binary_type):
            value = six.binary_type(value, 'utf8')
        return six.ensure_str(urllib_parse.quote(base64.b64encode(value)))

    def fromurl(self, url):
        str_item = base64.b64decode(urllib_parse.unquote(url))
        self.__dict__.update(eval(str_item))
        return self

    def tojson(self, path=""):
        if path:
            open(path, "wb").write(six.ensure_binary(dump_json(self.__dict__)))
        else:
            return six.ensure_str(dump_json(self.__dict__))

    def fromjson(self, json_item=None, path=""):
        if path:
            json_item = six.ensure_str(open(path, "rb").read())

        if isinstance(json_item, dict):
            item = json_item
        else:
            item = load_json(json_item)
        self.__dict__.update(item)
        return self

    def is_label(self):
        return not self.__dict__.get('action')

    def clone(self, **kwargs):
        newitem = copy.deepcopy(self)
        for k in ['label', 'type', 'contextMenu']:
            if k in newitem.__dict__:
                newitem.__dict__.pop(k)

        for k, v in kwargs.items():
            setattr(newitem, k, v)
        return newitem


class Video(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return repr(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def __getattr__(self, name):
        if name.startswith("__"):
            return super(Video, self).__getattribute__(name)

        elif name == 'type':
            return self._get_type()

        elif name == 'is_InputStream':
            if self.type in ['mpd', 'rtmp', 'hls']:
                return True
            return False

        elif name == 'player':
            if 'player' in self.__dict__:
                return self.player.lower()
            else:
                return 'default'

        elif name == 'label':
            if 'label' in self.__dict__:
                return self.label
            else:
                lng = {'es': u'Castellano', 'fr': u'Frances', 'en': u'Ingles', 'ru': u'Ruso', 'de': u'Aleman',
                       'it': u'Italiano', 'eu': u'Euskera', 'vo': u'Versión original'}  # ISO_639-1
                label = ''
                if self.lang:
                    label += lng.get(self.lang.lower(), self.lang)

                if self.res:
                    res_num = None
                    if isinstance(self.res, int):
                        res_num = self.res
                    elif not self.res.lower() in ['4k', '8k']:
                        res_num = re.findall(r'(\d+)', self.res)[0]
                    label += " [%s]" % ("%sp" % res_num) if res_num else self.res
                else:
                    label += (" (%s)" % self.type.upper())

                if self.bitrate:
                    try:
                        bitrate = int(self.bitrate)
                        if bitrate / 1000000.0 > 10:
                            l_bitrate = " - %dMbps" % (bitrate / 1000000)
                        elif bitrate / 1000000.0 > 1:
                            l_bitrate = " - %.2fMbps" % (bitrate / 1000000.0)
                        elif bitrate / 1000.0 > 2:
                            l_bitrate = " -  %dKbps" % (bitrate / 1000)
                        else:
                            l_bitrate = " - %dbps" % bitrate
                    except:
                        l_bitrate = " - %s" % self.bitrate
                    label = label[:-1] + l_bitrate + label[-1]

                return label

        else:
            # return self.__dict__.get(name, self.defaults.get(name, ''))
            return self.__dict__.get(name, '')

    def __deepcopy__(self, memo):
        new = Video(**self.__dict__)
        return new

    def _get_type(self):
        url = self.url if not isinstance(self.url, list) else self.url[0]
        if url.startswith('rtmp'):
            return 'rtmp'
        else:
            ext = os.path.splitext(url.split('?')[0].split('|')[0])[1]
            if ext.startswith('.'): ext = ext[1:]
            return ext.lower()

    def clone(self, **kwargs):
        newvideo = copy.deepcopy(self)
        for k, v in kwargs.items():
            setattr(newvideo, k, v)
        return newvideo


# Funciones auxiliares
def logger(message, level=None):
    def format_message(data=""):
        try:
            value = str(data)
        except Exception:
            value = repr(data)

        if isinstance(value, six.binary_type):
            value = six.text_type(value, 'utf8', 'replace')

        return value

    texto = '[%s] %s' % (xbmcaddon.Addon().getAddonInfo('id'), format_message(message))

    try:
        if level == 'info':
            xbmc.log(texto, LOGINFO)
        elif level == 'error':
            xbmc.log("######## ERROR #########", xbmc.LOGERROR)
            xbmc.log(texto, xbmc.LOGERROR)
        else:
            xbmc.log("######## DEBUG #########", LOGINFO)
            xbmc.log(texto, LOGINFO)
    except:
        # xbmc.log(six.ensure_str(texto, encoding='latin1', errors='strict'), LOGINFO)
        xbmc.log(str([texto]), LOGINFO)

def time_to_seconds(time_in):
    try:
        if len(time_in.split(':')) != 3:
            time_in = '00:' + time_in
        h, m, s = map(int, time_in.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return 0

def remove_white_spaces(html):
    patron = r'\n|\r|\t|&nbsp;'
    return re.sub(r'\s+', ' ', re.sub(patron, '', html))

"""def select_option(vit, titulo = "Selecciona una calidad/resolución"):
    select = 0
    ret = None

    if isinstance(vit, list):
        if len(vit) > 1:
            vit = sorted_videolist(vit)
            labels = list()
            no_repetidos = list()
            i = 0
            for li in vit[:]:
                key = str(li.url) + li.type
                if (key) not in no_repetidos:
                    i += 1
                    label = '%s. %s' % (i, li.label)
                    labels.append(label)
                    no_repetidos.append(key)
                else:
                    vit.remove(li)

            if len(vit) > 1:
                select = xbmcgui.Dialog().select(titulo, labels)

    else:
        vit = [vit]

    if select > -1:
        ret= vit[select]

    return ret
    """


# Funciones JSON
locker = Lock()
def load_json_file(path):
    with locker:
        if os.path.isfile(path):
            data = open(path, 'rb').read()
            data = load_json(six.ensure_str(data))
        else:
            data = dict()

    return data


def dump_json_file(data, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    data = six.ensure_binary(dump_json(data))
    with locker:
        open(path, 'wb').write(data)


def load_json(*args, **kwargs):
    if "object_hook" not in kwargs:
        kwargs["object_hook"] = set_encoding

    try:
        value = json.loads(*args, **kwargs)
    except Exception as e:
        # logger(e)
        value = {}

    return value


def dump_json(*args, **kwargs):
    if not kwargs:
        kwargs = {
            'indent': 4,
            'skipkeys': True,
            'sort_keys': True,
            'ensure_ascii': False
        }

    try:
        value = json.dumps(*args, **kwargs)
    except Exception:
        logger("Error dump_json")
        value = ''

    return value


def set_encoding(dct):
    if isinstance(dct, dict):
        return dict((set_encoding(key), set_encoding(value)) for key, value in dct.items())

    elif isinstance(dct, list):
        return [set_encoding(element) for element in dct]

    elif isinstance(dct, six.string_types):
        return six.ensure_str(dct)

    else:
        return dct


# Funciones de ordenacion
def natural_sort_key(s):
    import unicodedata
    s = six.ensure_text(str(s).lower())
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('(\d+)', ''.join((c for c in unicodedata.normalize('NFD', s)
                                                   if unicodedata.category(c) not in ['Po', 'Mn', 'Pc', 'Pd', 'Pe',
                                                                                      'Ps'])))]

def sorted_itenlist(itemlist, key='label'):
    l_sort = list()
    next = None

    if itemlist:
        if key not in itemlist[0].__dict__:
            logger("Error sorted_itenlist: El item no tiene el artributo %s" % key)
            return []

        if itemlist[-1].type == 'next':
            next = itemlist.pop()

        l_sort = sorted(itemlist, key=lambda x: natural_sort_key(x.__dict__.get(key)))

        if next:
            l_sort.append(next)

    return l_sort

def sorted_videolist(videolist):
    videolist.sort(key=lambda x: natural_sort_key(x.bitrate), reverse=True)
    videolist.sort(key=lambda x: natural_sort_key(x.res), reverse=True)
    videolist.sort(key=lambda x: x.is_InputStream, reverse=True)
    return videolist

# Funciones para los ajustes del addon
"""
def set_setting(name, value):
    try:
        settings = dict()
        path = os.path.join(DATA_PATH, 'settings.json')
        if os.path.isfile(path):
            settings = load_json_file(path)

        settings[name] = value

        dump_json_file(settings, path)

    except Exception as ex:
        logger("Error al guardar '%s' no se almacenara el valor \n%s" % (name, ex), 'error')
        return None

    return value

def get_setting(name, default=None):
    settings = dict()
    try:
        path = os.path.join(DATA_PATH, 'settings.json')
        if os.path.isfile(path):
            settings = load_json_file(path)
    except:
        pass

    return settings.get(name, default)
"""

# Main
from libs import httptools

httptools.load_cookies()
reload_module(httptools)