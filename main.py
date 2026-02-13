#Import libraries
from bs4 import BeautifulSoup
import json
import requests

HEADER = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}    

REV_CHG_URL = [requests.get('https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Mac%2FLAST_CHANGE?alt=media', headers = HEADER), requests.get('https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2FLAST_CHANGE?alt=media', headers = HEADER)]
CURRENT_REVISION_NO = [REV_CHG_URL[0].text, REV_CHG_URL[1].text]

begin = """<!DOCTYPE html>
<html>
<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<link href="https://chromium.googlesource.com/+static/base.css" rel="stylesheet"/>
<base href="https://chromium.googlesource.com/">
<style type="text/css">
table.blueTable {
  border: 1px solid #1C6EA4;
  background-color: #EEEEEE;
  width: 100%;
  text-align: center;
  border-collapse: collapse;
}
table.blueTable td, table.blueTable th {
  border: 1px solid #AAAAAA;
  padding: 3px 2px;
}
table.blueTable tbody td {
  font-size: 16px;
}
table.blueTable tr:nth-child(even) {
  background: #D0E4F5;
}
table.blueTable thead {
  background: #3077A4;
  background: -moz-linear-gradient(top, #6499bb 0%, #4484ad 66%, #3077A4 100%);
  background: -webkit-linear-gradient(top, #6499bb 0%, #4484ad 66%, #3077A4 100%);
  background: linear-gradient(to bottom, #6499bb 0%, #4484ad 66%, #3077A4 100%);
  border-bottom: 2px solid #444444;
}
table.blueTable thead th {
  font-size: 15px;
  font-weight: bold;
  color: #FFFFFF;
  text-align: center;
  border-left: 2px solid #D0E4F5;
}
table.blueTable thead th:first-child {
  border-left: none;
}
table.blueTable tfoot {
  font-size: 8px;
  font-weight: bold;
  color: #FFFFFF;
  background: #D0E4F5;
  background: -moz-linear-gradient(top, #dcebf7 0%, #d4e6f6 66%, #D0E4F5 100%);
  background: -webkit-linear-gradient(top, #dcebf7 0%, #d4e6f6 66%, #D0E4F5 100%);
  background: linear-gradient(to bottom, #dcebf7 0%, #d4e6f6 66%, #D0E4F5 100%);
  border-top: 2px solid #444444;
}
table.blueTable tfoot td {
  font-size: 8px;
}
table.blueTable tfoot .links {
  text-align: right;
}
table.blueTable tfoot .links a{
  display: inline-block;
  background: #1C6EA4;
  color: #FFFFFF;
  padding: 2px 8px;
  border-radius: 5px;
}
body{
    background: #fff2e0;
}
.Metadata {
    margin-bottom: 15px;
}
.u-monospace {
    font-family: 'Source Code Pro',monospace;
    max-width: 100%;
    overflow-x: scroll;
    border: groove #c33b3b 2px;
}
.MetadataMessage {
    background-color: #b9caff;
    border: 1px solid #de5353;
    color: #000;
    margin: 0;
    padding: 12px;
    white-space: pre-wrap;
}
</style>
</head>
<body>
"""

endLine = """
</body>
</html>
"""

def main():
    CR_REV_G = [requests.get('https://cr-rev.appspot.com/_ah/api/crrev/v1/redirect/' + CURRENT_REVISION_NO[0]), requests.get('https://cr-rev.appspot.com/_ah/api/crrev/v1/redirect/' + CURRENT_REVISION_NO[1])]
    CR_IDENTIFIER = json.loads(CR_REV_G[0].text)
    CR_IDENTIFIER_WIN = json.loads(CR_REV_G[1].text)
    
    try:
      r = requests.get(CR_IDENTIFIER['redirect_url'])
    except:
      r = requests.get(CR_IDENTIFIER['redirectUrl'])
      
    content = BeautifulSoup(r.content, "html.parser")
    
    print('SUMMARY'.center(54, "-"), '\n')
    print('REVISION NO. ' + CURRENT_REVISION_NO[0])
    title = content.title.string
    print('PAGE TITLE: ', title)
    print('SHA-1 COMMIT NO.: ', CR_IDENTIFIER['git_sha'])
    
    GIT_SHA1 = [CR_IDENTIFIER['git_sha'], CR_IDENTIFIER_WIN['git_sha']]
    
    ContentSummary = f"""
    <table class="blueTable">
     <thead>
      <tr>
       <th><strong>REVISION ID</strong></th>
       <th>SHA-1 COMMIT</th>
      </tr>
    </thead>
    <tfoot></tfoot>
     <tbody>
      <tr>
       <td><a href ="https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Mac/{CURRENT_REVISION_NO[0]}/"> {CURRENT_REVISION_NO[0]}</a> <sup><b>(MAC)</b></sup></td>
       <td><a href="https://chromium.googlesource.com/chromium/src/+/{GIT_SHA1[0]}">{GIT_SHA1[0]}</a></td>
      </tr>
      <tr>
       <td><a href ="https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Win/{CURRENT_REVISION_NO[1]}/">{CURRENT_REVISION_NO[1]}</a> <sup><b>(WIN)</b></sup></td>
       <td><a href="https://chromium.googlesource.com/chromium/src/+/{GIT_SHA1[1]}">{GIT_SHA1[1]}</a></td>
     </tbody>
    </table>
   <hr>"""
    HR_BREAKPOINT= f"""<hr style="height:1px;border-width:0;color:gray;background-color:gray">"""
    MetadataParser = content.find_all("div", {"class" : "Metadata"})
    PreMMsg = content.find_all("pre", {"class" : "MetadataMessage"})

    MTAB_P = MetadataParser[0].find("dl")
    METADATA_FT = MTAB_P()
    MTAB_RES = ContentSummary + MTAB_P.prettify() + HR_BREAKPOINT + PreMMsg[0].prettify()
    
    for tag in PreMMsg:
        if 'class' in tag.attrs.keys() and tag.attrs['class'][0].strip():
            print('CLASS ORIGINS :', tag.attrs['class'], '\n\n')
            print('METADATA'.center(54, "-"), '\n')
            print(METADATA_FT[1].text, ':' + '', METADATA_FT[2].text)
            print(METADATA_FT[9].text, ':' + '', METADATA_FT[10].text, METADATA_FT[11].text)
            print(METADATA_FT[13].text, ':' + '', METADATA_FT[14].text, METADATA_FT[15].text)
            print(METADATA_FT[17].text, ':' + '', METADATA_FT[18].text)
            print(METADATA_FT[21].text, ':' + '', METADATA_FT[23].text + '\n\n')
            print('DETAILS'.center(54, "-"), '\n')
            print(PreMMsg[0].text)
            
    with open(f'docs/index.html', 'w', encoding='utf8') as f:
       content = begin + MTAB_RES + endLine
       f.write(content)
    
if __name__ == '__main__':
    main()
