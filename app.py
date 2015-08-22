#!flask/bin/python
from flask import Flask
import flask
import time
import subprocess
import os
import subprocess
from os import listdir
from os.path import isfile, join, isdir

# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/'  # refers to application_top
HOST_DIR = os.getenv('HOME') + '/website/'
BASE_DIR = os.getenv('HOME') + '/Dropbox/'
CSS_DIR = BASE_DIR + 'Sites/bootstrap' 
IMG_DIR = BASE_DIR + 'Sites/images' 
MARKDOWN = BASE_DIR + 'Markdown.pl'

HOME_PAGE_HEADER = ""
HOME_PAGE_TRAILER = ""

app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return flask.send_from_directory(HOST_DIR + 'pages/', 'index.html')

def translateMdFileToHtml( mdFile, outFileName ):
    tmpFileName = outFileName + ".tmp"
    tmpFile = open(outFileName + ".tmp" , "w")
    inFile = open( mdFile, 'r' )
        
    p = subprocess.Popen(MARKDOWN, 
              shell=True, stdout=tmpFile, stdin=inFile)
    p.wait()
    tmpFile.close()
    tmpFile = open(outFileName + ".tmp" , "r")
    tmpFile.seek(0)
    lines = tmpFile.read()
    tmpFile.close()
    inFile.close()

    header = '<!doctype html>\n '
    header += '<title> BYJ </title >\n'
    header += '<head> <link rel="stylesheet" type="text/css" href="/path/bootstrap/css/bootstrap.css"> </head>\n'
    header += '<body>\n <div class=mainContent>\n'
    trailer = '</div>\n</body>\n'
    with open(outFileName, "w") as outFile:
        outFile.write(header)
        with open(tmpFileName ) as addFile:
            for line in addFile:
                outFile.write(line)
        outFile.write(trailer)
        os.remove(tmpFileName)

def copyFile( src, dst ):
    with open(src, "r") as inFile:
        with open(dst, "w") as outFile:
            for line in inFile:
                outFile.write(line)

def findMdFilesInternal( dirname ):
    MdFileList = list()
    myPath = BASE_DIR + dirname
    for root, dirs, files in os.walk( myPath ):
        for name in files:
            if name.endswith('.yj.md'):
                MdFileList.append( os.path.join( root, name ) )

    httpLinks = list()
    for mdFile in MdFileList:
        outFileName = mdFile.replace(BASE_DIR, '')
        outFileName = outFileName.replace('/', '___').rsplit('.yj.md.html', 1)[0] + ".html"
        httpLink = outFileName.rsplit('.yj.md.html', 1)[0]
        httpLinks.append(httpLink)
        outFileName = HOST_DIR + 'pages/' + outFileName
        translateMdFileToHtml( mdFile, outFileName )
        copyFileName = outFileName.replace('.yj.md.html', '.ymd')
        copyFile( mdFile, copyFileName)

    mySet = dict()
    mySet["mdFiles"] = httpLinks
    return mySet

class Node:
    def __init__(self, path, parentPath=""):
        self.dirs = dict()
        self.files = list()
        self.name = path
        self.fullName = parentPath + "/" + path

    def __str__(self):
        return "Node: " + self.fullName

    def addSubNode(self, name):
        if name not in self.dirs:
            self.dirs[name] = Node(name, self.fullName)
        return self.dirs[name]

    def getSubNode(self, name):
        if name in self.dirs:
            return self.dirs[name]
        else:
            return None


def formRecursiveDict( names, separator='___' ):
    dictRoot = Node("root")
    for pathName in names:
        pathList = pathName.split( '___' )
        # Run once through the list and create all the dirs.
        # Use only upto path[:-1]
        subNode = dictRoot
        for nodeName in pathList[:-1]:
            subNode = subNode.addSubNode( nodeName )
        # Run once more through the list and create all the files.
        subNode = dictRoot
        for nodeName in pathList:
            if nodeName not in subNode.dirs:
                print "added file:", nodeName
                #subNode.files.append(nodeName)
                subNode.files.append(pathName)
            else:
                subNode = subNode.dirs[nodeName]
    return dictRoot
    
