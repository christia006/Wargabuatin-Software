# main.py
from flask import Flask, request, jsonify
# Import start_auto_cache from ai_engine, as it's the core utility responsible for caching
from ai_engine import start_auto_cache 
# Import smart_rekomendasi from the new recommendation_module
from recommendation_module import smart_rekomendasi 
from chatbot_engine import chatbot_jawab, tambah_pertanyaan_umum
from laporan_handler import simpan_laporan
import os, json
from datetime import datetime
import subprocess

# Start the auto-caching process as soon as the application starts
start_auto_cache()

app = Flask(__name__)

# Configure the reports folder location
LAPORAN_DIR = os.path.join(os.path.dirname(__file__), 'laporan')
os.makedirs(LAPORAN_DIR, exist_ok=True)

# Default coordinates for the center of Indonesia
DEFAULT_LAT = -2.0
DEFAULT_LON = 118.0

# Path to the Recycle Bin mover script
RECYCLE_BIN_MOVER_SCRIPT = os.path.join('D:', os.sep, 'ai-smartcare-map', 'backend', 'Sistem', 'recycle_bin_mover.py')

@app.route('/api/laporan', methods=['POST'])
def api_laporan():
    """
    Endpoint to receive and store report data.
    If location or coordinates are not provided, default values will be used.
    """
    data = request.json

    if 'waktu' not in data:
        data['waktu'] = datetime.now().isoformat()

    # Ensure 'lokasi' exists and 'lat'/'lon' are valid numbers
    if not data.get('lokasi') or not (data.get('lat') is not None and data.get('lon') is not None):
        data['lat'] = DEFAULT_LAT
        data['lon'] = DEFAULT_LON
        print(f"DEBUG: Report location undefined or lat/lon incomplete, using default: {DEFAULT_LAT}, {DEFAULT_LON}")
    else:
        try:
            data['lat'] = float(data['lat'])
            data['lon'] = float(data['lon'])
        except (ValueError, TypeError):
            # If conversion fails, revert to default values
            data['lat'] = DEFAULT_LAT
            data['lon'] = DEFAULT_LON
            print(f"DEBUG: lat/lon conversion failed, using default: {DEFAULT_LAT}, {DEFAULT_LON}")

    try:
        simpan_laporan(data)
        return jsonify({"status": "ok", "message": "Laporan berhasil disimpan."}), 201
    except Exception as e:
        print(f"Error saving report: {e}")
        return jsonify({"status": "error", "message": f"Gagal menyimpan laporan: {str(e)}"}), 500

@app.route('/api/all_laporan', methods=['GET'])
def api_all_laporan():
    """
    Endpoint to retrieve all stored report data.
    Report data is retrieved from JSON files in the 'laporan' folder.
    """
    files = [f for f in os.listdir(LAPORAN_DIR) if f.endswith('.json')]
    data = []
    for file in files:
        try:
            with open(os.path.join(LAPORAN_DIR, file), 'r', encoding='utf-8') as f:
                d = json.load(f)
                data.append(d)
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file {file}: {e}")
        except Exception as e:
            print(f"General error reading file {file}: {e}")
    return jsonify({"laporan": data})

@app.route('/api/search', methods=['POST'])
def search():
    """
    Endpoint to perform recommendation searches based on a keyword.
    Uses the smart_rekomendasi function from recommendation_module.
    """
    keyword = request.json.get('keyword', '').lower().strip()
    results = smart_rekomendasi(keyword)
    return jsonify({"keyword": keyword, "rekomendasi": results})

@app.route('/api/all', methods=['GET'])
def all_lokasi():
    """
    Endpoint to get all location recommendations.
    Uses the smart_rekomendasi function with an empty keyword.
    """
    results = smart_rekomendasi('')
    return jsonify({"lokasi": results})

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """
    Endpoint for chatbot interaction.
    Uses the chatbot_jawab function from chatbot_engine.
    """
    keyword = request.json.get('keyword', '').lower().strip()
    jawaban = chatbot_jawab(keyword)
    return jsonify({"jawaban": jawaban})

if __name__ == '__main__':
    # --- Call function to add common questions at startup ---
    print("Ensuring common chatbot questions are loaded...")
    tambah_pertanyaan_umum()
    print("Common chatbot questions loaded.")
    # --- End of chatbot code addition ---

    # --- Code to start the Recycle Bin file mover script ---
    print(f"Attempting to start file mover service from: {RECYCLE_BIN_MOVER_SCRIPT}")
    try:
        # Use pythonw.exe to run the script without a console window.
        # stdout and stderr are set to PIPE to prevent creating separate console windows.
        subprocess.Popen(['pythonw.exe', RECYCLE_BIN_MOVER_SCRIPT],
                         cwd=os.path.dirname(RECYCLE_BIN_MOVER_SCRIPT),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        print("Recycle Bin file mover service started successfully.")
    except FileNotFoundError:
        print(f"ERROR: pythonw.exe or script '{RECYCLE_BIN_MOVER_SCRIPT}' not found. Ensure Python is installed and PATH is correct.")
    except Exception as e:
        print(f"ERROR: Failed to start file mover service: {e}")
    # --- End of code addition ---

    # Run the Flask application in debug mode
    app.run(debug=True)