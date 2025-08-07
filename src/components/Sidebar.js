import React, { useEffect, useState } from 'react';
import api from '../api';

export default function Sidebar({ selectedAdm4 }) {
  const [cuaca, setCuaca] = useState([]);
  useEffect(() => {
    if (selectedAdm4) {
      api.get(`/cuaca/${selectedAdm4}`).then(res => setCuaca(res.data));
    }
  }, [selectedAdm4]);
  return (
    <div style={{ width: '300px', overflowY: 'auto', background: '#f9f9f9', padding: '1rem' }}>
      <h2>Prakiraan Cuaca</h2>
      {cuaca.map((item, idx) => (
        <div key={idx}>
          <b>{item[0]}</b><br/>
          Suhu: {item[1]} °C<br/>
          Kelembapan: {item[2]}%<br/>
          Cuaca: {item[3]}
        </div>
      ))}
    </div>
  );
}
