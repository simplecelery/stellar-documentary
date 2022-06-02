import time
import StellarPlayer
import math
import json
import os
import sys
import requests
from shutil import copyfile

class jlpplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.configjson = ''
        self.medias = []
        self.pageindex = 0
        self.pagenumbers = 0
        self.cur_page = ''
        self.max_page = ''
        self.pg = ''
        self.wd = ''
        self.source = []
        self.allSource = []
        self.allmovidesdata = {}
        self.mediasize = 18
    
    def start(self):
        super().start()
        self.configjson = 'source.json'
        jsonpath = self.player.dataDirectory + os.path.sep +'source.json'
        if os.path.exists(jsonpath) == False:
            localpath = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + 'source.json'
            print(localpath)
            if os.path.exists(localpath):
                try:
                    copyfile(localpath,jsonpath)
                except IOError as e:
                    print("Unable to copy file. %s" % e)
                except:
                    print("Unexpected error:", sys.exc_info())
        down_url = "https://g.4ris.xyz/https://raw.githubusercontent.com/simplecelery/stellar-documentary/main/source.json"
        try:
            r = requests.get(down_url,timeout = 5,verify=False) 
            result = r.status_code
            if result == 200:
                with open(self.configjson,'wb') as f:
                    f.write(r.content)
        except:
            print('get remote source.json error')
        self.loadSourceFile(self.configjson)
        self.loadSource()
    
    def loadSource(self):
        displaynum = min(len(self.source),self.mediasize)
        self.medias = []
        for i in range(displaynum):
            self.medias.append(self.source[i])
        self.pageindex = 1
        self.pagenumbers = len(self.source) // self.mediasize
        if self.pagenumbers * self.mediasize < len(self.source):
            self.pagenumbers = self.pagenumbers + 1
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'   

      
    def loadSourceFile(self,filename):
        file = open(filename, "rb")
        self.allSource = json.loads(file.read())
        print(len(self.allSource))
        for item in self.allSource:
            newitem = {'title':item['name'],'picture':item['pic'],'info':item['blurb'],'urls':item['source']}
            self.source.append(newitem)
        file.close()    
    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,720,'',controls)        
    
    def onSearch(self, *args):
        self.loading()
        self.source = []
        search_word = self.player.getControlValue('main','search_edit').strip()
        if search_word == '':
            for item in self.allSource:
                newitem = {'title':item['name'],'picture':item['pic'],'info':item['blurb'],'urls':item['source']}
                self.source.append(newitem)
        else:
            for item in self.allSource:
                if item['name'].find(search_word) >= 0 or item['blurb'].find(search_word) >= 0:
                    newitem = {'title':item['name'],'picture':item['pic'],'info':item['blurb'],'urls':item['source']}
                    self.source.append(newitem)
        self.loadSource()
        self.player.updateControlValue('main','mediagrid',self.medias)
        self.loading(True)
        
    def makeLayout(self):
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'image','name':'picture', '@click':'on_grid_click'},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':13,'height':0.15,'hAlign':'center','@click':'on_grid_click'}
                    ],
                    'dir':'vertical'
                }
            ]
        ]
        controls = [
            {'type':'space','height':5},
            {
                'group':[
                    {'type':'edit','name':'search_edit','label':'搜索','width':0.8},
                    {'type':'button','name':'搜索','@click':'onSearch','width':100},
                ],
                'width':1.0,
                'height':30
            },
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':200,'itemwidth':130},
            {'group':
                [
                    {'type':'space'},
                    {'group':
                        [
                            {'type':'label','name':'cur_page',':value':'cur_page'},
                            {'type':'link','name':'首页','fontSize':13,'@click':'onClickFirstPage'},
                            {'type':'link','name':'上一页','fontSize':13,'@click':'onClickFormerPage'},
                            {'type':'link','name':'下一页','fontSize':13,'@click':'onClickNextPage'},
                            {'type':'link','name':'末页','fontSize':13,'@click':'onClickLastPage'},
                            {'type':'label','name':'max_page',':value':'max_page'},
                        ]
                        ,'width':0.7
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls
            
        
    def on_grid_click(self, page, listControl, item, itemControl):
        mediainfo = self.medias[item]
        self.createMediaFrame(mediainfo)
        
    def createMediaFrame(self,mediainfo):
        actmovies = []
        if len(mediainfo['urls']) > 0:
            print(mediainfo['urls'][0])
            actmovies = mediainfo['urls'][0]['medias']
        medianame = mediainfo['title']
        self.allmovidesdata[medianame] = {'allmovies':mediainfo['urls'],'actmovies':actmovies}
        
        xl_list_layout = {'type':'link','name':'flag','textColor':'#ff0000','width':0.6,'@click':'on_xl_click'}
        movie_list_layout = {'type':'link','name':'title','@click':'on_movieurl_click'}
        
        controls = [
            {'type':'space','height':10},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':mediainfo['picture'],'width':0.4},
                    {'type':'space','width':10},
                    {'group':[
                            {'type':'label','name':'medianame','textColor':'#ff7f00','fontSize':15,'value':mediainfo['title'],'height':40},
                            {'type':'space','height':10},
                            {'type':'label','name':'info','textColor':'#005555','value':mediainfo['info'],'height':250,'vAlign':'top'},
                            {'type':'space','height':5},
                        ],
                        'dir':'vertical'
                    },
                    {'type':'space','width':10}
                ],
                'width':1.0,
                'height':400
            },
            {'group':
                {'type':'grid','name':'xllist','itemlayout':xl_list_layout,'value':mediainfo['urls'],'separator':True,'itemheight':30,'itemwidth':100},
                'height':80
            },
            {'type':'space','height':5},
            {'group':
                {'type':'grid','name':'movielist','itemlayout':movie_list_layout,'value':actmovies,'separator':True,'itemheight':30,'itemwidth':120},
                'height':120
            }
        ]
        result,control = self.doModal(mediainfo['title'],680,640,'',controls)

    def on_xl_click(self, page, listControl, item, itemControl):
        self.player.updateControlValue(page,'movielist',[])
        if len(self.allmovidesdata[page]['allmovies']) > item:
            self.allmovidesdata[page]['actmovies'] = self.allmovidesdata[page]['allmovies'][item]['medias']
        self.player.updateControlValue(page,'movielist',self.allmovidesdata[page]['actmovies'])
    
    def on_movieurl_click(self, page, listControl, item, itemControl):
        if len(self.allmovidesdata[page]['actmovies']) > item:
            playurl = self.allmovidesdata[page]['actmovies'][item]['url']
            playname = page + ' ' + self.allmovidesdata[page]['actmovies'][item]['title']
            playlist = []
            for xl in self.allmovidesdata[page]['allmovies']:
                if len(xl['medias']) > item:
                    playlist.append({'url':xl['medias'][item]['url']})
                try:
                    self.player.playMultiUrls(playlist,playname)
                except:
                    self.player.play(playurl, caption=playname) 

    def loadPageData(self):
        maxnum = len(self.source)
        if (self.pageindex - 1) * self.mediasize > maxnum:
            return
        self.medias = []
        startnum = (self.pageindex - 1) * self.mediasize
        endnum = self.pageindex * self.mediasize
        endnum = min(maxnum,endnum)
        print(startnum)
        print(endnum)
        for i in range(startnum,endnum):
            self.medias.append(self.source[i])
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.player.updateControlValue('main','mediagrid',self.medias)
       
    def onClickFirstPage(self, *args):
        self.pageindex = 1
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def onClickFormerPage(self, *args):
        if self.pageindex == 1:
            return
        self.pageindex = self.pageindex - 1
        self.loading()
        self.loadPageData()
        self.loading(True)
    
    def onClickNextPage(self, *args):
        if self.pageindex >= self.pagenumbers:
            return
        self.pageindex = self.pageindex + 1
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def onClickLastPage(self, *args):
        self.pageindex = self.pagenumbers
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)

    def onPlayerSearch(self, dispatchId, searchId, wd, limit):
        # 播放器搜索异步接口
        try:
            result = [{
                "name": item["title"],
                "pic": item["picture"],
                "summary": item["info"],
                "pub_date": '',
                "urls": [['播放', item['url']]]
            } for item in self.source if wd in item['title']][:limit]
            print(result)
            self.player.dispatchResult(dispatchId, searchId=searchId, wd=wd, result=result)
        except:
            self.player.dispatchResult(dispatchId, searchId=searchId, wd=wd, result=[])
        
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = jlpplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()