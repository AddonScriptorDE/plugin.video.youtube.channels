#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,sys,urllib,urllib2,re,socket,os

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = 'plugin.video.youtube.channels'
xbox = xbmc.getCondVisibility("System.Platform.xbox")
addon = xbmcaddon.Addon(addonID)
addon_work_folder=xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
catsFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".cats")
iconVSX=xbmc.translatePath('special://home/addons/'+addonID+'/iconVSX.png')
forceViewMode=addon.getSetting("forceView")
viewMode=str(addon.getSetting("viewMode"))
showMessages=str(addon.getSetting("showMessages"))

if not os.path.isdir(addon_work_folder):
  os.mkdir(addon_work_folder)

def translation(id): return addon.getLocalizedString(id).encode('utf-8')

def index():
        addDir(translation(30001),"","favouriteChannels","")
        addDir(translation(30006),"","search","")
        addVSXDir("VidStatsX.com","","",iconVSX)
        xbmcplugin.endOfDirectory(pluginhandle)

def favouriteChannels():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if os.path.exists(catsFile):
          cats = []
          fh = open(catsFile, 'r')
          for line in fh:
            match=re.compile('(.+?)#(.+?)#(.+?)#(.+?)#', re.DOTALL).findall(line)
            cat=match[0][3]
            if cat not in cats:
              cats.append(cat)
              addCatMainDir("- "+cat, cat, "listCat", "")
          fh.close() 
        if os.path.exists(channelFavsFile):
          fh = open(channelFavsFile, 'r')
          all_lines = fh.readlines()
          for line in all_lines:
            match=re.compile('(.+?)#(.+?)#(.+?)#', re.DOTALL).findall(line)
            user=match[0][0]
            name=match[0][1]
            thumb=match[0][2]
            addChannelFavDir(name,user+"#1",'showSortSelection',thumb,user)
          fh.close()
        xbmcplugin.endOfDirectory(pluginhandle)

def listCat(cat):
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        if os.path.exists(catsFile):
          fh = open(catsFile, 'r')
          all_lines = fh.readlines()
          for line in all_lines:
            if cat+"#END" in line:
              match=re.compile('(.+?)#(.+?)#(.+?)#(.+?)#', re.DOTALL).findall(line)
              name=match[0][0]
              id=match[0][1]
              thumb=match[0][2]
              cat=match[0][3]
              addCatDir(name,id+"#1",'showSortSelection',thumb,id,cat)
          fh.close()
        xbmcplugin.endOfDirectory(pluginhandle)

def showSortSelection(url):
        addDir(translation(30021),url+"#published","listVideos","")
        addDir(translation(30022),url+"#viewCount","listVideos","")
        addDir(translation(30023),url+"#rating","listVideos","")
        xbmcplugin.endOfDirectory(pluginhandle)

def search():
        keyboard = xbmc.Keyboard('', translation(30006))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
          search_string = keyboard.getText().replace(" ","+")
          listSearchChannels(search_string+"#1")

