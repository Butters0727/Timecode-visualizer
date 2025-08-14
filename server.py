import os
import subprocess
import webbrowser
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tempfile

# --- Auto-detect ffprobe path ---
def find_ffprobe():
    # Look for ffprobe.exe in the same directory as the script
    # os.path.dirname(__file__) might be empty if run from interactive shell, so handle that
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(script_dir, 'ffprobe.exe')
    if os.path.exists(local_path):
        print(f"Found local ffprobe at: {local_path}")
        return local_path
    # Fallback to assuming it's in the system PATH
    print("Local ffprobe not found, falling back to system PATH.")
    return "ffprobe"

FFPROBE_PATH = find_ffprobe()

app = Flask(__name__)
CORS(app)

# --- API Route for processing files ---
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
            start_str = get_mp4_timecode(temp_file_path)
            duration_command = [FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', temp_file_path]
            duration_result = subprocess.run(duration_command, capture_output=True, text=True, check=True)
            duration_sec = float(duration_result.stdout.strip())
            
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

# --- Routes for serving the frontend application ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('.', path)

# --- Helper Functions ---
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
    command = [FFPROBE_PATH, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream_tags=timecode', '-of', 'default=noprint_wrappers=1:nokey=1', mp4_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        timecode = result.stdout.strip()
        if not timecode:
            return "00:00:00:00"
        return timecode
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running ffprobe: {e}")
        print("Please ensure ffprobe.exe is in the same directory as this script, or in your system's PATH.")
        raise e

def time_str_to_millis(time_str):
    parts = time_str.split(':')
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    return (h * 3600 + m * 60 + s) * 1000

if __name__ == '__main__':
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)
    app.run(port=5000, debug=False)
