import React from 'react';
import { motion } from 'framer-motion';

// Komponen Deskripsi Proyek
export default function ProjectDescription() {
  return (
    <motion.div
      className="project-description"
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
    >
      <div className="description-header">
        🌿 Wargabantuin: Aplikasi Cerdas untuk Petani dan Peternak di Indonesia
      </div>

      <div className="description-section">
        <h4 className="section-title">✨ Tujuan Utama Aplikasi</h4>
        <p>Wargabantuin membantu petani & peternak memilih hewan ternak dan tanaman sayuran paling cocok berdasarkan data iklim terbaru dari BMKG. Dengan peta interaktif & Chatbot AI, kami ingin mengurangi risiko kerugian akibat cuaca, demi pertanian dan peternakan berkelanjutan.</p>
        <p>⚠️ Saat ini hanya mendukung ±1000 lokasi (sekitar 20 lokasi per provinsi). Lokasi rumah Anda akan dicocokkan ke lokasi terdekat di peta, demi efisiensi server & penyimpanan.</p>
      </div>

      <div className="description-section">
        <h4 className="section-title">📌 Bagaimana Aplikasi Bekerja</h4>
        <ol>
          <li><span className="step-title">Memahami Kebutuhan</span>
            <p>Mencari hewan & sayuran yang cocok dengan cuaca lokal Anda.</p></li>
          <li><span className="step-title">Mengumpulkan Data</span>
            <p>Data cuaca dari BMKG dan data suhu/kelembapan ideal berbagai komoditas.</p>
            <pre className="code-block"><code>
{`// Contoh Data Lokasi
{
  "provinsi": "Sumatera Utara",
  "kotkab": "Tapanuli Tengah",
  "kecamatan": "Barus",
  "desa": "Kampung Solok",
  "lon": 98.38,
  "lat": 2.06,
  "timezone": "Asia/Jakarta"
}

// Contoh Data Hewan
{"nama":"Ayam Broiler","suhu_min":20,"suhu_max":28,"hu_min":60,"hu_max":75}

// Contoh Data Sayuran
{"nama":"Bawang Merah","suhu_min":25,"suhu_max":32,"hu_min":50,"hu_max":70}`}
            </code></pre>
          </li>
          <li><span className="step-title">Mengolah Data</span>
            <p>Menghitung suhu & kelembapan saat ini, suhu harian, dan rata-rata historis.</p></li>
          <li><span className="step-title">Memberikan Rekomendasi</span>
            <p>Skor kecocokan (0–100) dan alasan singkat kenapa cocok atau tidak.</p></li>
          <li><span className="step-title">Menguji & Memperbaiki</span>
            <p>Rekomendasi terus diuji dan diperbaiki bersama petani & peternak.</p></li>
          <li><span className="step-title">Menyajikan Aplikasi</span>
            <ul>
              <li><strong>Sistem Pengambil Data Otomatis</strong>: update rutin data BMKG</li>
              <li><strong>Pusat Data (API)</strong>: menyediakan data & rekomendasi</li>
              <li><strong>Tampilan Website</strong>: peta interaktif & antarmuka</li>
              <li><strong>Chatbot AI</strong>: menjawab pertanyaan pengguna</li>
            </ul></li>
        </ol>
      </div>

    <div className="description-section">
  <h4 className="section-title">🧠 Contoh Pertanyaan Lengkap yang Bisa Ditanyakan</h4>
  <div className="questions-list">
  <ul>
  <li>“Data provinsi apa saja yang tersedia”</li>
  <li>“Data kota/kotkab apa saja yang tersedia”</li>
  <li>“Kecamatan apa saja yang tersedia”</li>
  <li>“Desa apa saja yang tersedia”</li>
  <li>“Apa saja hewan yang dapat dicek”</li>
  <li>“Daftar sayuran”</li>
  <li>“[Nama Hewan] cocok di mana?”</li>
  <li> “[Nama Sayuran] cocok di mana?”</li>
   <li>“Dimana letak [nama_lokasi]”</li>
   <li>“Di mana posisi [nama_lokasi]”</li>
      <li>“"Koordinat [nama lokasi]”</li>
  <li>“Bagaimana cuaca di [nama lokasi]”</li>
  <li>“Suhu tertinggi di [nama lokasi]”</li>
  <li>“Suhu terendah di [nama lokasi]”</li>
  <li>“Kelembapan di [nama lokasi]”</li>
  <li>“Ringkasan cuaca di [nama lokasi]”</li>
</ul>



           <p>✅ <strong>Keterangan input:</strong></p>
          <ul>
        [nama lokasi] → kota,provinsi, kabupaten, kecamatan, atau desa<br/>
            [nama hewan] → ayam, kambing, sapi, dll<br/>
            [nama sayuran] → selada, tomat, bayam, dll<br/>
            [angka suhu tertentu] → misalnya 20°C, 22°C, dll
          </ul>

        
        </div>
      </div>

      <div className="description-footer">
        &copy; {new Date().getFullYear()} Team RUCE. All rights reserved.
      </div>
    </motion.div>
  );
}
