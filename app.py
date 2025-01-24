from flask import Flask, request, jsonify, send_file
import os
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# İlerleme bilgisini tutacak global bir değişken
progress_info = {}

def progress_hook(d):
    if d['status'] == 'downloading':
        progress_info['current'] = round(d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100, 2)
    elif d['status'] == 'finished':
        progress_info['current'] = 100

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format = data.get('format')

    if not url or not format:
        return jsonify({'error': 'URL or format missing in request'}), 400

    try:
        ydl_opts = {
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
            'progress_hooks': [progress_hook],
        }

        # YouTube Shorts'lar için özel işlem
        if 'shorts' in url:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'  # Shorts videoları için yüksek kaliteli video
            ydl_opts['noplaylist'] = True  # Playlist'i engelle

        if format == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

            if format == 'mp3':
                file_name = file_name.rsplit('.', 1)[0] + '.mp3'

            if not os.path.isfile(file_name):
                return jsonify({'error': 'File not found'}), 404

            return jsonify({'file_name': file_name})  # Dosya adını istemciye döndür

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_file', methods=['GET'])
def download_file():
    file_name = request.args.get('file')

    if not file_name or not os.path.isfile(file_name):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_name, as_attachment=True)

@app.route('/progress', methods=['GET'])
def get_progress():
    # İlerleme bilgisini döndürüyoruz
    return jsonify(progress_info)

@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)
