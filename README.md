# 🌾 Wargabantuin
**Aplikasi Cerdas untuk Petani dan Peternak di Indonesia**

Wargabantuin membantu warga, petani, dan peternak di Indonesia memilih hewan ternak dan sayuran yang paling cocok berdasarkan data cuaca terkini dari BMKG.  
Dengan peta interaktif dan chatbot AI, aplikasi ini mendukung pertanian dan peternakan yang lebih aman dan berkelanjutan.

---

## ✨ Fitur Utama
- Rekomendasi komoditas paling cocok dengan skor kecocokan (0–100) dan alasan singkat.
- Peta interaktif yang menampilkan rekomendasi di setiap lokasi.
- Chatbot AI yang dapat menjawab pertanyaan seputar cuaca dan kecocokan komoditas.
- Data terpercaya dari BMKG dan sumber resmi universitas/proyek pertanian.

---

## 🔧 Cara Kerja Singkat
1. Mengambil data cuaca terbaru dari BMKG.
2. Membersihkan dan memproses data (menghitung suhu rata-rata, tertinggi, terendah, dan kelembapan).
3. Membandingkan kondisi lokasi Anda dengan kebutuhan ideal hewan/sayuran.
4. Menghasilkan skor kecocokan dan rekomendasi.
5. Menyediakan data melalui API dan chatbot AI.

---

## 🗂️ Contoh Format Data

### Lokasi
```json
{
  "provinsi": "Sumatera Utara",
  "kotkab": "Tapanuli Tengah",
  "kecamatan": "Barus",
  "desa": "Kampung Solok",
  "lon": 00.0000000000,
  "lat": 0.0000000000,
  "timezone": "Asia/Jakarta"
}


Hewan
json
Salin
Edit
{"nama": "Ayam Broiler", "suhu_min": 20, "suhu_max": 28, "hu_min": 60, "hu_max": 75}
Sayuran
json
Salin
Edit
{"nama": "Bawang Merah", "suhu_min": 25, "suhu_max": 32, "hu_min": 50, "hu_max": 70}
🤖 Chatbot AI: Contoh Pertanyaan yang Dapat Dijawab
Cuaca di [lokasi]

Bagaimana cuaca di [lokasi]

Suhu tertinggi di [lokasi]

Suhu terendah hari ini di [lokasi]

Kelembapan di [lokasi]

Ringkasan cuaca hari ini di [lokasi]

Summary cuaca [lokasi]

Dimana letak [desa/kecamatan]

Koordinat [desa/kecamatan]

Apa saja hewan yang dapat dicek?

Daftar sayuran yang bisa saya tanyakan

Ingin pelihara ayam hari ini

Hewan apa saja yang cocok diternak di provinsi tertentu berdasarkan suhu rata-rata harian dan kelembapan rata-rata?

Sayuran apa saja yang cocok ditanam di desa tertentu dengan suhu dan kelembapan saat ini?

Di kecamatan mana saja di kabupaten tertentu yang cocok untuk beternak sapi atau menanam cabai?

Suhu maksimum berapa hari ini di suatu kotkab?

Kelembapan rata-rata harian di suatu desa?

Cuaca dominan hari ini di provinsi tertentu?

Desa mana saja di provinsi tertentu yang cuacanya cerah hari ini?

Provinsi mana saja yang cocok untuk menanam tomat jika suhu minimumnya di atas batas tertentu?

Hewan apa saja yang tidak cocok dipelihara di desa tertentu karena suhu terlalu tinggi?

Sayuran apa saja yang tidak cocok ditanam di kecamatan tertentu karena kelembapan terlalu rendah?

Berapa suhu rata-rata di kabupaten tertentu hari ini?

Suhu tertinggi dan terendah di desa tertentu hari ini?

Bagaimana ramalan cuaca harian di suatu lokasi?

Cuaca saat ini di desa tertentu?

Suhu dan kelembapan saat ini di desa tertentu?

Lokasi mana saja yang kelembapannya sesuai untuk hewan tertentu?

Lokasi mana saja yang suhunya sesuai untuk sayuran tertentu?

Desa mana saja di provinsi tertentu yang suhunya mendekati suhu ideal untuk kelinci?

Kecamatan mana saja yang cocok untuk menanam selada jika dilihat dari suhu dan kelembapan rata-rata?

Bagaimana cuaca dominan di provinsi tertentu hari ini?

Apakah suhu saat ini di suatu desa cocok untuk ayam petelur?

Di kabupaten mana saja kelembapan saat ini cukup tinggi untuk menanam bayam?

Kecamatan mana saja yang cuaca dominannya mendung hari ini?

Provinsi mana saja yang suhu minimumnya sesuai untuk menanam wortel?

Desa mana saja di provinsi tertentu yang suhunya paling rendah hari ini?

Desa mana saja yang suhu maksimumnya paling tinggi hari ini?

Kabupaten mana yang kelembapan rata-ratanya paling rendah?

Desa mana saja yang punya suhu rata-rata mendekati suhu ideal untuk memelihara kambing?

Bagaimana suhu maksimum, minimum, rata-rata, dan kelembapan rata-rata di desa tertentu?

Lokasi mana saja yang tidak cocok untuk hewan tertentu karena suhu terlalu rendah atau kelembapan terlalu tinggi?

Di provinsi mana saja yang cocok untuk menanam kangkung berdasarkan suhu dan kelembapan rata-rata harian?

🖥️ Teknologi

-> Frontend 
React
React Leaflet
Axios
Framer Motion
React Toastify
React Icons
React Markdown

Backend 
makefile
Salin
Edit
Flask==3.1.1
APScheduler==3.11.0
requests==2.32.4
psycopg2==2.9.10
torch==2.3.0
transformers==4.41.2
tzlocal==5.3.1
