from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from bs4 import BeautifulSoup
import json
import httpx
import asyncio
from urllib.parse import urljoin
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

html_template = """<!DOCTYPE html>
<html>
<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chromium Commits - MetadataParser</title>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<style type="text/css">
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}
.container { max-width: 1200px; margin: 0 auto; }
.header { text-align: center; color: white; margin-bottom: 30px; }
.header h1 { font-size: 2.5em; margin-bottom: 10px; }
.slide-container {
    background: white;
    border-radius: 15px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
    min-height: 500px;
    display: flex;
    flex-direction: column;
}
.slide { display: none; padding: 40px; flex-grow: 1; overflow-y: auto; }
.slide.active { display: block; }
.slide-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    border-bottom: 3px solid #667eea;
    padding-bottom: 15px;
}
.slide-title { font-size: 1.8em; color: #667eea; }
.slide-counter { background: #667eea; color: white; padding: 8px 16px; border-radius: 25px; font-weight: bold; }
.commit-info { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
.info-box { background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea; }
.info-label { font-weight: 600; color: #667eea; font-size: 0.85em; text-transform: uppercase; }
.info-value { color: #333; font-family: monospace; }
.message-box { background: #f0f4ff; padding: 15px; border-radius: 8px; border-left: 4px solid #764ba2; margin-bottom: 20px; }
.metadata-box { background: #e8f0ff; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }
.metadata-content { background: white; padding: 12px; border-radius: 6px; max-height: 250px; overflow-y: auto; font-size: 0.85em; }
.controls { display: flex; justify-content: center; align-items: center; gap: 15px; padding: 15px; background: #f8f9fa; border-top: 1px solid #e9ecef; }
.nav-btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.nav-btn:hover:not(:disabled) { background: #764ba2; }
.nav-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.progress-bar { height: 4px; background: #e9ecef; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.3s ease; }
.stats { text-align: center; color: white; margin-bottom: 15px; font-size: 0.9em; }
dl { display: grid; grid-template-columns: auto 1fr; gap: 10px; }
dt { font-weight: bold; color: #667eea; }
</style>
</head>
<body>
"""

endLine = """
<script>
$(document).ready(function() {
    let currentSlide = 0;
    const totalSlides = $('.slide').length;
    
    function updateSlide() {
        $('.slide').removeClass('active');
        $('.slide').eq(currentSlide).addClass('active');
        $('#prev-btn').prop('disabled', currentSlide === 0);
        $('#next-btn').prop('disabled', currentSlide === totalSlides - 1);
        const progress = ((currentSlide + 1) / totalSlides) * 100;
        $('.progress-fill').css('width', progress + '%');
        $('#slide-counter').text('Commit ' + (currentSlide + 1) + ' of ' + totalSlides);
    }
    
    $('#next-btn').click(function() { if (currentSlide < totalSlides - 1) { currentSlide++; updateSlide(); } });
    $('#prev-btn').click(function() { if (currentSlide > 0) { currentSlide--; updateSlide(); } });
    
    $('#jump-btn').click(function() {
        const slideNum = parseInt($('#slide-input').val()) - 1;
        if (slideNum >= 0 && slideNum < totalSlides) {
            currentSlide = slideNum;
            updateSlide();
        }
    });
    
    $(document).keydown(function(e) {
        if (e.keyCode === 37) $('#prev-btn').click();
        if (e.keyCode === 39) $('#next-btn').click();
    });
    
    updateSlide();
});
</script>
</body>
</html>
"""

def parse_commit_time(time_str):
    try:
        return datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    except Exception:
        return None

