# ai_engine.py
import os
import json
import requests
import time
import threading
import shutil
import datetime
import random
from collections import defaultdict, Counter # Counter is needed here for general utility, and defaultdict for rate limiting.

# --- Directory Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
SAMPAH_DIR = os.path.join(os.path.dirname(__file__), 'sampah')

# --- Cache Update Variables ---
_last_update_times = {}
UPDATE_INTERVAL = 300 # 5 minutes

# --- Rate Limiting Variables (Ditingkatkan) ---
# Stores lists of timestamps for each 'adm4' (simulating a unique endpoint/resource usage)
_request_timestamps = defaultdict(list)
# Batas permintaan per menit, bisa disesuaikan. BMKG biasanya memblokir jika terlalu cepat.
RATE_LIMIT_PER_MINUTE = 20 # Mengurangi dari 50 ke 20 per menit per ADM4
RATE_LIMIT_WINDOW_SECONDS = 60
# --- End Rate Limiting ---

# Ensure necessary directories exist
os.makedirs(SAMPAH_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def load_json(filepath):
    """Loads JSON data from a given file path."""
    try:
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ File {os.path.basename(filepath)} tidak ditemukan. Mengembalikan list kosong.")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Gagal decode JSON dari {os.path.basename(filepath)}: {e}")
        return []
    except Exception as e:
        print(f"❌ Gagal baca {os.path.basename(filepath)}: {e}")
        return []

def load_all_links():
    """
    Loads all links from all JSON files found in the DATA_DIR.
    Assumes each JSON file contains a list of dictionaries with 'adm4' and 'url'.
    """
    all_links = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            data = load_json(filepath)
            if isinstance(data, list):
                # Filter for items that look like links (have 'adm4' and 'url')
                valid_links = [item for item in data if isinstance(item, dict) and 'adm4' in item and 'url' in item]
                all_links.extend(valid_links)
            else:
                print(f"ℹ️ File {filename} tidak berisi list di root, dilewati.")
    print(f"✅ Ditemukan {len(all_links)} link dari semua file JSON di {DATA_DIR}.")
    return all_links

def save_cache(adm4, data):
    """Saves data to a JSON cache file in the CACHE_DIR."""
    file_path = os.path.join(CACHE_DIR, f"{adm4}.json")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Menambahkan delay setelah menyimpan untuk memberikan jeda pada sistem file
        time.sleep(0.05)
    except Exception as e:
        print(f"❌ Gagal simpan cache {adm4}: {e}")

