# Chromium Commits MetadataParser

A modern, interactive web-based viewer for Chromium repository commits with full metadata extraction and display.

## Features

✨ **Modern Interactive Slider**
- Navigate through commits with Previous/Next buttons
- Keyboard arrow keys for quick navigation
- Jump to specific commit by number
- Progress bar showing your position
- Smooth fade-in animations

📋 **Complete MetadataParser**
- Fetches all commit metadata from Chromium Git
- Displays author, committer, timestamp, and full commit messages
- Extracts metadata from each commit page
- No deprecated appspot API (removed)

🎨 **Modern UI/UX**
- Gradient background with vibrant colors
- Responsive design for desktop and mobile
- Embedded styling (no external CSS dependencies)
- jQuery for smooth interactions
- Professional color scheme and typography

⚡ **Efficient Processing**
- Fetches 50 recent commits (or last 24 hours if available)
- Generates single optimized HTML file
- Parallel metadata extraction
- Fast page loads and smooth navigation

## Requirements

```bash
pip install requests beautifulsoup4
```

## Usage

### Basic Run

```bash
python main.py
```

This will:
1. Fetch the 50 most recent commits from Chromium repository
2. Extract metadata for each commit
3. Generate `docs/index.html` with all commits

### Output

- **docs/index.html** - Modern interactive slider page with all commits and metadata

## Navigation

Once you open `docs/index.html` in a browser:

- **Next/Previous buttons** - Navigate between commits
- **Arrow keys** - Use left/right arrows on keyboard for quick navigation
- **Jump input** - Enter a commit number (1-50) and click "Jump" to go to that commit
- **Progress bar** - Visual indicator of your position
- **Click commit SHA** - Opens the Chromium Git page for that commit

## How It Works

1. **Fetch commits** - Queries the Chromium Git JSON API for recent commits
2. **Extract metadata** - For each commit, fetches the Chromium Git page and parses the MetadataParser HTML
3. **Build slides** - Creates interactive slides with commit details and metadata
4. **Generate HTML** - Outputs a single self-contained HTML file with all styling and JavaScript

## Structure

### main.py Functions

- `parse_commit_time()` - Parses Chromium timestamp format
- `get_commits_last_24h()` - Fetches recent commits from Chromium Git
- `fetch_commit_metadata()` - Extracts metadata for a specific commit
- HTML template with embedded CSS and jQuery

### Generated HTML

Each slide contains:
- **Commit SHA** - Full commit hash with link to Chromium Git
- **Author/Committer** - Names and emails
- **Timestamp** - When the commit was made
- **Repository** - Always chromium/src
- **Commit Message** - First line of the message
- **Metadata** - Full parsed metadata from the Chromium page

## API Used

- `https://chromium.googlesource.com/chromium/src/+log?format=JSON` - Commit log (JSON API)
- `https://chromium.googlesource.com/chromium/src/+/{sha}` - Individual commit page (parsed for metadata)

No deprecated APIs (appspot removed).

## Browser Compatibility

- Chrome/Chromium 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Responsive Design

- **Desktop** - Full two-column info layout with large fonts
- **Tablet** - Single column layout, adjusted spacing
- **Mobile** - Optimized for small screens, touch-friendly buttons

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ← | Previous commit |
| → | Next commit |
| Enter (in jump field) | Jump to commit number |

## Performance

- Single HTML file (no external dependencies except jQuery)
- Smooth animations with CSS transitions
- Progress bar updates in real-time
- Metadata box scrollable for long content

## Customization

Edit `main.py` to modify:

- **Number of commits** - Change `n=50` to different value
- **Styling** - Edit CSS section in `html_template`
- **Colors** - Modify `#667eea` (blue) and `#764ba2` (purple) hex codes
- **Animations** - Adjust timing in `@keyframes fadeIn`

## License

This tool fetches publicly available data from the Chromium repository and is for informational purposes only.

## Troubleshooting

### No commits found

If no commits are found in the last 24 hours, the script automatically falls back to the 50 most recent commits.

### Metadata parsing errors

If metadata extraction fails for a specific commit, the slide will show "No metadata found" but the commit details will still display.

### Browser shows blank page

Ensure JavaScript is enabled and jQuery CDN is accessible from your network.

## Future Enhancements

- [ ] Search/filter commits by author
- [ ] Export to CSV
- [ ] Dark mode toggle
- [ ] Local storage to remember last viewed commit
- [ ] Download individual commit metadata as JSON
- [ ] Commit diff viewer integration

---

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Author:** Chromium MetadataParser Tool

**Repository:** https://chromium.googlesource.com/chromium/src