def pretty_items(htmlText, inpData, nametag="<strong>%s: </strong>", 
             itemtag="<li  id='%s.yj.md.html' onclick='changeContent(this)'>%s</li>",
             itemtagCollapse="<li  id='%s.yj.md.html' onclick='changeContent(this)' class='collapse'>%s</li>",
             valuetag="  %s", blocktag=('<ul>', '</ul>')):
    if isinstance(inpData, list):
        print inpData 
        for i in inpData:
            link = i.split('___')[-1]
            #htmlText.append(itemtagCollapse % ( i, link ) )
            htmlText.append(itemtag % ( i, link ) )
    elif len(inpData.files) > 0:
        htmlText.append(blocktag[0])
        #pretty_items(htmlText, inpData.files)
        for i in inpData.files:
            link = i.split('___')[-1]
            #htmlText.append(itemtagCollapse % ( i, link ) )
            htmlText.append(itemtag % ( i, link ) )
        htmlText.append(blocktag[1])
    elif len(inpData.dirs) > 0:
        htmlText.append(blocktag[0])
        for k, v in inpData.dirs.iteritems():
            name = nametag % k
            htmlText.append(itemtag % ( name, name) )
            pretty_items(htmlText, v)
        htmlText.append(blocktag[1])
    return htmlText

def pretty_items_old(htmlText, inpData, nametag="<strong>%s: </strong>", 
             itemtag="<li  id='%s.yj.md.html' onclick='changeContent(this)'>%s</li>",
             itemtagCollapse="<li  id='%s.yj.md.html' onclick='changeContent(this)' class='collapse'>%s</li>",
             valuetag="  %s", blocktag=('<ul>', '</ul>')):
    if isinstance(inpData, dict):
        k = '.files'
        if '.files' in inpData:
            htmlText.append(blocktag[0])
            v = inpData[k]
            pretty_items(htmlText, v)
            htmlText.append(blocktag[1])

        htmlText.append(blocktag[0])
        for k, v in inpData['dirs'].iteritems():
            if (k == '.files'):
                continue
            name = nametag % k
            if isinstance(v, dict):
                htmlText.append(itemtag % ( name, name) )
                pretty_items(htmlText, v)
            else:
                assert(0)
        htmlText.append(blocktag[1])
    elif isinstance(inpData, list):
        for i in inpData:
            if isinstance(i, dict) or isinstance(i, list):
                htmlText.append(itemtag % (" - ", " - " ) )
                pretty_items(htmlText, i)
            else:
                link = i.split('___')[-1]
                #htmlText.append(itemtagCollapse % ( i, link ) )
                htmlText.append(itemtag % ( i, link ) )
    return htmlText

# pretty_items is a tricky function. We need the list we pass to the function. But
# the pretty_items function uses recursion and hence cannot return it directly.
# So we hold a reference.
def formHtmlText( inpData ):
    reference = list()
    pretty_items( reference, inpData )
    print reference
    return '\n'.join(reference)

def createHtmlDivOfFiles( files ):
    print files
    rDict = formRecursiveDict( files )
    htmlDiv = formHtmlText( rDict )
    return htmlDiv

def createHomePage():
   files = findMdFilesInternal( '' )[ 'mdFiles' ]
   files.sort()
   htmlFile = HOST_DIR + 'pages/' + '/index.html'
   with open(APP_ROOT + "home_page_header.html") as f: 
       HOME_PAGE_HEADER = "".join( f.readlines() )
   with open(APP_ROOT + "home_page_trailer.html") as f: 
       HOME_PAGE_TRAILER = "".join( f.readlines() )
   with open( htmlFile, 'w' ) as homePage:
       homePage.write(HOME_PAGE_HEADER)
       lines = createHtmlDivOfFiles(files)
       homePage.write(lines)
       homePage.write(HOME_PAGE_TRAILER)


@app.route('/findMdFiles/<dirname>')
def findMdFiles( dirname ):
    resp = flask.jsonify( findMdFilesInternal )
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    return resp

@app.route('/getMdFile/<dirname>')
def getMdFile(dirname):
    resp = app.send_static_file("/Users/byj/Dropbox/dailyLog.yj.html")
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    return resp

@app.route('/path/<path:path>')
def static_proxy(path):
    if path.endswith(".html"):
        resp = flask.send_from_directory(HOST_DIR + 'pages/', path)
    else:
        resp = flask.send_from_directory(HOST_DIR, path)
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    return resp

def cleanup():
    pass

def init():
    DirsToCopy = ( CSS_DIR, IMG_DIR )
    for dir in DirsToCopy:
        command = "cp -r " + dir + ' ' + HOST_DIR
        p = subprocess.Popen(command, shell=True)
        p.wait()
    createHomePage()
   

@app.route('/init')
def initAndReturnIndex():
    init()
    return "Init Complete..."


if __name__ == '__main__':
    cleanup()
    init()
    app.run(debug=True)