def listSearchChannels(params):
        spl=params.split("#")
        search=spl[0]
        index=spl[1]
        content = getUrl("https://gdata.youtube.com/feeds/api/channels?q="+search+"&start-index="+index+"&max-results=25&v=2")
        match=re.compile("<openSearch:totalResults>(.+?)</openSearch:totalResults><openSearch:startIndex>(.+?)</openSearch:startIndex>", re.DOTALL).findall(content)
        maxIndex=int(match[0][0])
        startIndex=int(match[0][1])
        spl=content.split('<entry')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('<uri>https://gdata.youtube.com/feeds/api/users/(.+?)</uri>', re.DOTALL).findall(entry)
            user=match[0]
            match=re.compile("viewCount='(.+?)'", re.DOTALL).findall(entry)
            viewCount=match[0]
            match=re.compile("subscriberCount='(.+?)'", re.DOTALL).findall(entry)
            subscribers=match[0]
            match=re.compile("<title>(.+?)</title>", re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            match=re.compile("<summary>(.+?)</summary>", re.DOTALL).findall(entry)
            desc=""
            if len(match)>0:
              desc=match[0]
              desc=cleanTitle(desc)
            match=re.compile("<media:thumbnail url='(.+?)'", re.DOTALL).findall(entry)
            thumb=match[0]
            addChannelDir("[B]"+title+"[/B]  -  "+subscribers+" Subscribers",user+"#1",'showSortSelection',thumb,user,"Views: "+viewCount+"\nSubscribers: "+subscribers+"\n"+desc)
        if startIndex+25<=maxIndex:
          addDir(translation(30007),search+"#"+str(int(index)+25),'listSearchChannels',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def listVideos(params):
        spl=params.split("#")
        user=spl[0]
        index=spl[1]
        orderby=spl[2]
        content = getUrl("http://gdata.youtube.com/feeds/api/videos?author="+user+"&racy=include&max_results=25&start-index="+index+"&orderby="+orderby)
        match=re.compile("<openSearch:totalResults>(.+?)</openSearch:totalResults><openSearch:startIndex>(.+?)</openSearch:startIndex>", re.DOTALL).findall(content)
        maxIndex=int(match[0][0])
        startIndex=int(match[0][1])
        spl=content.split('<entry>')
        for i in range(1,len(spl),1):
          try:
            entry=spl[i]
            match=re.compile('<id>http://gdata.youtube.com/feeds/api/videos/(.+?)</id>', re.DOTALL).findall(entry)
            id=match[0]
            match=re.compile("viewCount='(.+?)'", re.DOTALL).findall(entry)
            viewCount=match[0]
            match=re.compile("duration='(.+?)'", re.DOTALL).findall(entry)
            durationTemp=int(match[0])
            min=(durationTemp/60)+1
            sec=durationTemp%60
            duration=str(min)+":"+str(sec)
            match=re.compile("<author><name>(.+?)</name>", re.DOTALL).findall(entry)
            author=match[0]
            match=re.compile("<title type='text'>(.+?)</title>", re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            match=re.compile("<content type='text'>(.+?)</content>", re.DOTALL).findall(entry)
            desc=""
            if len(match)>0:
              desc=match[0]
              desc=cleanTitle(desc)
            match=re.compile("<published>(.+?)T", re.DOTALL).findall(entry)
            date=match[0]
            thumb="http://img.youtube.com/vi/"+id+"/0.jpg"
            addLink(title,id,'playVideo',thumb,"Date: "+date+"; Views: "+viewCount+"\n"+desc,duration,author)
          except:
            pass
        if startIndex+25<=maxIndex:
          addDir(translation(30007),user+"#"+str(int(index)+25)+"#"+orderby,'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(youtubeID):
        url = getYoutubeUrl(youtubeID)
        listitem = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def getYoutubeUrl(youtubeID):
        if xbox==True:
          url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + youtubeID
        else:
          url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + youtubeID
        return url

def playChannel(id):
        content = getUrl("http://gdata.youtube.com/feeds/api/videos?author="+id+"&racy=include&max_results=25&start-index=1&orderby=published")
        spl=content.split('<entry>')
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        for i in range(1,len(spl),1):
          try:
            entry=spl[i]
            match=re.compile('<id>http://gdata.youtube.com/feeds/api/videos/(.+?)</id>', re.DOTALL).findall(entry)
            id=match[0]
            url = getYoutubeUrl(id)
            match=re.compile("<title type='text'>(.+?)</title>", re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            listitem = xbmcgui.ListItem(title)
            playlist.add(url,listitem)
          except:
            pass
        xbmc.Player().play(playlist)

def favourites(param):
        mode=param[:param.find("#")]
        channelEntry=param[param.find("#")+1:].replace("[B]","").replace("[/B]","")
        name=channelEntry[:channelEntry.find("#")]
        if mode=="ADD":
          if os.path.exists(channelFavsFile):
            fh = open(channelFavsFile, 'r')
            content=fh.read()
            fh.close()
            if content.find(channelEntry)==-1:
              fh=open(channelFavsFile, 'a')
              fh.write(channelEntry+"\n")
              fh.close()
          else:
            fh=open(channelFavsFile, 'a')
            fh.write(channelEntry+"\n")
            fh.close()
          if showMessages=="true":
            xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30016).format(channel=name)+',4000)')
        elif mode=="REMOVE":
          fh = open(channelFavsFile, 'r')
          content=fh.read()
          fh.close()
          entry=content[content.find(channelEntry):]
          fh=open(channelFavsFile, 'w')
          fh.write(content.replace(channelEntry+"\n",""))
          fh.close()
          xbmc.executebuiltin("Container.Refresh")
          if showMessages=="true":
            xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30017).format(channel=name)+',4000)')

def addToCat(args):
        match=re.compile('(.+?)#(.+?)#(.+?)#', re.DOTALL).findall(args)
        name=match[0][0]
        id=match[0][1]
        thumb=match[0][2]
        playlistsTemp=[]
        catsCount=20
        for i in range(0,catsCount,1):
          playlistsTemp.append(addon.getSetting("cat_"+str(i)))
        playlists=[]
        for pl in playlistsTemp:
          if pl!="":
            playlists.append(pl)
        playlists.append("- "+translation(30005))
        if len(playlists)==0:
          addon.openSettings()
          playlistsTemp=[]
          for i in range(0,catsCount,1):
            playlistsTemp.append(addon.getSetting("cat_"+str(i)))
          playlists=[]
          for pl in playlistsTemp:
            if pl!="":
              playlists.append(pl)
          playlists.append("- "+translation(30005))
        dialog = xbmcgui.Dialog()
        index=dialog.select(translation(30004), playlists)
        if index>=0:
          pl = playlists[index]
          while ("- "+str(translation(30005)) in pl):
            addon.openSettings()
            playlistsTemp=[]
            for i in range(0,catsCount,1):
              playlistsTemp.append(addon.getSetting("cat_"+str(i)))
            playlists=[]
            for pl in playlistsTemp:
              if pl!="":
                playlists.append(pl)
            playlists.append("- "+translation(30005))
            dialog = xbmcgui.Dialog()
            index=dialog.select(translation(30004), playlists)
            if index>=0:
              pl = playlists[index]
          if pl!="":
            playlistEntry=name+"#"+id+"#"+thumb+"#"+pl+"#END"
            if os.path.exists(catsFile):
              fh = open(catsFile, 'r')
              content=fh.read()
              fh.close()
              if content.find(playlistEntry)==-1:
                fh=open(catsFile, 'a')
                fh.write(playlistEntry+"\n")
                fh.close()
            else:
              fh=open(catsFile, 'a')
              fh.write(playlistEntry+"\n")
              fh.close()
          if showMessages=="true":
            xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30018).format(channel=name, cat=pl)+',5000)')
          xbmc.executebuiltin("Container.Refresh")

