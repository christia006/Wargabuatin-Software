import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';
// Tidak ada impor CSS di sini karena styling peta ditangani di App.css

// Komponen untuk mengontrol aksi peta seperti flyTo
// Memungkinkan perubahan tampilan peta berdasarkan lokasi yang ditemukan/dicari
export function MapController({ myLocation, searchedLocation }) {
  const map = useMap(); // Hook dari react-leaflet untuk mengakses instance peta

  // Efek untuk memindahkan peta ke lokasi pengguna
  useEffect(() => {
    if (myLocation) {
      map.flyTo([myLocation.lat, myLocation.lon], 13, { duration: 1.5 });
    }
  }, [myLocation, map]);

  // Efek untuk memindahkan peta ke lokasi yang dicari dari input pencarian
  useEffect(() => {
    if (searchedLocation && searchedLocation.lat && searchedLocation.lon) {
      map.flyTo([searchedLocation.lat, searchedLocation.lon], 13, { duration: 1.5 });
    }
  }, [searchedLocation, map]);

  return null; // Komponen ini tidak merender elemen UI, hanya melakukan interaksi dengan peta
}