def get_random_user_agent():
    """Returns a random User-Agent string."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Android 12; Mobile; rv:102.0) Gecko/102.0 Firefox/102.0',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Mobile Safari/537.36'
    ]
    return random.choice(user_agents)

def fetch_with_retry(url, adm4=None, retries=5, initial_delay=1):
    """
    Fetches data from a URL with retries and applies rate limiting based on adm4.
    """
    headers = {'User-Agent': get_random_user_agent()}

    # --- Rate Limiting Logic ---
    if adm4: # Apply rate limiting only if adm4 is provided
        current_time = time.time()

        # Clean up old timestamps outside the window
        _request_timestamps[adm4] = [
            ts for ts in _request_timestamps[adm4] if current_time - ts < RATE_LIMIT_WINDOW_SECONDS
        ]

        # If we've hit the limit, wait until the window clears
        if len(_request_timestamps[adm4]) >= RATE_LIMIT_PER_MINUTE:
            wait_time = _request_timestamps[adm4][0] + RATE_LIMIT_WINDOW_SECONDS - current_time
            if wait_time > 0:
                print(f"⏳ Rate limit hit for {adm4}. Waiting for {wait_time:.2f} seconds before retrying this ADM4...")
                time.sleep(wait_time + random.uniform(0.5, 1.5)) # Add extra random delay after waiting
                # After waiting, re-clean up as time has passed
                current_time = time.time()
                _request_timestamps[adm4] = [
                    ts for ts in _request_timestamps[adm4] if current_time - ts < RATE_LIMIT_WINDOW_SECONDS
                ]

        # Record the current request timestamp
        _request_timestamps[adm4].append(current_time)
    # --- End Rate Limiting ---

    for i in range(retries):
        try:
            print(f"🌐 Mencoba fetch: {url} (Percobaan {i+1}/{retries})")
            res = requests.get(url, headers=headers, timeout=15) # Increased timeout
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as e:
            if res.status_code == 429: # Too Many Requests
                sleep_duration = initial_delay * (2 ** i) + random.uniform(1, 3) # Exponential backoff with random jitter
                print(f"⚠️ Dibatasi oleh server (429) untuk {url}. Menunggu {sleep_duration:.2f} detik.")
                time.sleep(sleep_duration)
            elif res.status_code == 403: # Forbidden (often used for blocking)
                sleep_duration = initial_delay * (2 ** i) * 2 + random.uniform(5, 10) # Longer for 403
                print(f"⛔ Akses diblokir (403) untuk {url}. Ini serius! Menunggu {sleep_duration:.2f} detik dan mengubah User-Agent.")
                time.sleep(sleep_duration)
                headers = {'User-Agent': get_random_user_agent()} # Change User-Agent on 403 block
            elif i < retries - 1:
                sleep_duration = initial_delay * (i + 1) + random.uniform(0.5, 2)
                print(f"⚠️ HTTPError {res.status_code} saat fetch {url}. Menunggu {sleep_duration:.2f} detik.")
                time.sleep(sleep_duration)
            else:
                print(f"❌ Gagal total HTTPError saat fetch {url}: {e} (Status: {res.status_code})")
                break
        except requests.exceptions.ConnectionError as e:
            sleep_duration = initial_delay * (i + 1) + random.uniform(0.5, 2)
            print(f"❌ Koneksi error saat fetch {url}: {e}. Menunggu {sleep_duration:.2f} detik.")
            time.sleep(sleep_duration)
        except requests.exceptions.Timeout as e:
            sleep_duration = initial_delay * (i + 1) + random.uniform(0.5, 2)
            print(f"❌ Timeout saat fetch {url}: {e}. Menunggu {sleep_duration:.2f} detik.")
            time.sleep(sleep_duration)
        except Exception as e:
            print(f"❌ Error tak terduga saat fetch {url}: {e}")
            break
    return None

def auto_cache_worker():
    """Worker thread to periodically fetch and cache weather data."""
    print("🟢 Auto cache worker dimulai...")
    while True:
        links = load_all_links() # Use the new function to load all links
        now = time.time()

        for item in links:
            adm4 = item.get('adm4')
            url = item.get('url')
            if not adm4 or not url:
                continue

            last_update = _last_update_times.get(adm4, 0)
            if now - last_update < UPDATE_INTERVAL:
                print(f"ℹ️ {adm4} baru diupdate. Melewatkan pembaruan saat ini.")
                continue

            print(f"📥 Fetching data baru untuk: {adm4} dari {url}")
            # Pastikan adm4 diteruskan ke fetch_with_retry untuk rate limiting
            fetched_data = fetch_with_retry(url, adm4=adm4) 

            # --- PERUBAHAN DI SINI ---
            cache_file = os.path.join(CACHE_DIR, f"{adm4}.json")
            # --- AKHIR PERUBAHAN ---

            data_to_save = None
            location_extracted = {}
            weather_data_extracted = []

            if fetched_data:
                # Handle different API response structures
                if isinstance(fetched_data, dict) and 'lokasi' in fetched_data:
                    location_extracted = fetched_data.get('lokasi', {})
                    if isinstance(fetched_data.get('data'), list):
                        weather_data_extracted = fetched_data['data']
                    elif fetched_data.get('data') is None:
                        weather_data_extracted = []
                    else:
                        print(f"⚠️ 'data' field for {adm4} is not a list, treating as empty.")
                        weather_data_extracted = []
                elif isinstance(fetched_data, list) and fetched_data:
                    for entry in fetched_data:
                        if isinstance(entry, dict) and 'lokasi' in entry:
                            location_extracted = entry.get('lokasi', {})
                            if 'cuaca' in entry and isinstance(entry.get('cuaca'), list):
                                weather_data_extracted = entry['cuaca']
                            elif 'data' in entry and isinstance(entry.get('data'), list):
                                weather_data_extracted = entry['data']
                            break
                else:
                    print(f"⚠️ Respon API untuk {adm4} tidak dalam format yang dikenali (bukan dict/list dengan lokasi).")

                if location_extracted:
                    data_to_save = {
                        "lokasi": location_extracted,
                        "data": weather_data_extracted
                    }
                else:
                    print(f"⚠️ Tidak dapat menemukan informasi lokasi yang valid dari API untuk {adm4}.")

                if data_to_save:
                    if os.path.exists(cache_file):
                        try:
                            timestamp_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                            shutil.move(cache_file, os.path.join(SAMPAH_DIR, f"{adm4}_{timestamp_str}.json"))
                            print(f"🗑️ Memindahkan cache lama untuk: {adm4}.json ke sampah.")
                        except Exception as e:
                            print(f"⚠️ Gagal memindahkan cache lama ({cache_file}) ke sampah: {e}")

                    save_cache(adm4, data_to_save)
                    _last_update_times[adm4] = now
                    print(f"✅ Cache baru disimpan untuk: {adm4}.json")
                else:
                    print(f"⚠️ Gagal ambil data atau data tidak lengkap untuk {adm4}. Memuat dummy data atau menggunakan cache lama jika ada.")
                    if not os.path.exists(cache_file):
                        dummy = {
                            "lokasi": {"adm4": adm4, "desa": "N/A", "kecamatan": "N/A", "kotkab": "N/A", "provinsi": "N/A", "lat": None, "lon": None},
                            "data": []
                        }
                        save_cache(adm4, dummy)
                        print(f"✅ Dummy cache disimpan untuk: {adm4}.json")
                    else:
                        print(f"ℹ️ Cache {adm4}.json sudah ada, tidak membuat dummy baru setelah gagal fetch atau data tidak lengkap.")

            _last_update_times[adm4] = now # Keep updating last time to avoid trying again too quickly
            time.sleep(random.uniform(0.5, 2)) # Increased random delay between requests to different locations

        print("😴 Auto cache worker tidur selama 10 detik...")
        time.sleep(10)

def start_auto_cache():
    """Starts the auto-caching worker in a daemon thread."""
    thread = threading.Thread(target=auto_cache_worker, daemon=True)
    thread.start()

# Example of how to start the auto cache worker (optional, you can call it from another script)
if __name__ == '__main__':
    print("Starting AI Engine main process...")
    start_auto_cache()
    # Keep the main thread alive if this is the primary script
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nAI Engine stopped.")