# D:\ai-smartcare-map\backend\chatbot_engine.py
import os
import json
import uuid
import re
from seacrowd import load_dataset as sc_load

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

BELAJAR_DIR = r'D:\ai-smartcare-map\backend\belajar'
os.makedirs(BELAJAR_DIR, exist_ok=True)

def normalize(text):
    """
    Hilangkan tanda baca, lowercase, dan normalisasi spasi berlebihan.
    Misal: "Apa apA" -> "apa apa"
    """
    text = re.sub(r"[^\w\s]", "", text).lower()
    text = re.sub(r"\s+", " ", text).strip() # Replace multiple spaces with single space
    return text

# Placeholder for geocoding functionality. You will need to implement this
# or ensure `geocodeLocation` is available and correctly imported/called.
# For demonstration, let's create a mock one.
def mock_geocode_location(location_name):
    """
    Mock function to simulate geocoding a location.
    In a real scenario, this would call a mapping API (e.g., OpenStreetMap Nominatim, Google Maps API).
    """
    print(f"⌛ Menganalisis lokasi '{location_name}'...")
    known_locations = {
        "binjai": {"name": "Binjai", "lat": 3.6146, "lon": 98.4687},
        "jakarta": {"name": "Jakarta", "lat": -6.2088, "lon": 106.8456},
        "medan": {"name": "Medan", "lat": 3.5952, "lon": 98.6722}
    }
    normalized_name = normalize(location_name)
    for key, value in known_locations.items():
        if key in normalized_name: # Simple match for demonstration
            return value
    return None

