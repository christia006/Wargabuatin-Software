import psycopg2
from config import DB_CONFIG
from models import CREATE_TABLES
from default_data import LINKS_API_DATA, HEWAN_COCOK_DATA, SAYURAN_COCOK_DATA

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Buat tabel
    for sql in CREATE_TABLES:
        cur.execute(sql)
    conn.commit()

    # Cek & insert data default jika kosong
    insert_if_empty(cur, 'links_api', LINKS_API_DATA)
    insert_if_empty(cur, 'hewan_cocok', HEWAN_COCOK_DATA)
    insert_if_empty(cur, 'sayuran_cocok', SAYURAN_COCOK_DATA)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ DB siap dan data default sudah dimasukkan (jika belum ada).")

def insert_if_empty(cur, table_name, data_list):
    cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cur.fetchone()[0]
    if count == 0 and data_list:
        print(f"📝 Mengisi data default ke tabel {table_name} ...")
        if table_name == 'links_api':
            for item in data_list:
                cur.execute("""
                    INSERT INTO links_api (adm4, desa, lat, lon, url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (adm4) DO NOTHING;
                """, (item['adm4'], item['desa'], item['lat'], item['lon'], item['url']))
        else:  # hewan_cocok & sayuran_cocok
            for item in data_list:
                cur.execute(f"""
                    INSERT INTO {table_name} (nama, suhu_min, suhu_max, hu_min, hu_max)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (nama) DO NOTHING;
                """, (item['nama'], item['suhu_min'], item['suhu_max'], item['hu_min'], item['hu_max']))
        print(f"✅ Data default dimasukkan ke {table_name}.")
