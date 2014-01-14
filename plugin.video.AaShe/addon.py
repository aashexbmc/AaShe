import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import re
import cookielib

def showMainItems(localpath, handle):
	mainItems = [
		("Latest", "http://www.ashemaletube.com", ""),
		("Most Popular", "http://www.ashemaletube.com/most-viewed", "sort=mw"),
		("Top Rated", "http://www.ashemaletube.com/top-rated", "sort=tr"),		
		("Longest", "http://www.ashemaletube.com/longest", "sort=lg"),
		("Random", "http://www.ashemaletube.com/random", "")
		]

	li=xbmcgui.ListItem("Search")
	u=localpath + "?mode=4"
	xbmcplugin.addDirectoryItem(handle, u, li, True)

	li=xbmcgui.ListItem("Channels")
	u=localpath + "?mode=1"
	xbmcplugin.addDirectoryItem(handle, u, li, True)

	for name, url, sortBy in mainItems:
		li=xbmcgui.ListItem(name)
		u=localpath + "?mode=2&name=" + urllib.quote_plus(name) + \
      "&url=" + urllib.quote_plus(url) + "&sortBy=" + urllib.quote_plus(sortBy)
		xbmcplugin.addDirectoryItem(handle, u, li, True)

	xbmcplugin.endOfDirectory(handle)

def listChannels(localpath, handle):	
	sortBy = getSortBySetting()

	url="http://www.ashemaletube.com/channels.php"
	
	request = urllib2.urlopen(url)
	response = request.read()
	request.close()
	
	pattern = re.compile("<a title=\"(.+?)\" href=\"/channels/(.+?)/(.+?)/page1\.html\?sort=mw\">")

	match = pattern.findall(response)
	channels = []
	
	for title, id, name in match:
		print name
		if name not in channels:
			thumb = "http://t01.ashemaletube.com/ast/misc/cat" + id + ".jpg"
			channels.append(name)
			li=xbmcgui.ListItem(title, title, thumb, thumb)
			url = "http://www.ashemaletube.com/channels/"+ id + "/" + name
			u=localpath + "?mode=2&name=" + urllib.quote_plus(name) + "&url=" + urllib.quote_plus(url)
			xbmcplugin.addDirectoryItem(handle, u, li, True)
	xbmcplugin.endOfDirectory(handle)

def listChannelItems(localpath, handle, url, page, sortBy):			
	
	addSortParam = False
	
	if sortBy == None:
		sortBy = getSortBySetting()
	else:
		addSortParam = True	
	
	pageUrl = url + "/page" + str(int(page)) + ".html?" + sortBy
		
	getVideosList(localpath, handle, pageUrl)
	name = "Next Page"
	li=xbmcgui.ListItem(name)
	u=localpath + "?mode=2&name=" + urllib.quote_plus(name) + \
    "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1)

	if addSortParam == True:
		u = u + "&sortBy="  + urllib.quote_plus(sortBy)
	
	xbmcplugin.addDirectoryItem(handle, u, li, True)
	xbmcplugin.endOfDirectory(handle)