def fetch_indoqa_and_save():
    print("⏳ Mengambil dataset SEACrowd/indoqa …")
    try:
        dset = sc_load("indoqa", schema="seacrowd")
        count = 0
        for split in ["train", "validation"]:
            if split not in dset:
                continue
            for item in dset[split]:
                q_raw = item.get("question")
                a_raw = item.get("answer")

                if q_raw is None or a_raw is None:
                    continue

                q = " ".join(str(x) for x in q_raw) if isinstance(q_raw, list) else str(q_raw).strip()
                a = " ".join(str(x) for x in a_raw) if isinstance(a_raw, list) else str(a_raw).strip()

                if not q or not a:
                    continue

                path = os.path.join(BELAJAR_DIR, f"{uuid.uuid4()}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"question": q, "answer": a}, f, ensure_ascii=False, indent=2)
                count += 1
                if count >= 200: # Limit for quick testing
                    break
            if count >= 200:
                break
        print(f"✅ Berhasil simpan {count} Q&A IndoQA ke folder: '{BELAJAR_DIR}'")
    except Exception as e:
        print(f"❌ Gagal fetch dataset: {e}")

def hapus_cache_huggingface():
    import shutil
    cache = os.path.expanduser("~/.cache/huggingface/datasets")
    if os.path.exists(cache):
        shutil.rmtree(cache)
        print("✅ Cache Hugging Face datasets berhasil dihapus.")
    else:
        print("⚠️ Cache datasets tidak ditemukan.")

def chatbot_jawab(text):
    tx = normalize(text)
    words = set(tx.split())

    # Perintah khusus hapus semua
    if tx in ["clear", "hapus", "hapus semua", "clear chat", "hapus chat"]:
        for fn in os.listdir(BELAJAR_DIR):
            if fn.endswith(".json"):
                os.remove(os.path.join(BELAJAR_DIR, fn))
        return "__clear_chat__" # Special signal for frontend

    # Handle "lokasi saya" or similar requests
    if "lokasi saya" in tx or "temukan saya" in tx:
        return "Tentu, saya bisa bantu menemukan lokasi Anda saat ini. Mohon berikan izin lokasi di browser Anda."

    # Try to detect location search queries
    location_keywords = ["cari lokasi", "lokasi", "dimana", "peta", "alamat"]
    is_location_query = any(keyword in tx for keyword in location_keywords) and len(tx.split()) > 1

    if is_location_query:
        # Extract location name (simple example, could be more sophisticated)
        location_name_match = re.search(r"(?:cari lokasi|lokasi|dimana|peta|alamat)\s*:\s*(.*)", tx)
        if location_name_match:
            location_name = location_name_match.group(1).strip()
        else:
            # Fallback: assume the last part of the sentence is the location
            location_name_candidates = [word for word in tx.split() if len(word) > 2] # Avoid very short words
            if location_name_candidates:
                location_name = location_name_candidates[-1] # Try last meaningful word
            else:
                location_name = ""


        if location_name:
            geo_data = mock_geocode_location(location_name) # Call your actual geocoding function
            if geo_data:
                return f"📍 Lokasi \"{geo_data['name']}\" ditemukan. Peta akan mengarah ke sana."
            else:
                return f"❌ Lokasi \"{location_name}\" tidak ditemukan. Coba nama lain atau periksa ejaan."
        else:
            return "Mohon masukkan nama lokasi yang ingin dicari."


   

    # Load all Q&A from the 'belajar' directory
    qa_pairs = []
    for fn in os.listdir(BELAJAR_DIR):
        if fn.endswith(".json"):
            path = os.path.join(BELAJAR_DIR, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                q_raw = data.get("question", "")
                a = data.get("answer", "")
                if q_raw and a:
                    qa_pairs.append({"question": q_raw, "answer": a})
            except Exception as e:
                print(f"❌ Error membaca file {fn}: {e}")

    # --- Enhanced Matching Logic ---
    # 1. Exact or near-exact match after normalization
    for qa in qa_pairs:
        q_norm = normalize(qa["question"])
        if tx == q_norm:
            return qa["answer"]

    # 2. Fuzzy matching for close variations using fuzzywuzzy
    # Find the best match among all questions
    questions = [normalize(qa["question"]) for qa in qa_pairs]
    if questions: # Ensure there are questions to compare against
        # Use fuzz.ratio for short exact phrases, token_set_ratio for longer ones
        best_match_tuple = process.extractOne(tx, questions, scorer=fuzz.ratio)
        if best_match_tuple and best_match_tuple[1] >= 85: # Higher threshold for direct match
            matched_question_norm = best_match_tuple[0]
            for qa in qa_pairs:
                if normalize(qa["question"]) == matched_question_norm:
                    return qa["answer"]

        # Also try token_set_ratio for more flexible matching
        best_match_tuple_tokenset = process.extractOne(tx, questions, scorer=fuzz.token_set_ratio)
        if best_match_tuple_tokenset and best_match_tuple_tokenset[1] >= 75: # Slightly lower threshold for token set
            matched_question_norm = best_match_tuple_tokenset[0]
            for qa in qa_pairs:
                if normalize(qa["question"]) == matched_question_norm:
                    return qa["answer"]


    # 3. Keyword-based matching (fallback if fuzzy match isn't strong enough)
    # This checks if a significant portion of the user's input words are present in a question,
    # or vice-versa, allowing for more flexible partial matches.
    user_words = set(tx.split())
    for qa in qa_pairs:
        q_norm = normalize(qa["question"])
        q_words = set(q_norm.split())

        # Check for significant overlap of words
        common_words = user_words.intersection(q_words)
        if len(common_words) > 0:
            # Heuristic: if at least 50% of user words are in question OR
            # at least 50% of question words are in user input OR
            # for very short inputs (like "hai"), if there's any common word.
            if ((len(common_words) / len(user_words) >= 0.5) if user_words else False) or \
               ((len(common_words) / len(q_words) >= 0.5) if q_words else False) or \
               (len(common_words) >= 1 and len(tx) <= 5): # Very short input (e.g., "hai", "halo", "apa")
                return qa["answer"]

    # Jika tidak ditemukan jawaban
    return "🤖 Maaf, saya belum tahu jawabannya. Coba tanyakan hal lain."

# ✅ Fungsi tambahan: menambah pertanyaan umum
def tambah_pertanyaan_umum():
    data_umum = [
        # Existing data
    {"question": "hai", "answer": "halo"},
{"question": "ini web apa?", "answer": " bukan web tapi software"},
{"question": "ini web apa", "answer": "bukan web tapi software"},
{"question": "wargabuatin?", "answer": "Wargabantuin: Aplikasi AI untuk Filter Hewan & Sayur Cocok Berdasarkan Data Cuaca – Pendekatan CRISP-DM + Agile"},
{"question": "apa itu wargabuatin?", "answer": "Wargabantuin: Aplikasi AI untuk Filter Hewan & Sayur Cocok Berdasarkan Data Cuaca – Pendekatan CRISP-DM + Agile"},
{"question": "wargabuatin apa?", "answer": "Wargabantuin: Aplikasi AI untuk Filter Hewan & Sayur Cocok Berdasarkan Data Cuaca – Pendekatan CRISP-DM + Agile"},
{"question": "siapa penciptamu?", "answer": "Time RUCE"},
{"question": "RUCE?", "answer": "Time yang beranggotakan Ruth,Christian,Elkana"},
{"question": "Apa itu Ruce?", "answer": "Time yang beranggotakan Ruth,Christian,Elkana"},
{"question": "Kamu lagi apa?", "answer": "lagi komunikasi dengan kamu"},
{"question": "ohh?", "answer": "iya "},
{"question": "makasih?", "answer": "sama-sama "},
{"question": "sampai jumpa", "answer": "ok"},
{"question": "halo", "answer": "hai"},




    
    ]

    count = 0
    for item in data_umum:
        q = item["question"].strip()
        a = item["answer"].strip()
        # Check if a similar question already exists to avoid duplicates
        found = False
        for fn in os.listdir(BELAJAR_DIR):
            if fn.endswith(".json"):
                path = os.path.join(BELAJAR_DIR, fn)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    if normalize(data.get("question", "")) == normalize(q):
                        found = True
                        break
                except Exception as e:
                    print(f"❌ Error membaca file {fn}: {e}")
        if not found:
            path = os.path.join(BELAJAR_DIR, f"{uuid.uuid4()}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"question": q, "answer": a}, f, ensure_ascii=False, indent=2)
            count += 1

    print(f"✅ Berhasil tambah {count} pertanyaan umum ke folder '{BELAJAR_DIR}'")

if __name__ == "__main__":
    print("Tambah pertanyaan umum? (y/n)")
    if input("> ").strip().lower() == "y":
        tambah_pertanyaan_umum()
    print("Fetch dataset IndoQA? (y/n)")
    if input("> ").strip().lower() == "y":
        fetch_indoqa_and_save()
    print("Hapus cache HF? (y/n)")
    if input("> ").strip().lower() == "y":
        hapus_cache_huggingface()