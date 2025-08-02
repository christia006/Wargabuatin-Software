import os
import json
import datetime
from collections import Counter
import pytz

# Import necessary components from ai_engine.py
from ai_engine import DATA_DIR, CACHE_DIR, load_json

def cocok_item(item, rata2_suhu, rata2_hu, keyword):
    """Checks if an item (animal/vegetable) is suitable based on avg temp/humidity and keyword."""
    nama = item.get("nama", "").lower()
    suhu_min = item.get("suhu_min")
    suhu_max = item.get("suhu_max")
    hu_min = item.get("hu_min")
    hu_max = item.get("hu_max")

    if not all(isinstance(v, (int, float)) for v in [suhu_min, suhu_max, hu_min, hu_max]):
        return False

    cocok_suhu = (rata2_suhu is not None) and (suhu_min <= rata2_suhu <= suhu_max)
    cocok_hu = (rata2_hu is not None) and (hu_min <= rata2_hu <= hu_max)
    cocok_keyword = (keyword in nama) or (keyword == '')

    return cocok_suhu and cocok_hu and cocok_keyword

def smart_rekomendasi(keyword):
    keyword = keyword.lower()
    hewan_list = load_json(os.path.join(DATA_DIR, 'hewan_cocok.json'))
    sayuran_list = load_json(os.path.join(DATA_DIR, 'sayuran_cocok.json'))
    results = []

    # Pastikan pakai timezone Asia/Jakarta untuk perbandingan realtime
    tz_jakarta = pytz.timezone("Asia/Jakarta")
    now_local = datetime.datetime.now(tz=tz_jakarta) # Ambil waktu sekarang dengan timezone
    
    # Dapatkan tanggal hari ini dalam format YYYY-MM-DD
    today_date_str = now_local.strftime('%Y-%m-%d')

    # Define weather icon mappings
    weather_icons = {
        "hujan": "https://api-apps.bmkg.go.id/storage/icon/cuaca/hujan%20ringan-pm.svg",
        "berawan": "https://api-apps.bmkg.go.id/storage/icon/cuaca/berawan-am.svg",
        "cerah berawan": "https://api-apps.bmkg.go.id/storage/icon/cuaca/cerah%20berawan-am.svg",
        "default": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png" # Default fallback
    }

    # Iterate through existing cache files
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith('.json'):
            adm4 = filename[:-5] # Remove .json extension
            cache_file = os.path.join(CACHE_DIR, filename)

            try:
                with open(cache_file, encoding='utf-8') as f:
                    data = json.load(f)

                lokasi = data.get('lokasi', {})
                data_list = data.get('data', [])

                suhu_hari_ini_values = [] # List untuk menyimpan suhu HARI INI saja
                t_values_all = []        # List untuk menyimpan semua suhu (untuk rata-rata periode)
                hu_values_all = []       # List untuk menyimpan semua kelembaban (untuk rata-rata periode)
                descs_all = []           # List untuk menyimpan semua deskripsi cuaca (jika diperlukan untuk mode dominan, tapi kita pakai realtime)
                date_start, date_end = None, None # Inisialisasi dengan None

                # Variabel untuk menemukan data cuaca paling realtime
                closest_item = None
                min_diff = float('inf')

                # Flatten semua data cuaca jadi satu list untuk memudahkan iterasi
                flat_list = []
                for d_entry in data_list:
                    cuaca_entry_list = d_entry.get('cuaca', d_entry.get('data', []))
                    for c_item in cuaca_entry_list:
                        if isinstance(c_item, list):
                            flat_list.extend(c_item)
                        elif isinstance(c_item, dict):
                            flat_list.append(c_item)

                # Find start & end dates (dari flat_list yang sudah di-flatten)
                datetimes = []
                for c_item in flat_list:
                    dt_str = c_item.get('datetime')
                    if dt_str:
                        try:
                            dt_obj = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            datetimes.append(dt_obj)
                        except ValueError:
                            try:
                                dt_obj = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                                datetimes.append(dt_obj)
                            except Exception:
                                pass

                if datetimes:
                    datetimes_sorted = sorted(datetimes)
                    date_start = datetimes_sorted[0].strftime('%Y-%m-%d')
                    date_end = datetimes_sorted[-1].strftime('%Y-%m-%d')

                # Kumpulkan semua nilai suhu, kelembaban, dan deskripsi cuaca
                for c_item in flat_list:
                    t = c_item.get('t')
                    hu = c_item.get('hu')
                    desc = c_item.get('weather_desc')
                    local_dt_str = c_item.get('local_datetime') or c_item.get('datetime')

                    # Kumpulkan semua suhu dan kelembaban untuk rata-rata periode keseluruhan
                    if isinstance(t, (int, float)):
                        t_values_all.append(t)
                    if isinstance(hu, (int, float)):
                        hu_values_all.append(hu)
                    if isinstance(desc, str):
                        descs_all.append(desc)

                    # --- AKURASI SUHU HARI INI: Filter berdasarkan tanggal lokal "hari ini" ---
                    if local_dt_str:
                        try:
                            # Coba parse dengan beberapa format
                            current_item_dt = datetime.datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                current_item_dt = datetime.datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M")
                            except Exception:
                                current_item_dt = None # Jika gagal parse, set ke None

                        if current_item_dt and current_item_dt.strftime('%Y-%m-%d') == today_date_str:
                            if isinstance(t, (int, float)):
                                suhu_hari_ini_values.append(t)
                    # --- AKHIR AKURASI SUHU HARI INI ---

                    # Logic untuk mencari data cuaca paling realtime (untuk t_realtime, hu_realtime, cuaca_realtime)
                    if local_dt_str:
                        try:
                            local_dt_obj_tz = tz_jakarta.localize(datetime.datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M:%S"))
                        except ValueError:
                            try:
                                local_dt_obj_tz = tz_jakarta.localize(datetime.datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M"))
                            except Exception:
                                continue # Lanjutkan ke item berikutnya jika tidak bisa diparse
                        
                        diff = abs((local_dt_obj_tz - now_local).total_seconds())

                        if diff < min_diff:
                            min_diff = diff
                            closest_item = c_item
                
                # --- Ekstraksi nilai realtime (suhu, kelembapan, cuaca) ---
                t_realtime = None
                hu_realtime = None
                cuaca_realtime = ''
                weather_icon_url = weather_icons["default"]

                if closest_item:
                    if isinstance(closest_item.get('t'), (int, float)):
                        t_realtime = round(closest_item.get('t'), 1)
                    if isinstance(closest_item.get('hu'), (int, float)):
                        hu_realtime = round(closest_item.get('hu'), 1)
                    
                    cuaca_realtime = closest_item.get('weather_desc', '') # Default ke string kosong
                    
                    cuaca_lower = cuaca_realtime.lower()
                    if "hujan" in cuaca_lower:
                        weather_icon_url = weather_icons["hujan"]
                    elif "cerah berawan" in cuaca_lower:
                        weather_icon_url = weather_icons["cerah berawan"]
                    elif "berawan" in cuaca_lower:
                        weather_icon_url = weather_icons["berawan"]

                # --- Finalisasi Suhu Hari Ini (Rata-rata, Max, Min) ---
                # Default ke None jika tidak ada data suhu hari ini
                suhu_hari_ini = {
                    "rata2": round(sum(suhu_hari_ini_values)/len(suhu_hari_ini_values),1) if suhu_hari_ini_values else None,
                    "max": round(max(suhu_hari_ini_values),1) if suhu_hari_ini_values else None,
                    "min": round(min(suhu_hari_ini_values),1) if suhu_hari_ini_values else None
                }

                # Finalize rata-rata suhu dan kelembaban periode (default ke None jika tidak ada data)
                rata2_suhu = round(sum(t_values_all)/len(t_values_all),1) if t_values_all else None
                rata2_hu = round(sum(hu_values_all)/len(hu_values_all),1) if hu_values_all else None

                # Filter suitable animals & vegetables (hanya jika rata2_suhu dan rata2_hu adalah float)
                cocok_hewan, cocok_sayur = [], []
                if isinstance(rata2_suhu, float) and isinstance(rata2_hu, float):
                    for h in hewan_list:
                        if cocok_item(h, rata2_suhu, rata2_hu, keyword):
                            cocok_hewan.append(h["nama"])
                    for s in sayuran_list:
                        if cocok_item(s, rata2_suhu, rata2_hu, keyword):
                            cocok_sayur.append(s["nama"])

                cocok_lokasi = any(keyword in (lokasi.get(k,'').lower()) for k in ['desa','kecamatan','kotkab','provinsi', 'adm4'])
                
                alasan = []
                if cocok_lokasi:
                    alasan.append("Lokasi cocok dengan keyword")
                if keyword and cocok_hewan and any(keyword in h.lower() for h in cocok_hewan):
                    alasan.append(f"Hewan '{keyword}' cocok")
                if keyword and cocok_sayur and any(keyword in s.lower() for s in cocok_sayur):
                    alasan.append(f"Sayuran '{keyword}' cocok")
                if not keyword and (cocok_hewan or cocok_sayur):
                     alasan.append("Tidak ada keyword, menampilkan lokasi dengan rekomendasi")
                if not alasan and (t_realtime is not None or hu_realtime is not None):
                     alasan.append("Kondisi cuaca tersedia")
                if not alasan and not keyword:
                    alasan.append("Tidak ada keyword dan kondisi cuaca belum spesifik untuk rekomendasi")
                if not alasan and keyword:
                    alasan.append("Keyword tidak ditemukan atau kondisi cuaca tidak cocok")


                if cocok_hewan or cocok_sayur or cocok_lokasi or keyword == '' or t_realtime is not None or hu_realtime is not None:
                    results.append({
                        "adm4": adm4,
                        "desa": lokasi.get('desa',''),
                        "kecamatan": lokasi.get('kecamatan',''),
                        "kotkab": lokasi.get('kotkab',''),
                        "provinsi": lokasi.get('provinsi',''),
                        "lat": lokasi.get('lat'),
                        "lon": lokasi.get('lon'),
                        "suhu_hari_ini": suhu_hari_ini, # Mengandung None jika tidak ada data
                        "rata2_suhu": rata2_suhu,
                        "rata2_hu": rata2_hu,
                        "suhu_realtime": t_realtime,
                        "kelembapan_realtime": hu_realtime,
                        "weather_desc": cuaca_realtime,
                        "weather_icon_url": weather_icon_url,
                        "date_start": date_start or '',
                        "date_end": date_end or '',
                        "cocok_untuk": {
                            "hewan": cocok_hewan or [],
                            "sayuran": cocok_sayur or []
                        },
                        "alasan": ", ".join(alasan) if alasan else "Informasi cuaca tersedia"
                    })
            except Exception as e:
                # print(f"❌ Gagal parsing cache {adm4}: {e}") # Debugging
                pass # Abaikan lokasi yang gagal diproses

    return results

# Example of how to use smart_rekomendasi (optional)
if __name__ == '__main__':
    print("\n--- Rekomendasi untuk 'ayam' ---")
    recommendations = smart_rekomendasi("ayam")
    for rec in recommendations:
        print(f"Lokasi: {rec['desa']}, {rec['kecamatan']}, {rec['kotkab']}, {rec['provinsi']}")
        print(f"    Suhu Realtime: {rec['suhu_realtime'] if rec['suhu_realtime'] is not None else 'N/A'}°C")
        print(f"    Kelembapan Realtime: {rec['kelembapan_realtime'] if rec['kelembapan_realtime'] is not None else 'N/A'}%")
        print(f"    Cuaca Saat Ini: {rec['weather_desc'] if rec['weather_desc'] else 'Tidak ada data'}")
        print(f"    Weather Icon: {rec['weather_icon_url']}")
        
        # Output Suhu Hari Ini dengan pemeriksaan None
        print(f"    Suhu Hari Ini:")
        print(f"        Rata-rata: {rec['suhu_hari_ini']['rata2'] if rec['suhu_hari_ini']['rata2'] is not None else 'N/A'}°C")
        print(f"        Maksimum: {rec['suhu_hari_ini']['max'] if rec['suhu_hari_ini']['max'] is not None else 'N/A'}°C")
        print(f"        Minimum: {rec['suhu_hari_ini']['min'] if rec['suhu_hari_ini']['min'] is not None else 'N/A'}°C")
        
        print(f"    Rata-rata Suhu (Periode): {rec['rata2_suhu'] if rec['rata2_suhu'] is not None else 'N/A'}°C")
        print(f"    Rata-rata Kelembaban: {rec['rata2_hu'] if rec['rata2_hu'] is not None else 'N/A'}%")
        print(f"    Cocok untuk Hewan: {', '.join(rec['cocok_untuk']['hewan']) if rec['cocok_untuk']['hewan'] else 'Tidak ada'}")
        print(f"    Cocok untuk Sayuran: {', '.join(rec['cocok_untuk']['sayuran']) if rec['cocok_untuk']['sayuran'] else 'Tidak ada'}")
        print(f"    Alasan: {rec['alasan']}\n")

    print("\n--- Rekomendasi umum (tanpa keyword) ---")
    recommendations_general = smart_rekomendasi("")
    for rec in recommendations_general[:3]:
        print(f"Lokasi: {rec['desa']}, {rec['kecamatan']}, {rec['kotkab']}, {rec['provinsi']}")
        print(f"    Suhu Realtime: {rec['suhu_realtime'] if rec['suhu_realtime'] is not None else 'N/A'}°C")
        print(f"    Kelembapan Realtime: {rec['kelembapan_realtime'] if rec['kelembapan_realtime'] is not None else 'N/A'}%")
        print(f"    Cuaca Saat Ini: {rec['weather_desc'] if rec['weather_desc'] else 'Tidak ada data'}")
        
        print(f"    Suhu Hari Ini:")
        print(f"        Rata-rata: {rec['suhu_hari_ini']['rata2'] if rec['suhu_hari_ini']['rata2'] is not None else 'N/A'}°C")
        print(f"        Maksimum: {rec['suhu_hari_ini']['max'] if rec['suhu_hari_ini']['max'] is not None else 'N/A'}°C")
        print(f"        Minimum: {rec['suhu_hari_ini']['min'] if rec['suhu_hari_ini']['min'] is not None else 'N/A'}°C")
        
        print(f"    Alasan: {rec['alasan']}\n")