def removeFromCat(args):
        match=re.compile('(.+?)#(.+?)#(.+?)#(.+?)#', re.DOTALL).findall(args)
        name=match[0][0]
        id=match[0][1]
        thumb=match[0][2]
        cat=match[0][3]
        fh = open(catsFile, 'r')
        content=fh.read()
        fh.close()
        fh=open(catsFile, 'w')
        fh.write(content.replace(args+"\n",""))
        fh.close()
        xbmc.executebuiltin("Container.Refresh")
        if showMessages=="true":
          xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30019).format(channel=name, cat=cat)+',5000)')
        xbmc.executebuiltin("Container.Refresh")

def removeCat(args):
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Info:', translation(30010)+"?")
        if ok==True:
          newContent=""
          fh = open(catsFile, 'r')
          for line in fh:
            if args+"#END" not in line:
               newContent+=line
          fh.close()
          fh=open(catsFile, 'w')
          fh.write(newContent)
          fh.close()
          xbmc.executebuiltin("Container.Refresh")

def renameCat(args):
        keyboard = xbmc.Keyboard(args, translation(30011)+" "+args)
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
          newName = keyboard.getText()
          fh=open(catsFile, 'r')
          content=fh.read()
          fh.close()
          fh=open(catsFile, 'w')
          fh.write(content.replace(args+"#END",newName+"#END"))
          fh.close()
          xbmc.executebuiltin("Container.Refresh")

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def cleanTitle(title):
        title=title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","\\").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
        title=title.replace("&#038;","&").replace("&#8230;","...").replace("&#8211;","-").replace("&#8220;","-").replace("&#8221;","-").replace("&#8217;","'")
        title=title.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
        title=title.strip()
        return title

def addLink(name,url,mode,iconimage,desc="",duration="",author=""):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc, "Duration": duration, "Director": author } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addVSXDir(name,url,mode,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="plugin://plugin.video.vidstatsx_com",listitem=liz,isFolder=True)
        return ok

def addChannelDir(name,url,mode,iconimage,user,desc=""):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
        playListInfos="ADD#"+user+"#"+name[:name.find("  -")]+"#"+iconimage+"#"
        liz.addContextMenuItems([(translation(30026), 'XBMC.RunPlugin(plugin://'+addonID+'/?mode=playChannel&url='+user+')',),(translation(30024), 'XBMC.RunPlugin(plugin://'+addonID+'/?mode=favourites&url='+urllib.quote_plus(playListInfos)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addChannelFavDir(name,url,mode,iconimage="DefaultFolder.png",user=""):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        if iconimage=="": iconimage="DefaultFolder.png"
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        playListInfos="REMOVE#"+user+"#"+name+"#"+iconimage+"#"
        liz.addContextMenuItems([(translation(30026), 'XBMC.RunPlugin(plugin://'+addonID+'/?mode=playChannel&url='+user+')',),(translation(30002), 'RunPlugin(plugin://'+addonID+'/?mode=addToCat&url='+urllib.quote_plus(name+"#"+user+"#"+iconimage+"#")+')',),(translation(30025), 'XBMC.RunPlugin(plugin://'+addonID+'/?mode=favourites&url='+urllib.quote_plus(playListInfos)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addCatMainDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.addContextMenuItems([(translation(30009), 'RunPlugin(plugin://'+addonID+'/?mode=removeCat&url='+urllib.quote_plus(url)+')',),(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=renameCat&url='+urllib.quote_plus(url)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addCatDir(name,url,mode,iconimage,user,cat):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.addContextMenuItems([(translation(30026), 'XBMC.RunPlugin(plugin://'+addonID+'/?mode=playChannel&url='+user+')',),(translation(30003), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromCat&url='+urllib.quote_plus(name+"#"+user+"#"+iconimage+"#"+cat+"#END")+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'search':
    search()
elif mode == 'favouriteChannels':
    favouriteChannels()
elif mode == 'listSearchChannels':
    listSearchChannels(url)
elif mode == 'showSortSelection':
    showSortSelection(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'listCat':
    listCat(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playChannel':
    playChannel(url)
elif mode == 'favourites':
    favourites(url)
elif mode == 'addToCat':
    addToCat(url)
elif mode == 'removeFromCat':
    removeFromCat(url)
elif mode == 'removeCat':
    removeCat(url)
elif mode == 'renameCat':
    renameCat(url)
else:
    index()
