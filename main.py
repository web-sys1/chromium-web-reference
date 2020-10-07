from bs4 import BeautifulSoup
import json
import requests

HEADER = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}    

REV_CHG_URL = requests.get('https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Mac%2FLAST_CHANGE?alt=media', headers = HEADER)
CURRENT_REVISION_NO = REV_CHG_URL.text

top = """
<!DOCTYPE html>
<html>
<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<base href="https://chromium.googlesource.com/">
<style type="text/css">
.Metadata {
    margin-bottom: 15px;
}
.u-monospace {
    font-family: 'Source Code Pro',monospace;
}
.MetadataMessage {
    background-color: #fafafa;
    border: 1px solid #ccc;
    color: #000;
    margin: 0;
    padding: 12px;
    white-space: pre-wrap;
}
</style>
</head>
<body>
"""
bottom = """
</body>
</html>
"""

def main():
    CR_REV_G = requests.get('https://cr-rev.appspot.com/_ah/api/crrev/v1/redirect/' + CURRENT_REVISION_NO)
    CR_IDENTIFIER = json.loads(CR_REV_G.text)
    r = requests.get(CR_IDENTIFIER['redirect_url'])
    content = BeautifulSoup(r.content, "html.parser")
    print('SUMMARY'.center(54, "-"), '\n')
    print('REVISION NO. ' + CURRENT_REVISION_NO)
    title = content.title.string
    print('PAGE TITLE: ', title)
    print('SHA-1 COMMIT NO.: ', CR_IDENTIFIER['git_sha'])

    MetadataParser = content.find_all("div", {"class" : "Metadata"})
    PreMMsg = content.find_all("pre", {"class" : "MetadataMessage"})

    MTAB_P = MetadataParser[0].find("table")
    METADATA_FT = MTAB_P()
    MTAB_RES = MTAB_P.prettify() + PreMMsg[0].prettify()
    
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
            
    with open(f'index.html', 'w', encoding='utf8') as f:
       content = top + MTAB_RES + bottom
       return f.write(content)
    
if __name__ == '__main__':
    main()
    
