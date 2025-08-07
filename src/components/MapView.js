import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import api from '../api';
import 'leaflet/dist/leaflet.css';

// Komponen tombol untuk cari lokasi user
function LocateButton() {
  const map = useMap();

  const handleLocate = () => {
    if (!navigator.geolocation) {
      alert('Geolocation tidak didukung browser!');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        console.log('Lokasi user:', latitude, longitude);
        map.flyTo([latitude, longitude], 13); // pindahkan peta
        // Tambahkan marker? (opsional, lihat catatan bawah)
      },
      (err) => {
        console.error(err);
        alert('Gagal mendapatkan lokasi.');
      }
    );
  };

  return (
    <button
      onClick={handleLocate}
      style={{
        position: 'absolute',
        top: 10,
        left: 10,
        zIndex: 1000,
        padding: '6px 12px',
        background: '#007bff',
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}
    >
      Cari Lokasi Saya
    </button>
  );
}

export default function MapView({ onSelect }) {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    api.get('/locations')
      .then(res => {
        console.log('Data lokasi:', res.data);
        setLocations(res.data);
      })
      .catch(err => console.error('Gagal fetch lokasi:', err));
  }, []);

  return (
    <div style={{ position: 'relative', height: '100vh' }}>
      <MapContainer center={[-0.7893, 113.9213]} zoom={5} style={{ height: '100%', width: '100%' }}>
        <TileLayer url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />

        {locations.map((loc, idx) => (
          <Marker
            key={idx}
            position={[loc.lat, loc.lon]}  // pastikan loc.lat & loc.lon ada!
            eventHandlers={{ click: () => onSelect(loc.adm4) }}
          >
            <Popup>{loc.desa}</Popup>
          </Marker>
        ))}

        {/* Tombol muncul di atas peta */}
        <LocateButton />
      </MapContainer>
    </div>
  );
}