async def fetch_commit_metadata_async(client, git_sha):
    try:
        url = f'https://chromium.googlesource.com/chromium/src/+/{git_sha}'
        response = await client.get(url, headers=HEADER, timeout=3.0)
        content = BeautifulSoup(response.content, "html.parser")
        
        MetadataParser = content.find_all("div", {"class": "Metadata"})
        PreMMsg = content.find_all("pre", {"class": "MetadataMessage"})
        
        metadata_content = ""
        if MetadataParser:
            MTAB_P = MetadataParser[0].find("dl")
            if MTAB_P:
                base_url = "https://chromium.googlesource.com/"
                for a_tag in MTAB_P.find_all('a', href=True):
                    a_tag['href'] = urljoin(base_url, a_tag['href'])
                metadata_content = MTAB_P.prettify()
                if PreMMsg:
                    metadata_content += "<hr/>" + PreMMsg[0].prettify()
        
        return metadata_content if metadata_content else "<p>No metadata found</p>"
    except Exception as e:
        return f"<p>Error fetching metadata: {e}</p>"

@app.get("/", response_class=HTMLResponse)
@app.get("/api/cron", response_class=HTMLResponse)
async def generate_page():
    async with httpx.AsyncClient(verify=False) as client:
        try:
            url = 'https://chromium.googlesource.com/chromium/src/+log?format=JSON&n=50'
            response = await client.get(url, headers=HEADER, timeout=5.0)
            text = response.text
            if text.startswith(")]}'"):
                text = text[4:]
            data = json.loads(text)
            commits = data.get('log', [])[:50]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching log: {e}")

        if not commits:
            raise HTTPException(status_code=404, detail="No commits found")

        tasks = [fetch_commit_metadata_async(client, commit.get('commit', '')) for commit in commits]
        metadata_results = await asyncio.gather(*tasks)

    page_content = f"""
<div class="container">
    <div class="progress-bar">
        <div class="progress-fill"></div>
    </div>
    
    <div class="stats">
        <strong>Chromium Commits • Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong>
    </div>
    
    <div class="header">
        <h1>🔍 Chromium Commits</h1>
        <p>Browse {len(commits)} recent commits with full metadata</p>
    </div>
    
    <div class="slide-container">
"""

    for idx, (commit, metadata_html) in enumerate(zip(commits, metadata_results)):
        git_sha = commit.get('commit', 'unknown')
        author = commit.get('author', {})
        committer = commit.get('committer', {})
        message = commit.get('message', 'No message')
        timestamp = committer.get('time', '')
        
        commit_time = parse_commit_time(timestamp)
        commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S") if commit_time else timestamp
        message_first_line = message.split('\n')[0] if message else 'No message'
        
        page_content += f"""
        <div class="slide">
            <div class="slide-header">
                <div class="slide-title">
                    <a href="https://chromium.googlesource.com/chromium/src/+/{git_sha}" target="_blank">
                        {git_sha[:12]}
                    </a>
                </div>
                <div class="slide-counter" id="slide-counter">Commit {idx + 1} of {len(commits)}</div>
            </div>
            
            <div class="commit-info">
                <div class="info-box">
                    <div class="info-label">Author</div>
                    <div class="info-value">{author.get('name', 'Unknown')}</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Committer</div>
                    <div class="info-value">{committer.get('name', 'Unknown')}</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Timestamp</div>
                    <div class="info-value">{commit_time_str}</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Repository</div>
                    <div class="info-value">chromium/src</div>
                </div>
            </div>
            
            <div class="message-box">
                <div class="info-label">📝 Commit Message</div>
                <div class="info-value" style="font-family: inherit;">{message_first_line}</div>
            </div>
            
            <div class="metadata-box">
                <div class="info-label">📋 Metadata</div>
                <div class="metadata-content">
                    {metadata_html}
                </div>
            </div>
        </div>
"""

    page_content += f"""
        <div class="controls">
            <button id="prev-btn" class="nav-btn">← Previous</button>
            <div class="slide-input" style="display:flex; gap:5px;">
                <input type="number" id="slide-input" min="1" max="{len(commits)}" placeholder="Go to" style="width:60px; text-align:center;">
                <button id="jump-btn" class="nav-btn">Jump</button>
            </div>
            <button id="next-btn" class="nav-btn">Next →</button>
        </div>
    </div>
</div>"""

    full_html = html_template + page_content + endLine
    return HTMLResponse(content=full_html)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
