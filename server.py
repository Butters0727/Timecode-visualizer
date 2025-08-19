import os
import subprocess
import webbrowser
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tempfile
import ffmpeg

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    try:
        if file.filename.lower().endswith('.tc'):
            start_str, end_str = parse_tc_file(temp_file_path)
            start_millis = time_str_to_millis(start_str)
            end_millis = time_str_to_millis(end_str)

        elif file.filename.lower().endswith('.mp4'):
            timecode_data = ffmpeg.probe(temp_file_path, select_streams='v:0', show_entries='stream_tags=timecode')
            timecode = timecode_data['streams'][0]['tags']['timecode'] if 'tags' in timecode_data['streams'][0] and 'timecode' in timecode_data['streams'][0]['tags'] else "00:00:00:00"
            start_str = timecode

            duration_data = ffmpeg.probe(temp_file_path, select_streams='v:0', show_entries='format=duration')
            duration_sec = float(duration_data['format']['duration'])
            
            start_millis = time_str_to_millis(start_str)
            end_millis = start_millis + (duration_sec * 1000)
        else:
            os.remove(temp_file_path)
            return jsonify({"error": "Unsupported file type"}), 400

        os.remove(temp_file_path)
        return jsonify({
            "name": file.filename,
            "startTime": start_millis,
            "endTime": end_millis
        })

    except Exception as e:
        os.remove(temp_file_path)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('.', path)

def parse_tc_file(tc_path):
    with open(tc_path, 'r', errors='ignore') as f:
        lines = [line for line in f if line.strip()]
        if not lines:
            raise ValueError("TC file is empty")
        h1, m1, s1 = lines[0].strip().split(',')[1:4]
        start_time_str = f"{h1.zfill(2)}:{m1.zfill(2)}:{s1.zfill(2)}"
        h2, m2, s2 = lines[-1].strip().split(',')[1:4]
        end_time_str = f"{h2.zfill(2)}:{m2.zfill(2)}:{s2.zfill(2)}"
        return start_time_str, end_time_str

def get_mp4_timecode(mp4_path):
    pass

def time_str_to_millis(time_str):
    parts = time_str.split(':')
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    return (h * 3600 + m * 60 + s) * 1000

if __name__ == '__main__':
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)
    app.run(port=5000, debug=False)