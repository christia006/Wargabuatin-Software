# models.py
CREATE_TABLES = [
"""
CREATE TABLE IF NOT EXISTS links_api (
    id SERIAL PRIMARY KEY,
    adm4 VARCHAR(20) UNIQUE,
    desa TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    url TEXT
);
""",
"""
CREATE TABLE IF NOT EXISTS cuaca_prediksi (
    id SERIAL PRIMARY KEY,
    adm4 VARCHAR(20),
    datetime TIMESTAMP,
    t REAL,
    hu REAL,
    weather_desc TEXT,
    UNIQUE(adm4, datetime)
);
""",
"""
CREATE TABLE IF NOT EXISTS hewan_cocok (
    id SERIAL PRIMARY KEY,
    nama TEXT UNIQUE,
    suhu_min REAL,
    suhu_max REAL,
    hu_min REAL,
    hu_max REAL
);
""",
"""
CREATE TABLE IF NOT EXISTS sayuran_cocok (
    id SERIAL PRIMARY KEY,
    nama TEXT UNIQUE,
    suhu_min REAL,
    suhu_max REAL,
    hu_min REAL,
    hu_max REAL
);
"""
]
