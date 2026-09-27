#Import libraries
from bs4 import BeautifulSoup
import json
import requests
from urllib.parse import urljoin
import os
import sys
from datetime import datetime, timedelta

HEADER = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}    

html_template = """<!DOCTYPE html>
<html>
<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chromium Commits - MetadataParser</title>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<style type="text/css">
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    text-align: center;
    color: white;
    margin-bottom: 30px;
}

.header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.header p {
    font-size: 1.1em;
    opacity: 0.9;
}

.slide-container {
    background: white;
    border-radius: 15px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
    min-height: 600px;
    display: flex;
    flex-direction: column;
}

.slide {
    display: none;
    padding: 40px;
    animation: fadeIn 0.5s ease-in;
    flex-grow: 1;
    overflow-y: auto;
}

.slide.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.slide-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 30px;
    border-bottom: 3px solid #667eea;
    padding-bottom: 20px;
}

.slide-title {
    font-size: 1.8em;
    color: #667eea;
    flex-grow: 1;
}

.slide-counter {
    background: #667eea;
    color: white;
    padding: 8px 16px;
    border-radius: 25px;
    font-weight: bold;
    white-space: nowrap;
}

.commit-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}

.info-box {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.info-label {
    font-weight: 600;
    color: #667eea;
    font-size: 0.9em;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.info-value {
    color: #333;
    word-break: break-all;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 0.95em;
}

.info-value a {
    color: #667eea;
    text-decoration: none;
}

.info-value a:hover {
    text-decoration: underline;
}

.message-box {
    background: #f0f4ff;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #764ba2;
    margin-bottom: 30px;
}

.message-label {
    font-weight: 600;
    color: #764ba2;
    font-size: 0.9em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.message-text {
    color: #333;
    line-height: 1.6;
}

.metadata-box {
    background: #e8f0ff;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin-bottom: 30px;
}

.metadata-label {
    font-weight: 600;
    color: #667eea;
    font-size: 0.9em;
    text-transform: uppercase;
    margin-bottom: 15px;
}

.metadata-content {
    background: white;
    padding: 15px;
    border-radius: 6px;
    max-height: 300px;
    overflow-y: auto;
    font-size: 0.9em;
    color: #333;
    line-height: 1.6;
}

.controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 20px 40px;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
}

.nav-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
}

.nav-btn:hover:not(:disabled) {
    background: #764ba2;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.nav-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.slide-input {
    display: flex;
    gap: 10px;
    align-items: center;
}

.slide-input input {
    width: 80px;
    padding: 10px;
    border: 2px solid #667eea;
    border-radius: 6px;
    font-size: 1em;
    text-align: center;
}

.slide-input input:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.slide-input button {
    background: #667eea;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.slide-input button:hover {
    background: #764ba2;
    transform: translateY(-2px);
}

.progress-bar {
    height: 4px;
    background: #e9ecef;
    position: relative;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    transition: width 0.3s ease;
}

.stats {
    text-align: center;
    color: white;
    margin-bottom: 20px;
    font-size: 0.95em;
}

dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 15px;
    margin-bottom: 10px;
}

dt {
    font-weight: 600;
    color: #667eea;
    padding-right: 10px;
}

dd {
    margin: 0;
    color: #333;
    word-break: break-word;
}

pre {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.85em;
    line-height: 1.4;
    color: #333;
}

@media (max-width: 768px) {
    .slide {
        padding: 20px;
    }
    
    .commit-info {
        grid-template-columns: 1fr;
    }
    
    .header h1 {
        font-size: 1.8em;
    }
    
    .controls {
        flex-wrap: wrap;
        padding: 15px 20px;
    }
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #764ba2;
}
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
    
    $('#next-btn').click(function() {
        if (currentSlide < totalSlides - 1) {
            currentSlide++;
            updateSlide();
        }
    });
    
    $('#prev-btn').click(function() {
        if (currentSlide > 0) {
            currentSlide--;
            updateSlide();
        }
    });
    
    $('#jump-btn').click(function() {
        const slideNum = parseInt($('#slide-input').val()) - 1;
        if (slideNum >= 0 && slideNum < totalSlides) {
            currentSlide = slideNum;
            updateSlide();
        }
    });
    
    $('#slide-input').keypress(function(e) {
        if (e.which === 13) {
            $('#jump-btn').click();
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
    """Parse Chromium timestamp format: 'Fri Sep 25 18:04:31 2026'"""
    try:
        return datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    except:
        return None

def get_commits_last_24h():
    """Fetch all commits from the last 24 hours."""
    print('FETCHING COMMITS FROM LAST 24 HOURS'.center(54, "-"), '\n')
    
    try:
        url = 'https://chromium.googlesource.com/chromium/src/+log?format=JSON&n=200'
        response = requests.get(url, headers=HEADER, timeout=30)
        response.raise_for_status()
        
        text = response.text
        if text.startswith(")]}'"):
            text = text[4:]
        
        data = json.loads(text)
        
        if 'log' not in data or len(data['log']) == 0:
            print('ERROR: No commits found in log')
            return []
        
        commits_24h = []
        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)
        
        print(f'Current time: {now.strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'24h cutoff: {cutoff_time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        print(f'Fetched {len(data["log"])} commits from API\n')
        
        for commit in data['log']:
            try:
                commit_time_str = commit.get('committer', {}).get('time', '')
                if commit_time_str:
                    commit_time = parse_commit_time(commit_time_str)
                    if commit_time:
                        commits_24h.append((commit_time, commit))
            except (ValueError, TypeError):
                continue
        
        commits_24h.sort(key=lambda x: x[0], reverse=True)
        commits_24h = [c for c in commits_24h if c[0] >= cutoff_time]
        commits_24h = [c[1] for c in commits_24h]
        
        print(f'Found {len(commits_24h)} commits in last 24 hours\n')
        return commits_24h
        
    except Exception as e:
        print(f'ERROR fetching commits: {e}')
        return []

def fetch_commit_metadata(git_sha):
    """Fetch MetadataParser content for a specific commit."""
    try:
        url = f'https://chromium.googlesource.com/chromium/src/+/{git_sha}'
        response = requests.get(url, headers=HEADER, timeout=15)
        response.raise_for_status()
        
        content = BeautifulSoup(response.content, "html.parser")
        
        MetadataParser = content.find_all("div", {"class": "Metadata"})
        PreMMsg = content.find_all("pre", {"class": "MetadataMessage"})
        
        metadata_content = ""
        if MetadataParser:
            try:
                MTAB_P = MetadataParser[0].find("dl")
                if MTAB_P:
                    base_url = "https://chromium.googlesource.com/"
                    for a_tag in MTAB_P.find_all('a', href=True):
                        a_tag['href'] = urljoin(base_url, a_tag['href'])
                    
                    metadata_content = MTAB_P.prettify()
                    
                    if PreMMsg:
                        metadata_content += "<hr/>" + PreMMsg[0].prettify()
            except IndexError:
                pass
        
        return metadata_content if metadata_content else "<p>No metadata found</p>"
        
    except Exception as e:
        return f"<p>Error fetching metadata: {e}</p>"

# Main execution
print('SUMMARY'.center(54, "-"), '\n')

commits = get_commits_last_24h()

if not commits:
    print('Fetching recent commits instead...\n')
    try:
        url = 'https://chromium.googlesource.com/chromium/src/+log?format=JSON&n=50'
        response = requests.get(url, headers=HEADER, timeout=30)
        text = response.text
        if text.startswith(")]}'"):
            text = text[4:]
        data = json.loads(text)
        commits = data.get('log', [])[:50]
        print(f'Showing {len(commits)} recent commits:\n')
    except:
        commits = []

if not commits:
    print('No commits found')
else:
    print(f'Generating modern slider page with {len(commits)} commits...\n')
    
    os.makedirs('docs', exist_ok=True)
    
    page_content = f"""
