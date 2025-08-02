import os
import time
from send2trash import send2trash
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Konfigurasi ---
SAMPAH_DIR = r"D:\ai-smartcare-map\backend\sampah" # Folder sumber yang akan dipantau
LOG_FILE = r"D:\ai-smartcare-map\backend\Sistem\recycle_bin_mover.log" # File log untuk mencatat aktivitas
POLLING_INTERVAL = 5 # Interval polling dalam detik (jika tidak menggunakan event handler)

# Pastikan folder sampah ada
if not os.path.exists(SAMPAH_DIR):
    os.makedirs(SAMPAH_DIR)
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now()}: Folder sampah '{SAMPAH_DIR}' dibuat.\n")

# Fungsi untuk menulis log
def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    print(log_entry.strip()) # Juga cetak ke konsol untuk debugging

# Fungsi untuk memindahkan file ke Recycle Bin
def move_to_recycle_bin():
    files_moved = 0
    errors_occurred = 0
    try:
        items_in_sampah = os.listdir(SAMPAH_DIR)
        if not items_in_sampah:
            # write_log(f"Folder '{SAMPAH_DIR}' kosong. Tidak ada file untuk dipindahkan.")
            return 0, 0 # Tidak ada file yang dipindahkan
            
        write_log(f"Memeriksa folder '{SAMPAH_DIR}' untuk file yang akan dipindahkan...")
        for item_name in items_in_sampah:
            item_path = os.path.join(SAMPAH_DIR, item_name)
            try:
                send2trash(item_path)
                write_log(f"Berhasil memindahkan '{item_path}' ke Recycle Bin.")
                files_moved += 1
            except Exception as e:
                write_log(f"ERROR: Gagal memindahkan '{item_path}' ke Recycle Bin: {e}")
                errors_occurred += 1
    except Exception as e:
        write_log(f"ERROR: Terjadi kesalahan saat mengakses folder '{SAMPAH_DIR}': {e}")
        errors_occurred += 1
    
    return files_moved, errors_occurred

# --- Event Handler untuk Watchdog (Mode Real-time) ---
class SampahEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            write_log(f"File baru terdeteksi: {event.src_path}. Memproses pemindahan...")
            time.sleep(1) # Beri sedikit waktu agar file selesai ditulis
            move_to_recycle_bin()

    def on_moved(self, event):
        # Ini akan terpicu jika file dipindahkan ke dalam folder sampah
        if not event.is_directory and event.dest_path.startswith(SAMPAH_DIR):
            write_log(f"File dipindahkan ke folder sampah: {event.dest_path}. Memproses pemindahan...")
            time.sleep(1) # Beri sedikit waktu
            move_to_recycle_bin()

# --- Main Program ---
if __name__ == "__main__":
    from datetime import datetime # Impor di sini agar bisa digunakan dalam fungsi log

    write_log("Memulai layanan pemindahan file ke Recycle Bin.")
    write_log(f"Memantau folder: {SAMPAH_DIR}")

    # Mode polling (fallback atau jika event handler tidak bekerja)
    # Observer dengan watchdog lebih efisien karena berbasis event
    observer = Observer()
    event_handler = SampahEventHandler()
    observer.schedule(event_handler, SAMPAH_DIR, recursive=False) # Pantau hanya folder sampah itu sendiri

    # Lakukan pemindahan awal saat script dimulai
    files_moved_initial, errors_initial = move_to_recycle_bin()
    if files_moved_initial > 0 or errors_initial > 0:
        write_log(f"Pemindahan awal selesai: {files_moved_initial} file dipindahkan, {errors_initial} error.")
    else:
        write_log("Tidak ada file di folder sampah saat startup awal.")

    observer.start() # Mulai pemantau event
    write_log("Pemantau folder watchdog dimulai.")

    try:
        while True:
            # Ini adalah bagian loop utama. Watchdog akan menangani event secara asinkron.
            # Kita bisa menambahkan polling periodik di sini sebagai fallback
            # jika event handler mungkin terlewat (misal saat banyak file tiba-tiba).
            time.sleep(POLLING_INTERVAL)
            files_moved_polling, errors_polling = move_to_recycle_bin()
            if files_moved_polling > 0 or errors_polling > 0:
                write_log(f"Pemindahan polling selesai: {files_moved_polling} file dipindahkan, {errors_polling} error.")

    except KeyboardInterrupt:
        write_log("Layanan dihentikan secara manual.")
    except Exception as e:
        write_log(f"ERROR: Layanan berhenti karena kesalahan tak terduga: {e}")
    finally:
        observer.stop()
        observer.join()
        write_log("Layanan pemindahan file ke Recycle Bin dihentikan.")