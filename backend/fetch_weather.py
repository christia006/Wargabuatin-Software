import json
import requests
from db import get_db_connection

def fetch_all_weather():
    conn = get_db_connection()
    cur = conn.cursor()

    with open('data/links_api.json') as f:
        links = json.load(f)

    for link in links:
        adm4 = link['adm4']
        url = link['url']
        try:
            res = requests.get(url)
            data = res.json()
            for group in data['data']:
                for period in group['cuaca'][0]:
                    datetime = period['datetime']
                    t = period['t']
                    hu = period['hu']
                    desc = period['weather_desc']
                    cur.execute("""
                        INSERT INTO cuaca_prediksi (adm4, datetime, t, hu, weather_desc)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (adm4, datetime) DO UPDATE
                        SET t=EXCLUDED.t, hu=EXCLUDED.hu, weather_desc=EXCLUDED.weather_desc
                    """, (adm4, datetime, t, hu, desc))
        except Exception as e:
            print(f"Error fetch {adm4}: {e}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    fetch_all_weather()
