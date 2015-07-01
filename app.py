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
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
HOST_DIR = os.getenv('HOME') + '/website/'
BASE_DIR = os.getenv('HOME') + '/Dropbox/'
CSS_DIR = BASE_DIR + 'Sites/bootstrap' 
IMG_DIR = BASE_DIR + 'Sites/images' 
MARKDOWN = BASE_DIR + 'Markdown.pl'

HOME_PAGE_HEADER = """
<!doctype html>
 <title> BYJ </title >
<head> 
<link rel="stylesheet" type="text/css" href="/path/bootstrap/css/bootstrap.css"> 
<style>
.box {
    margin: 0px;
}
#leftBar {
    width: 18%;
    display: inline-block;
    vertical-align: top;
}
#content {
    width: 80%;
    display: inline-block;
    vertical-align: top;
}

#navbar {
  display: block;
  list-style-type: none;
}
 
.menuitem {
    list-style-type:   none;
    display:           inline-block;
    width:             150px;
    margin-left:       5px;
    margin-right:      5px;
    font-family:       Georgia;
    font-size:         11px;
    background-color:  #c0dbf1;
    border:            1px solid black;
    padding:           0;    
}
.menuitem:hover {
    background-color:        #8bb3d4;
}

</style>
</head>
<body>
<script src="/path/bootstrap/jquery/jquery.js"></script>
<script>
    function changeContent(file) { 
        console.log(file);
        $.get("http://127.0.0.1:5000/path/".concat(file).concat("?rnd=seconds_since_epoch"), function(response) {
            $('#content').html(response);
        });
    } 
    function init() { 
        console.log("init");
        $.get("http://127.0.0.1:5000/init", function(response) {
            $('#content').html(response);
        });
    } 
$(document).ready(function() {
    //changeContent("arista_commands.yj.md.html");
}); 
</script>

<div id=leftBar>
<ul id="navbar" >
<li  class="menuitem" onClick="init()" >init</li>
"""
HOME_PAGE_TRAILER = """
</ul>
<br></p>
</div>
<div id=content class='top'>
<h3>Home Page</h3>
</div>
</body>
"""

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

def createHomePage():
   files = findMdFilesInternal( '' )[ 'mdFiles' ]
   files.sort()
   print files
   htmlFile = HOST_DIR + 'pages/' + '/index.html'
   with open( htmlFile, 'w' ) as homePage:
       homePage.write(HOME_PAGE_HEADER)
       for f in files:
           name = f.replace('___', ' ' )
           line = '<li  class="menuitem" id="' + f +  '.yj.md.html"' + \
                     'onClick="changeContent(this.id)" >' + name + '</li>\n'
           homePage.write(line)
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