def getVideosList(localpath, handle, pageUrl):	
	videoLength = str(getSetting("videoLength")).lower()
	screenSize = str(getSetting("screenSize"))

	period = getPeriodSetting()	
	pageUrl = pageUrl + period
	
	cj = cookielib.CookieJar()
	ck = cookielib.Cookie(version=0, name='videosLengthFilter', value=videoLength, port=None, port_specified=False, domain='www.ashemaletube.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
	cj.set_cookie(ck)
	ck = cookielib.Cookie(version=0, name='screenSize', value=screenSize, port=None, port_specified=False, domain='www.ashemaletube.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
	cj.set_cookie(ck)
	request_object = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	
	response = request_object.open(pageUrl)
	response_html = response.read()
	response.close()
	
	videoDetialsRE = '<div class="thumb vidItem" .+?>.+? href="/videos/(.+?)/(.+?)\.html">.+? src="(.+?)" alt="(.+?)"'
	videoDurationRE = '<span class="fs11 viddata flr">(([0-9])?[:]?([0-9]{2}):([0-9]{2}))</span>'

	videoPattern = re.compile(videoDetialsRE, re.S)
	lenghtPattern = re.compile(videoDurationRE)
	
	videoDetails = videoPattern.findall(response_html)
	videoDurations = lenghtPattern.findall(response_html)
	
	n = 0
	for id, name, thumb, title in videoDetails:		
		duration = convertTimeToMinutes(videoDurations[n])
		li=xbmcgui.ListItem(title, title, thumb, thumb)		
		li.setInfo( type="Video", infoLabels={ "Title": title, "Duration": duration } )
		u=localpath + "?mode=3&name=" + urllib.quote_plus(name) + "&url=" + urllib.quote_plus("/videos/" + id + "/" + name + ".html") + "&thumb=" + urllib.quote_plus(thumb)
		xbmcplugin.addDirectoryItem(handle, u, li, False)
		n = n + 1

def playVideo(localpath, handle, url, name, thumb):
	request = urllib2.urlopen("http://www.ashemaletube.com" + url)
	response = request.read()
	request.close()

	p=re.compile("'file': \"(.+?)\"")
	match=p.findall(response)
	video = match[0]
	
	detail = xbmcgui.ListItem(name,iconImage=thumb,thumbnailImage=thumb); detail.setInfo('video',{'Title':name})
	
	xbmc.Player().play(video, detail, False)

def showSearchResult(localpath, handle, url, page):
	pageUrl = url + "page" + str(int(page)) + ".html?" + getSortBySetting()
	getVideosList(localpath, handle, pageUrl)
	name = "Next Page"
	li=xbmcgui.ListItem(name)
	u=localpath + "?mode=5&name=" + urllib.quote_plus(name) + \
    "&url=" + urllib.quote_plus(url) + "&page=" + str(int(page) + 1)
	xbmcplugin.addDirectoryItem(handle, u, li, True)
	xbmcplugin.endOfDirectory(handle)
	
def searchVideos(localpath, handle):
	searchUrl = "http://www.ashemaletube.com/search/"
	input = _get_keyboard( heading="Enter the query" )	
	if ( not input ): return False, 0	
	title = urllib.quote_plus(input)
	searchUrl = searchUrl + title + "/"	
	showSearchResult(localpath, handle, searchUrl, 1)
	
def getSetting(id):
	settings = xbmcaddon.Addon(id='plugin.video.AaShe')	
	settingValue = settings.getSetting(id)
	return settingValue

def getPeriodSetting():
	period=""
	periodSetting = getSetting("period")
	
	if periodSetting == "1":
		period="&so=y"
	elif periodSetting == "2":
		period="&so=d"
	elif periodSetting == "3":
		period="&so=a"
		
	return period

def getSortBySetting():
	sortBy=""
	sortSetting = getSetting("sortBy")
	
	if sortSetting == "1":
		sortBy="sort=mw"
	elif sortSetting == "2":
		sortBy="sort=tr"
	elif sortSetting == "3":
		sortBy="sort=lg"
	
	return sortBy
		
def _get_keyboard( default="", heading="", hidden=False ):	
	keyboard = xbmc.Keyboard( default, heading, hidden )
	keyboard.doModal()
	if ( keyboard.isConfirmed() ):
		return unicode( keyboard.getText(), "utf-8" )
	return default
	
def convertTimeToMinutes(time):
	minutes = 0
	if len(time) == 4:
		if len(time[1]) > 0:
			minutes = int(time[1]) * 60
		minutes = minutes + int(time[2])
		minutes = float(str(minutes) + "." + time[3])
	elif len(time) == 3:
		minutes = int(time[1])
		if minutes == 0:
			minutes = float("0." + time[2])
		else:
			minutes = float(str(minutes) + "." + time[2])
			
	print "length = " + str(len(time)) + ", time = " + str(time) + ", converted to = " + str(minutes)
			
	return minutes
	
def get_params(args):
	param=[]
	print "Parsing arguments: " + str(args)
	paramstring=args[2]
	if len(paramstring)>=2:
		params=args[2]
		cleanedparams=params.replace('?', '')
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

def main():
	params=get_params(sys.argv)
	mode=None
	url=None
	page=1
	name=None
	sortBy=None
	thumb=None
	try:
		url=urllib.unquote_plus(params["url"])
	except:
		pass
	try:
		mode=int(params["mode"])
	except:
		pass
	try:
		page=int(params["page"])
	except:
		pass
	try:
		name=urllib.unquote_plus(params["name"])
	except:
		pass
	try:
		sortBy=int(params["sortBy"])
	except:
		pass
	try:
		thumb=urllib.unquote_plus(params["thumb"])
	except:
		pass
		
	if mode==None:
		showMainItems(sys.argv[0], int(sys.argv[1]))
	if mode==1:
		listChannels(sys.argv[0], int(sys.argv[1]))
	elif mode==2:
		listChannelItems(sys.argv[0], int(sys.argv[1]), url, page, sortBy)	
	elif mode==3:
		playVideo(sys.argv[0], int(sys.argv[1]), url, name, thumb)
	elif mode==4:
		searchVideos(sys.argv[0], int(sys.argv[1]))
	elif mode==5:
		showSearchResult(sys.argv[0], int(sys.argv[1]), url, page)

if __name__ == "__main__":
	main()