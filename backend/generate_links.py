import json

PROVINCE_CODES = [
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "21", "31", "32", "33",
    "34", "35", "36", "51", "52", "53", "61", "62", "63", "64", "65", "71", "72",
    "73", "74", "75", "76", "81", "82", "91", "92"
]

result = []

# Atur range sesuai kebutuhan
kab_range = range(1, 3)       # contoh: hanya 2 kabupaten dulu (01–02)
kec_range = range(1, 3)       # contoh: hanya 2 kecamatan dulu (01–02)
desa_range = range(2001, 2004)  # contoh: hanya 3 desa (2001–2003)

for prov in PROVINCE_CODES:
    for kab_num in kab_range:
        kab_code = f"{prov}.{kab_num:02d}"
        kec_codes = [f"{kab_code}.{kec_num:02d}" for kec_num in kec_range]

        # Loop desa dulu, lalu kecamatan: supaya urut desa per kecamatan seperti yg diinginkan
        for desa_num in desa_range:
            for kec_code in kec_codes:
                adm4 = f"{kec_code}.{desa_num}"
                url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
                result.append({"adm4": adm4, "url": url})

print(f"✅ Total generated: {len(result)}")

# Simpan ke file
with open("data/links_api.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("🎉 links_api.json berhasil dibuat!")
