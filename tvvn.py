# -*- coding: UTF-8 -*-
#---------------------------------------------------------------------
# File: tvvn.py
# By:   Binh Nguyen <binh@vnoss.org>
# Date: 2013-06-05
#---------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#---------------------------------------------------------------------

import os, re, sys, gzip, urllib, urllib2, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from StringIO import StringIO

try:
	import json
except:
	import simplejson as json

addon = xbmcaddon.Addon('plugin.video.tvvn')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
mysettings = xbmcaddon.Addon(id='plugin.video.tvvn')
home = mysettings.getAddonInfo('path')
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
datafile = xbmc.translatePath(os.path.join(home, 'data.json'))

data = json.loads(open(datafile,"r").read())

mode=None

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
							
	return param

params=get_params()

try: 	chn=urllib.unquote_plus(params["chn"])
except: pass
try: 	src=urllib.unquote_plus(params["src"])
except: pass
try: 	mode=int(params["mode"])
except: pass

def construct_menu(namex):
	name = data['directories'][namex]['title']
	lmode = '2'
	iconimage = ''
	desc = data['directories'][namex]['desc']

	menu_items = data['directories'][namex]['content']
	for menu_item in menu_items:
		#type == channel
		if (menu_item['type'] == "chn"):
			add_chn_link (menu_item['id'])
		#type == directory
		if (menu_item['type'] == "dir"):
			add_dir_link (menu_item['id'])
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	return

def add_chn_link (namex):
	ok = True
	title = data['channels'][namex]['title']
	name = title
	iconimage = data['channels'][namex]['logo']
	desc = data['channels'][namex]['desc']
	ref = data['channels'][namex]['src']['referer']
	stream_name = data['channels'][namex]['src']['playpath']
	src = data['channels'][namex]['src']['id']

	if (iconimage == ''):
		iconimage = 'default.png'
	if (mysettings.getSetting('descriptions')=='true' and desc != ''):
		if mysettings.getSetting('descriptions_on_right') == 'false':
			name = desc+"    "+name
		else:
			name = name+"    "+desc

	give_url = sys.argv[0]+"?mode=1&chn="+namex+"&src="+src
	liz = xbmcgui.ListItem( name, iconImage=xbmc.translatePath(os.path.join(home, 'resources', 'logos', iconimage)), thumbnailImage=xbmc.translatePath(os.path.join(home, 'resources', 'logos', iconimage)))
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setProperty("Fanart_Image",fanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=give_url,listitem=liz)

def add_dir_link (namex):
	name = '['+data['directories'][namex]['title']+']'
	desc = data['directories'][namex]['desc']
	iconimage = data['directories'][namex]['logo']
	if (iconimage == ''):
		iconimage = 'default.png'
	if (mysettings.getSetting('descriptions')=='true' and desc != ''):
		if mysettings.getSetting('descriptions_on_right') == 'false':
			name = desc+"    "+name
		else:
			name = name+"    "+desc
	li = xbmcgui.ListItem( name, iconImage=xbmc.translatePath(os.path.join(home, 'resources', 'logos', iconimage)), thumbnailImage=xbmc.translatePath(os.path.join(home, 'resources', 'logos', iconimage)))
	li.setInfo(type="Video", infoLabels={"Title": name})
	li.setProperty("Fanart_Image",fanart)
	give_url = sys.argv[0]+"?mode=2&chn="+namex
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=give_url, listitem=li, isFolder=True)

def update_chn_list():
	url = mysettings.getSetting('json_url')
	request = urllib2.Request(url)
	request.add_header('Accept-encoding', 'gzip')
	url_error = "no"
	try:
		response = urllib2.urlopen(request)
	except urllib2.URLError, e:
		url_error = "yes"

	if (url_error == "no"):
		buf = StringIO(response.read())
		f = gzip.GzipFile(fileobj=buf)
		ff=f.read()
		r_data=json.loads(ff)
		if (data['timestamp'] < r_data['timestamp']):
			day_diff = str((int(r_data['timestamp']) - int(data['timestamp'])) /60/60/24)
			dialog = xbmcgui.Dialog()
			ack = dialog.yesno(addon.getLocalizedString(30005), addon.getLocalizedString(30006)+" "+day_diff+" day(s) old",addon.getLocalizedString(30007))
			if ack:
				d = open(datafile, 'r+')
				d.seek(0)
				d.write(ff)
				d.close()

def play_link(chn, src):
	item = xbmcgui.ListItem(chn)

	playpath = data['channels'][chn]['src']['playpath']
	videoUrl = data['sources'][src]['url']
	if (playpath != ''):
		videoUrl = videoUrl+"/"+playpath
	swfUrl = data['sources'][src]['swfurl']
	pageUrl = data['sources'][src]['pageurl']
	if (data['channels'][chn]['src']['referer'] != ''):
		pageUrl = pageUrl+"/"+data['channels'][chn]['src']['referer']
	flashVer = 'LNX_11,2,202,233'
	token = data['sources'][src]['token']
	app = data['sources'][src]['app']

	full_url = videoUrl+' swfVfy=1 live=1 token='+token+' playpath='+playpath+' flashVer='+flashVer+' pageUrl='+pageUrl+' tcUrl='+videoUrl+' swfUrl='+swfUrl

	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(full_url, item)
	return

def Init():
	construct_menu("root")
	if (mysettings.getSetting('json_url_auto_update')=='true' and mysettings.getSetting('json_url')!=''):
		update_chn_list()

if mode==None:
	Init()
elif mode==1:
	play_link(chn, src)
elif mode==2:
	construct_menu(chn)
