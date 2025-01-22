from flask import Flask, request, jsonify, send_file
import os
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS hatalarını engellemek için

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format = data.get('format')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Yt-dlp ayarları
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
        }

        if format == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        # İndirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

            if format == 'mp3':
                file_name = file_name.rsplit('.', 1)[0] + '.mp3'

            return send_file(file_name, as_attachment=True, mimetype='audio/mpeg' if format == 'mp3' else 'video/mp4')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)
