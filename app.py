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
 <title> BYJ Home Page </title >
<head> 
<link rel="stylesheet" type="text/css" href="/path/bootstrap/css/bootstrap.css"> 
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
<META HTTP-EQUIV="Expires" CONTENT="-1">
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

#listContainer{
  margin-top:15px;
}
 
#expList ul, li {
    list-style: none;
    margin:0;
    padding:0;
    cursor: pointer;
}
#expList p {
    margin:0;
    display:block;
}
#expList p:hover {
    background-color:#121212;
}
#expList li {
    line-height:140%;
    text-indent:0px;
    background-position: 1px 8px;
    padding-left: 20px;
    background-repeat: no-repeat;
}
 
/* Collapsed state for list element */

/*    background-image: url(../img/collapsed.png); */
#expList .collapsed {
    background-image: url(/path/images/collapsed.png);
}
/* Expanded state for list element
/* NOTE: This class must be located UNDER the collapsed one */
#expList .expanded {
    background-image: url(/path/images/expanded.png);
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
.highlight {color:red;}
</style>
</head>
<body>
<script src="/path/bootstrap/jquery/jquery.js"></script>
<script>

    function changeContent(object) { 
        console.log(object);
        //console.log(object.id);
        $('.highlight').removeClass('highlight');
        $(object).addClass('highlight');
        $.get("http://127.0.0.1:5000/path/".concat(object.id).concat("?rnd=seconds_since_epoch"), function(response) {
            $('#content').html(response);
        });
    } 
    function init() { 
        console.log("init");
/*
        $.get("http://127.0.0.1:5000/init", function(response) {
            $('#content').html(response);
        });
*/
        $.ajaxSetup({
            cache: false // Disable caching of AJAX responses
        });
    } 

function prepareList() {
    $('#expList').find('li:has(ul)').unbind('click').click(function(event) {
        if(this == event.target) {
            $(this).toggleClass('expanded');
            $(this).children('ul').toggle('medium');
        }
        return false;
    }).addClass('collapsed').removeClass('expanded').children('ul').hide();
 
    //Hack to add links inside the cv
    $('#expList a').unbind('click').click(function() {
        window.open($(this).attr('href'));
        return false;
    });
    //Create the button functionality
    $('#expandList').unbind('click').click(function() {
        $('.collapsed').addClass('expanded');
        $('.collapsed').children().show('medium');
    })
    $('#collapseList').unbind('click').click(function() {
        $('.collapsed').removeClass('expanded');
        $('.collapsed').children().hide('medium');
    })
};



$(document).ready(function() {
    changeContent("arista_commands.yj.md.html");
    prepareList();
}); 
</script>

<div id=leftBar>
<ul id="explist" >
<li  onClick="init()" >init</li>
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

def formRecursiveDict( names, separator='___' ):
    dictRoot = dict()
    for name in names:
        newDict = dictRoot
        nodes = name.split( separator )
        for node in nodes[ : -1 ]:
            if node not in newDict:
                newDict[node] = dict()
            newDict = newDict[node]
        if '.files' not in newDict:
            newDict['.files'] = list()
        newDict['.files'].append(name)
    return dictRoot

def pretty_items(htmlText, inpData, nametag="<strong>%s: </strong>", 
             itemtag="<li  id='%s.yj.md.html' onclick='changeContent(this)' >%s</li>",
             valuetag="  %s", blocktag=('<ul>', '</ul>')):
    print inpData
    if isinstance(inpData, dict):
        if '.files' not in inpData:
            htmlText.append(blocktag[0])
        for k, v in inpData.iteritems():
            name = nametag % k
            if isinstance(v, dict) or isinstance(v, list):
                if (k != '.files'):
                    htmlText.append(itemtag % ( name, name) )
                pretty_items(htmlText, v)
            else:
                value = valuetag % v
                htmlText.append(itemtag % (name + value, name + value ))
        if '.files' not in inpData:
            htmlText.append(blocktag[1])
    elif isinstance(inpData, list):
        htmlText.append(blocktag[0])
        for i in inpData:
            if isinstance(i, dict) or isinstance(i, list):
                htmlText.append(itemtag % (" - ", " - " ) )
                pretty_items(htmlText, i)
            else:
                link = i.split('___')[-1]
                htmlText.append(itemtag % ( i, link ) )
        htmlText.append(blocktag[1])
    return htmlText

def formHtmlText( inpData ):
    r = list()
    pretty_items( r, inpData )
    return '\n'.join(r)

def createHtmlDivOfFiles( files ):
    rDict = formRecursiveDict( files )
    htmlDiv = formHtmlText( rDict )
    return htmlDiv

def createHomePage():
   files = findMdFilesInternal( '' )[ 'mdFiles' ]
   files.sort()
   print files
   htmlFile = HOST_DIR + 'pages/' + '/index.html'
   with open( htmlFile, 'w' ) as homePage:
       homePage.write(HOME_PAGE_HEADER)
       lines = createHtmlDivOfFiles(files)
       homePage.write(lines)
       homePage.write(HOME_PAGE_TRAILER)

def createHomePage2():
   files = findMdFilesInternal( '' )[ 'mdFiles' ]
   files.sort()
   print files
   htmlFile = HOST_DIR + 'pages/' + '/index.html'
   with open( htmlFile, 'w' ) as homePage:
       homePage.write(HOME_PAGE_HEADER)
       for f in files:
           name = f.replace('___', ' ' )
           line = '<li  class="menuitem" id="' + f +  '.yj.md.html"' + \
                     'onClick="changeContent(this)" >' + name + '</li>\n'
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
