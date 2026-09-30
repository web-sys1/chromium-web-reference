from flask import Flask
from bs4 import BeautifulSoup
import json
import requests
from urllib.parse import urljoin
import os
import sys
from main import *
from datetime import datetime, timedelta

app = Flask(__name__)

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

html_template = """<!DOCTYPE html>...""" 
endLine = """..."""                      


@app.route("/")
@app.route("/api/cron")
def generate_page():
    commits = get_commits_last_24h()

    if not commits:
        try:
            url = 'https://chromium.googlesource.com/chromium/src/+log?format=JSON&n=50'
            response = requests.get(url, headers=HEADER, timeout=30)
            text = response.text
            if text.startswith(")]}'"):
                text = text[4:]
            data = json.loads(text)
            commits = data.get('log', [])[:50]
        except:
            commits = []

    if not commits:
        return "<h1>No commits found</h1>", 404

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
        commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S") if commit_time else timestamp
        
        message_first_line = message.split('\n')[0] if message else 'No message'
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

    page_content += f"""
        <div class="controls">
            <button id="prev-btn" class="nav-btn">← Previous</button>
            <div class="slide-input">
                <input type="number" id="slide-input" min="1" max="{len(commits)}" placeholder="Go to">
                <button id="jump-btn" class="nav-btn">Jump</button>
            </div>
            <button id="next-btn" class="nav-btn">Next →</button>
        </div>
    </div>
</div>"""

    full_html = html_template + page_content + endLine
    return full_html

if __name__ == "__main__":
    app.run(debug=True)