<div class="container">
    <div class="progress-bar">
        <div class="progress-fill"></div>
    </div>
    
    <div class="stats">
        <strong>Chromium Commits • MetadataParser • Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong>
    </div>
    
    <div class="header">
        <h1>🔍 Chromium Commits</h1>
        <p>Browse {len(commits)} recent commits with full metadata</p>
    </div>
    
    <div class="slide-container">
"""
    
    for idx, commit in enumerate(commits):
        git_sha = commit.get('commit', 'unknown')
        author = commit.get('author', {})
        committer = commit.get('committer', {})
        message = commit.get('message', 'No message')
        timestamp = committer.get('time', '')
        
        commit_time = parse_commit_time(timestamp)
        if commit_time:
            commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            commit_time_str = timestamp
        
        message_first_line = message.split('\n')[0] if message else 'No message'
        message_full = message.replace('<', '&lt;').replace('>', '&gt;')
        
        print(f'[{idx + 1}/{len(commits)}] Fetching metadata for {git_sha[:12]}...')
        metadata_html = fetch_commit_metadata(git_sha)
        
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
                <div class="message-label">📝 Commit Message (First Line)</div>
                <div class="message-text">{message_first_line}</div>
            </div>
            
            <div class="metadata-box">
                <div class="metadata-label">📋 Metadata</div>
                <div class="metadata-content">
                    {metadata_html}
                </div>
            </div>
        </div>
"""
    
    page_content += """
        <div class="controls">
            <button id="prev-btn" class="nav-btn">← Previous</button>
            <div class="slide-input">
                <input type="number" id="slide-input" min="1" max="{}" placeholder="Go to">
                <button id="jump-btn" class="nav-btn">Jump</button>
            </div>
            <button id="next-btn" class="nav-btn">Next →</button>
        </div>
    </div>
</div>
""".format(len(commits))
    
    # Write single page
    with open('docs/index.html', 'w', encoding='utf8') as f:
        f.write(html_template + page_content + endLine)
    
    print(f"\n[OK] Generated modern slider with {len(commits)} commits")
    print(f"[OK] Output: docs/index.html")
    print(f"\nFeatures:")
    print(f"   - Arrow buttons or keyboard arrows to navigate")
    print(f"   - Jump to specific commit by number")
    print(f"   - Progress bar shows your position")
    print(f"   - Responsive design for mobile & desktop")
    print(f"   - No external CSS dependency")
    print(f"   - Modern gradient UI with smooth animations")
    print(f"   - jQuery-powered interactive slider")
