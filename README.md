<div align="center">

# 🌾 **Wargabantuin**  
*Aplikasi cerdas bantu petani & peternak memilih hewan ternak dan sayuran sesuai cuaca terkini.*

[![last commit](https://img.shields.io/badge/last%20commit-today-brightgreen)](#)
[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](#)
[![Flask](https://img.shields.io/badge/Flask-API-green?logo=flask)](#)

*Built with the tools and technologies:*

![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61dafb)
![React Leaflet](https://img.shields.io/badge/React_Leaflet-008000?logo=leaflet&logoColor=white)
![Axios](https://img.shields.io/badge/Axios-5A29E4?logo=axios&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?logo=framer&logoColor=white)
![React Toastify](https://img.shields.io/badge/React_Toastify-FB923C?logo=react&logoColor=white)
![React Icons](https://img.shields.io/badge/React_Icons-61DAFB?logo=react&logoColor=white)
![React Markdown](https://img.shields.io/badge/React_Markdown-000000?logo=markdown&logoColor=white)

![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)
![APScheduler](https://img.shields.io/badge/APScheduler-FFCA28?logo=python&logoColor=black)
![Requests](https://img.shields.io/badge/Requests-000000?logo=python&logoColor=white)
![psycopg2](https://img.shields.io/badge/psycopg2-336791?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-FFD43B?logo=python&logoColor=black)
![tzlocal](https://img.shields.io/badge/tzlocal-3776AB?logo=python&logoColor=white)

</div>

---

## ✨ Fitur Utama
- Rekomendasi hewan & sayuran berbasis cuaca (skor 0–100)
- Peta interaktif
- Chatbot AI untuk tanya jawab langsung
- Data selalu update otomatis dari BMKG

---

## 🔄 Alur Singkat
```txt
Pengguna ➜ Frontend (React) 
       ➜ Backend API (Flask)
           ➜ Auto cache data BMKG
           ➜ Filter & analisis data
           ➜ AI rekomendasi & chatbot
       ➜ Frontend tampilkan peta & jawaban
