import os
import sys
import mimetypes
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote

PORT = 8080
DIRECTORY = '/sdcard/Download'

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
SERVER_URL = f"http://{LOCAL_IP}:{PORT}"

class VaultStudioEngine(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = unquote(self.path.split('?')[0])
        
        if url_path == '/':
            self.send_dashboard()
            return
            
        if url_path.startswith('/stream/'):
            filename = url_path[8:]
            file_path = os.path.join(DIRECTORY, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.stream_file(file_path)
            else:
                self.send_error(404, "File Not Found")
            return

        self.send_error(404, "Endpoint Not Found")

    def send_dashboard(self):
        try:
            all_entries = os.listdir(DIRECTORY)
            files = [
                f for f in all_entries 
                if os.path.isfile(os.path.join(DIRECTORY, f)) and not f.startswith('.')
            ]
        except Exception:
            files = []
        
        stats = {'video': 0, 'audio': 0, 'image': 0, 'document': 0}
        total_size_bytes = 0
        cards_html = ""
        featured_media_src = ""
        featured_media_title = "Select any media below to play"
        featured_type = "video"

        for f in files:
            file_path = os.path.join(DIRECTORY, f)
            size_bytes = os.path.getsize(file_path)
            total_size_bytes += size_bytes
            size_mb = size_bytes / (1024 * 1024)
            ext = os.path.splitext(f)[1].lower()
            stream_url = f"/stream/{f}"
            
            if ext in ['.mp4', '.mkv', '.webm', '.mov']:
                category = "video"
                stats['video'] += 1
                icon = "🎬"
                badge_class = "badge-video"
                if not featured_media_src:
                    featured_media_src = stream_url
                    featured_media_title = f
                    featured_type = "video"
                action_content = f'<button class="action-btn" onclick="playMedia(\'{stream_url}\', \'{f}\', \'video\')">▶ Play Video</button>'
            elif ext in ['.mp3', '.wav', '.ogg']:
                category = "audio"
                stats['audio'] += 1
                icon = "🎵"
                badge_class = "badge-audio"
                if not featured_media_src:
                    featured_media_src = stream_url
                    featured_media_title = f
                    featured_type = "audio"
                action_content = f'<button class="action-btn" onclick="playMedia(\'{stream_url}\', \'{f}\', \'audio\')">🎵 Play Audio</button>'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                category = "image"
                stats['image'] += 1
                icon = "🖼️"
                badge_class = "badge-image"
                action_content = f'<div class="img-preview"><img src="{stream_url}" alt="{f}"></div>'
            else:
                category = "document"
                stats['document'] += 1
                icon = "📄"
                badge_class = "badge-doc"
                action_content = f'<a href="{stream_url}" class="action-btn btn-download" target="_blank">📥 Download File</a>'
            
            cards_html += f'''
            <div class="file-card" data-filename="{f.lower()}" data-category="{category}">
                <div class="card-top">
                    <div class="icon-box">{icon}</div>
                    <div class="file-info">
                        <div class="file-title">{f}</div>
                        <div class="file-meta">
                            <span>{size_mb:.2f} MB</span>
                            <span class="badge {badge_class}">{category.upper()}</span>
                        </div>
                    </div>
                </div>
                <div class="card-action">
                    {action_content}
                </div>
            </div>
            '''

        total_mb = total_size_bytes / (1024 * 1024)
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={SERVER_URL}"

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vault Studio UI</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            padding: 15px 15px 40px 15px;
            max-width: 650px;
            margin: 0 auto;
        }}

        .app-header {{
            display: flex; align-items: center; justify-content: space-between;
            background: #1e293b; padding: 12px 18px; border-radius: 18px;
            border: 1px solid #334155; margin-bottom: 16px;
        }}
        .brand-logo {{
            display: flex; align-items: center; gap: 12px;
        }}
        .logo-icon {{
            width: 42px; height: 42px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            border-radius: 12px; display: flex; align-items: center;
            justify-content: center; font-size: 1.4rem; font-weight: bold;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }}
        .brand-text {{
            display: flex; flex-direction: column;
        }}
        .brand-name {{
            font-size: 1.1rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.5px;
        }}
        .brand-tag {{
            font-size: 0.7rem; color: #94a3b8; font-weight: 500;
        }}
        .status-badge {{
            background: rgba(34, 197, 94, 0.15); color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700;
        }}

        .search-wrapper {{
            display: flex; align-items: center;
            background: #1e293b;
            padding: 12px 18px; border-radius: 16px;
            border: 1px solid #334155;
            margin-bottom: 16px;
        }}
        .search-input {{
            width: 100%; border: none; background: transparent;
            outline: none; color: #f8fafc; font-size: 0.95rem; margin: 0 10px;
        }}
        .search-input::placeholder {{ color: #64748b; }}
        .icon {{ color: #94a3b8; font-size: 1.1rem; }}

        .filter-tags {{
            display: flex; gap: 8px; overflow-x: auto;
            padding-bottom: 8px; margin-bottom: 20px; scrollbar-width: none;
        }}
        .filter-tags::-webkit-scrollbar {{ display: none; }}
        
        .tag-btn {{
            background: #1e293b; border: 1px solid #334155; color: #94a3b8;
            padding: 8px 18px; border-radius: 20px; cursor: pointer;
            font-size: 0.82rem; font-weight: 600; white-space: nowrap; transition: 0.2s;
        }}
        .tag-btn.active {{
            background: #2563eb; color: #ffffff; border-color: #3b82f6;
        }}

        .featured-frame {{
            background: #1e293b; border-radius: 20px; padding: 14px;
            border: 1px solid #334155; margin-bottom: 20px;
        }}
        .player-wrapper {{
            width: 100%; aspect-ratio: 16/9; background: #0f172a;
            border-radius: 14px; overflow: hidden; display: flex; flex-direction: column;
            align-items: center; justify-content: center; position: relative;
        }}
        video#featuredVideo {{ width: 100%; height: 100%; outline: none; }}
        audio#featuredAudio {{ width: 90%; outline: none; margin-top: 15px; }}

        .audio-visualizer {{
            display: none; align-items: flex-end; gap: 6px; height: 50px; margin-bottom: 10px;
        }}
        .bar {{ width: 8px; background: #3b82f6; border-radius: 4px; animation: pulse 1s infinite alternate; }}
        .bar:nth-child(2) {{ animation-delay: 0.2s; height: 35px; }}
        .bar:nth-child(3) {{ animation-delay: 0.4s; height: 50px; }}
        .bar:nth-child(4) {{ animation-delay: 0.1s; height: 25px; }}
        @keyframes pulse {{ 0% {{ height: 10px; }} 100% {{ height: 45px; }} }}

        .player-controls-bar {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 4px 2px 4px;
        }}
        .featured-title {{
            color: #f8fafc; font-size: 0.88rem; font-weight: 600;
            word-break: break-all; flex-grow: 1; margin-right: 10px;
        }}
        .next-btn {{
            background: #334155; color: #ffffff; border: none;
            padding: 8px 16px; border-radius: 20px; font-weight: 600;
            font-size: 0.82rem; cursor: pointer; transition: 0.2s; flex-shrink: 0;
        }}
        .next-btn:active {{ background: #2563eb; }}

        .analytics-card, .share-card {{
            background: #1e293b; border-radius: 18px; padding: 16px;
            border: 1px solid #334155; margin-bottom: 20px;
        }}
        .analytics-grid {{
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
            text-align: center; margin-top: 12px;
        }}
        .stat-box {{
            background: #0f172a; padding: 10px 6px; border-radius: 12px;
            border: 1px solid #1e293b;
        }}
        .stat-num {{ font-size: 1.1rem; font-weight: 800; color: #60a5fa; }}
        .stat-lbl {{ font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }}

        .share-card {{ display: flex; align-items: center; justify-content: space-between; }}
        .qr-img {{ border-radius: 10px; width: 75px; height: 75px; border: 2px solid #334155; }}

        .container {{ display: flex; flex-direction: column; gap: 12px; }}
        
        .file-card {{
            background: #1e293b; border-radius: 16px; padding: 14px 16px;
            border: 1px solid #334155; display: flex; flex-direction: column; gap: 10px;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .file-card:active {{ transform: scale(0.99); border-color: #3b82f6; }}
        
        .card-top {{ display: flex; align-items: center; gap: 12px; }}
        .icon-box {{
            width: 42px; height: 42px; background: #0f172a; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem; flex-shrink: 0; border: 1px solid #334155;
        }}
        .file-info {{ flex-grow: 1; overflow: hidden; }}
        .file-title {{
            font-weight: 600; color: #f1f5f9; font-size: 0.88rem;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .file-meta {{
            display: flex; align-items: center; gap: 8px;
            font-size: 0.75rem; color: #94a3b8; margin-top: 4px;
        }}
        
        .badge {{
            padding: 2px 8px; border-radius: 6px; font-size: 0.65rem; font-weight: 700;
        }}
        .badge-video {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; }}
        .badge-audio {{ background: rgba(168, 85, 247, 0.2); color: #c084fc; }}
        .badge-image {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
        .badge-doc {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}

        .card-action {{ width: 100%; }}
        .action-btn {{
            width: 100%; background: #0f172a; color: #38bdf8; border: 1px solid #334155;
            padding: 9px 14px; border-radius: 10px; font-size: 0.82rem; font-weight: 600;
            cursor: pointer; text-decoration: none; display: block; text-align: center;
            transition: 0.2s;
        }}
        .action-btn:active {{ background: #2563eb; color: #fff; border-color: #2563eb; }}
        .btn-download {{ color: #fbbf24; }}

        .img-preview {{
            width: 100%; border-radius: 10px; overflow: hidden;
            max-height: 200px; border: 1px solid #334155;
        }}
        .img-preview img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    </style>
</head>
<body>

    <div class="app-header">
        <div class="brand-logo">
            <div class="logo-icon">⚡</div>
            <div class="brand-text">
                <span class="brand-name">VAULT STUDIO</span>
                <span class="brand-tag">Local Media Streamer</span>
            </div>
        </div>
        <div class="status-badge">● LIVE</div>
    </div>

    <div class="search-wrapper">
        <span class="icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Search local files...">
        <span class="icon">🎙️</span>
    </div>

    <div class="filter-tags">
        <button class="tag-btn active" onclick="filterCategory('all', this)">Search All</button>
        <button class="tag-btn" onclick="filterCategory('video', this)">Videos ({stats['video']})</button>
        <button class="tag-btn" onclick="filterCategory('audio', this)">Audio ({stats['audio']})</button>
        <button class="tag-btn" onclick="filterCategory('image', this)">Photos ({stats['image']})</button>
        <button class="tag-btn" onclick="filterCategory('document', this)">Docs ({stats['document']})</button>
    </div>

    <div class="featured-frame">
        <div class="player-wrapper">
            <video id="featuredVideo" controls preload="metadata" style="display: {'block' if featured_type == 'video' else 'none'};">
                <source id="videoSource" src="{featured_media_src if featured_type == 'video' else ''}">
            </video>
            
            <div id="audioVis" class="audio-visualizer" style="display: {'flex' if featured_type == 'audio' else 'none'};">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
            
            <audio id="featuredAudio" controls style="display: {'block' if featured_type == 'audio' else 'none'};">
                <source id="audioSource" src="{featured_media_src if featured_type == 'audio' else ''}">
            </audio>
        </div>
        <div class="player-controls-bar">
            <div class="featured-title" id="featuredTitle">{featured_media_title}</div>
            <button class="next-btn" onclick="playNextMedia()">▶| Next</button>
        </div>
    </div>

    <div class="analytics-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong style="color: #f8fafc; font-size: 0.9rem;">Vault Analytics</strong>
            <span style="font-size: 0.8rem; font-weight: 700; color: #60a5fa;">{total_mb:.2f} MB</span>
        </div>
        <div class="analytics-grid">
            <div class="stat-box"><div class="stat-num">{stats['video']}</div><div class="stat-lbl">Videos</div></div>
            <div class="stat-box"><div class="stat-num">{stats['audio']}</div><div class="stat-lbl">Audio</div></div>
            <div class="stat-box"><div class="stat-num">{stats['image']}</div><div class="stat-lbl">Images</div></div>
            <div class="stat-box"><div class="stat-num">{stats['document']}</div><div class="stat-lbl">Docs</div></div>
        </div>
    </div>

    <div class="share-card">
        <div>
            <div style="font-weight: 700; color: #f8fafc; font-size: 0.88rem;">📶 Local Network Stream</div>
            <div style="font-family: monospace; color: #60a5fa; font-size: 0.8rem; margin-top: 4px;">{SERVER_URL}</div>
        </div>
        <img src="{qr_image_url}" class="qr-img" alt="QR Code">
    </div>

    <div class="container" id="cardContainer">
        {cards_html}
    </div>

    <script>
        const cards = document.querySelectorAll('.file-card');
        const videoEl = document.getElementById('featuredVideo');
        const audioEl = document.getElementById('featuredAudio');
        const videoSrc = document.getElementById('videoSource');
        const audioSrc = document.getElementById('audioSource');
        const audioVis = document.getElementById('audioVis');
        const titleLabel = document.getElementById('featuredTitle');

        let playlist = [];
        let currentTrackIndex = 0;

        function buildPlaylist() {{
            playlist = [];
            cards.forEach(c => {{
                const cat = c.getAttribute('data-category');
                if ((cat === 'video' || cat === 'audio') && c.style.display !== 'none') {{
                    const btn = c.querySelector('.action-btn');
                    if (btn) {{
                        const onclickText = btn.getAttribute('onclick');
                        if (onclickText) {{
                            const matches = onclickText.match(/playMedia\('(.*?)',\s*'(.*?)',\s*'(.*?)'\)/);
                            if (matches) {{
                                playlist.push({{ url: matches[1], title: matches[2], type: matches[3] }});
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function playMedia(url, title, type) {{
            buildPlaylist();
            currentTrackIndex = playlist.findIndex(item => item.url === url);
            
            titleLabel.innerText = title;
            
            if (type === 'video') {{
                audioEl.pause();
                audioEl.style.display = 'none';
                audioVis.style.display = 'none';
                
                videoSrc.src = url;
                videoEl.style.display = 'block';
                videoEl.load();
                videoEl.play();
            }} else if (type === 'audio') {{
                videoEl.pause();
                videoEl.style.display = 'none';
                
                audioSrc.src = url;
                audioEl.style.display = 'block';
                audioVis.style.display = 'flex';
                audioEl.load();
                audioEl.play();
            }}
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function playNextMedia() {{
            buildPlaylist();
            if (playlist.length === 0) return;
            currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
            const nextTrack = playlist[currentTrackIndex];
            playMedia(nextTrack.url, nextTrack.title, nextTrack.type);
        }}

        videoEl.addEventListener('ended', playNextMedia);
        audioEl.addEventListener('ended', playNextMedia);

        document.getElementById('searchInput').addEventListener('keyup', function(e) {{
            const q = e.target.value.toLowerCase();
            cards.forEach(c => {{
                const match = c.getAttribute('data-filename').includes(q);
                c.style.display = match ? "flex" : "none";
            }});
            buildPlaylist();
        }});

        function filterCategory(cat, btn) {{
            document.querySelectorAll('.tag-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            cards.forEach(c => {{
                if (cat === 'all' || c.getAttribute('data-category') === cat) {{
                    c.style.display = "flex";
                }} else {{
                    c.style.display = "none";
                }}
            }});
            buildPlaylist();
        }}

        window.onload = buildPlaylist;
    </script>
</body>
</html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(html.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def stream_file(self, file_path):
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        range_header = self.headers.get('Range')
        
        if range_header:
            bytes_range = range_header.replace('bytes=', '').split('-')
            start = int(bytes_range[0]) if bytes_range[0] else 0
            end = int(bytes_range[1]) if bytes_range[1] else file_size - 1
            if end >= file_size: end = file_size - 1
            length = end - start + 1
            
            self.send_response(206)
            self.send_header('Content-Type', mime_type)
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
            self.send_header('Content-Length', str(length))
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                f.seek(start)
                self.wfile.write(f.read(length))
        else:
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), VaultStudioEngine)
    print(f"Vault Studio running at {SERVER_URL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

