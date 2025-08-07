import React, { useRef, useCallback, useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

export default function ReportModal({
    showReportModal,
    setShowReportModal,
    reportData,
    setReportData,
    geocodeLocation,
    initialMapCenter,
    setAllLaporan
}) {
    const debounceTimeoutRef = useRef(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submissionMessage, setSubmissionMessage] = useState('');
    const [successExtraMessage, setSuccessExtraMessage] = useState(''); // ✅ tambahan

    useEffect(() => {
        if (!showReportModal) {
            setReportData({
                lokasi: '', kategori: '', deskripsi: '', waktu: '', kontak: '',
                lat: '', lon: '', setuju: false
            });
            setSubmissionMessage('');
            setSuccessExtraMessage(''); // ✅ reset saat modal ditutup
        }
    }, [showReportModal, setReportData]);

    const debouncedGeocode = useCallback((locationName) => {
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
        }
        debounceTimeoutRef.current = setTimeout(async () => {
            if (locationName.trim().length > 2) {
                setSubmissionMessage('Mencari koordinat lokasi...');
                const geoResult = await geocodeLocation(locationName);
                if (geoResult) {
                    setReportData(prev => ({
                        ...prev,
                        lat: geoResult.lat,
                        lon: geoResult.lon
                    }));
                    setSubmissionMessage(`Koordinat ditemukan: ${geoResult.lat.toFixed(6)}, ${geoResult.lon.toFixed(6)}`);
                } else {
                    setReportData(prev => ({ ...prev, lat: '', lon: '' }));
                    setSubmissionMessage('Lokasi tidak ditemukan, mohon periksa ejaan.');
                }
            } else {
                setReportData(prev => ({ ...prev, lat: '', lon: '' }));
                setSubmissionMessage('');
            }
        }, 800);
    }, [geocodeLocation, setReportData]);

    const handleReportChange = (e) => {
        const { name, value, type, checked } = e.target;
        let newReportData = { ...reportData };

        if (name === 'lokasi') {
            newReportData = { ...newReportData, lokasi: value };
            debouncedGeocode(value);
        } else if (type === 'checkbox') {
            newReportData = { ...newReportData, [name]: checked };
        } else {
            newReportData = { ...newReportData, [name]: value };
        }
        setReportData(newReportData);
    };

    const handleReportSubmit = async () => {
        if (!reportData.setuju) {
            setSubmissionMessage('Mohon centang persetujuan sebelum mengirim laporan.');
            return;
        }

        if (!reportData.lokasi.trim() || !reportData.deskripsi.trim()) {
            setSubmissionMessage('Lokasi dan Deskripsi wajib diisi.');
            return;
        }

        setIsSubmitting(true);
        setSubmissionMessage('Mengirim laporan...');
        setSuccessExtraMessage(''); // reset

        let finalLat = reportData.lat;
        let finalLon = reportData.lon;

        if (reportData.lokasi && (!reportData.lat || !reportData.lon)) {
            const geoResult = await geocodeLocation(reportData.lokasi);
            if (geoResult) {
                finalLat = geoResult.lat;
                finalLon = geoResult.lon;
            } else {
                finalLat = initialMapCenter[0];
                finalLon = initialMapCenter[1];
                setSubmissionMessage('Lokasi yang Anda masukkan tidak dapat ditemukan, laporan akan ditandai di pusat peta Indonesia.');
            }
        } else if (!reportData.lokasi.trim()) {
            finalLat = initialMapCenter[0];
            finalLon = initialMapCenter[1];
            setSubmissionMessage('Anda tidak mengisi lokasi, laporan akan ditandai di pusat peta Indonesia.');
        }

        try {
            const reportDataToSend = {
                ...reportData,
                lat: finalLat,
                lon: finalLon,
                waktu: reportData.waktu || new Date().toISOString()
            };
            delete reportDataToSend.setuju;

            await axios.post('/api/laporan', reportDataToSend);
            setSubmissionMessage('Laporan berhasil dikirim!');
            setSuccessExtraMessage('Berhasil dilaporkan dan laporan tampil di halaman Peta dengan penanda warna hijau'); // ✅ tambahan

            const res = await axios.get('/api/all_laporan');
            setAllLaporan(res.data.laporan || []);

            setTimeout(() => {
                setShowReportModal(false);
            }, 1500);
        } catch (e) {
            console.error('Error submitting report:', e);
            setSubmissionMessage('Gagal mengirim laporan. Silakan coba lagi nanti.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <AnimatePresence>
            {showReportModal && (
                <motion.div
                    className="modal-bg"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                >
                    <motion.div
                        className="modal-card"
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <h3>📝 Buat Laporan Baru</h3>
                        <input
                            name="lokasi"
                            placeholder="Nama Lokasi (contoh: Jalan Merdeka 12)"
                            value={reportData.lokasi}
                            onChange={handleReportChange}
                            disabled={isSubmitting}
                            required
                        />
                        <input
                            name="lat"
                            placeholder="Latitude (Terisi Otomatis)"
                            value={reportData.lat ? reportData.lat.toFixed(6) : ''}
                            disabled
                        />
                        <input
                            name="lon"
                            placeholder="Longitude (Terisi Otomatis)"
                            value={reportData.lon ? reportData.lon.toFixed(6) : ''}
                            disabled
                        />
                        <select
                            name="kategori"
                            value={reportData.kategori}
                            onChange={handleReportChange}
                            disabled={isSubmitting}
                        >
                            <option value="">Pilih Kategori (Opsional)</option>
                            <option value="Bencana Alam">Bencana Alam</option>
                            <option value="Kecelakaan">Kecelakaan</option>
                            <option value="Kesehatan">Kesehatan</option>
                            <option value="Keamanan">Keamanan</option>
                            <option value="Infrastruktur">Infrastruktur</option>
                            <option value="Lingkungan">Lingkungan</option>
                            <option value="Lain-lain">Lain-lain</option>
                        </select>
                        <textarea
                            name="deskripsi"
                            placeholder="Deskripsi masalah atau kejadian (wajib diisi)"
                            value={reportData.deskripsi}
                            onChange={handleReportChange}
                            rows="1"
                            disabled={isSubmitting}
                            required
                        ></textarea>
                        <input
                            type="datetime-local"
                            name="waktu"
                            value={reportData.waktu}
                            onChange={handleReportChange}
                            disabled={isSubmitting}
                        />
                        <input
                            name="kontak"
                            placeholder="Kontak (Email/No. Telepon - Opsional)"
                            value={reportData.kontak}
                            onChange={handleReportChange}
                            disabled={isSubmitting}
                        />
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                name="setuju"
                                checked={reportData.setuju}
                                onChange={handleReportChange}
                                disabled={isSubmitting}
                                required
                            />
                            <span>Saya setuju data ini dibagikan ke publik.</span>
                        </label>

                        {submissionMessage && (
                            <motion.p
                                className={`submission-message ${submissionMessage.includes('berhasil') ? 'success' : (submissionMessage.includes('gagal') || submissionMessage.includes('tidak ditemukan') || submissionMessage.includes('wajib diisi') || submissionMessage.includes('Mohon centang')) ? 'error' : ''}`}
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.3 }}
                            >
                                {submissionMessage}
                            </motion.p>
                        )}

                        {successExtraMessage && ( // ✅ tambahan
                            <motion.p
                                className="submission-message success"
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.3 }}
                            >
                                {successExtraMessage}
                            </motion.p>
                        )}

                        <div className="modal-btns">
                            <button onClick={() => setShowReportModal(false)} disabled={isSubmitting}>Batal</button>
                            <button onClick={handleReportSubmit} disabled={isSubmitting}>
                                {isSubmitting ? 'Mengirim...' : 'Kirim Laporan'}
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
