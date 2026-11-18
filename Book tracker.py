import json
from datetime import date, timedelta
import os
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data buku.json")
RIWAYAT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Riwayat membaca.json")
HEWAN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Hewan.json")

def baca_riwayat():
    if os.path.exists(RIWAYAT_FILE):
        try:
            with open(RIWAYAT_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

# JUDUL*
def tampilkan_judul(teks, warna="35"): #35 itu kode warna ungu dari ANSI escape code
    kode_warna = f"\033[{warna}m"
    reset_warna = "\033[0m"
    garis = "=" *(len(teks) + 18)
    print(f"{kode_warna}{garis}")
    print(f"{kode_warna}{teks.center(len(garis))}")
    print(f"{kode_warna}{garis}{reset_warna}")
tampilkan_judul("📚 Selamat datang di Book Tracker 📚")
print()
# TAMPILAN MENU
MERAH = "\033[31m"
HIJAU = "\033[32m"
KUNING = "\033[33m"
BIRU = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
RESET = "\033[0m"

def warna(teks, kode):
    return f"{kode}{teks}{RESET}"

def tampilan_menu(hewan):
    print(CYAN + "=" * 5 + " MENU BOOK TRACKER " + "=" * 5 + RESET)
    emoji = ["🥚", "🐣", "🐥", "🐔"][min(hewan["total_baca"] // 3, 3)]
    print(f"{emoji} {hewan['nama']} - {kondisi_hewan(hewan)}")
    print(MAGENTA + "1." + RESET + "🔎 Cari Buku ")
    print(MAGENTA + "2." + RESET + "➕ Tambah Buku ")
    print(MAGENTA + "3." + RESET + "🗃️  Tampilkan Daftar Buku ")
    print(MAGENTA + "4." + RESET + "📑 Riwayat Membaca ")
    print(MAGENTA + "5." + RESET + "🚪 Keluar")


# ---------- FUNGSI BANTU (baca & simpan file) ----------
def baca_data():
    if not os.path.exists(FILE):
        print(MERAH + "⚠️ File tidak ditemukan di: " + RESET)
        print(FILE)
        return []

    try:
        with open(FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        print(MERAH + "⚠️ Isi file JSON ada yang salah (cek koma/kurung/kutip):" + RESET)
        print(error)
        return []

    if isinstance(data, dict):
        return data.get("buku", [])
    return data

def simpan_data(data_buku):
    with open(FILE, "w", encoding="utf-8") as file:
        json.dump({"buku": data_buku}, file, indent=2, ensure_ascii=False)

def simpan_riwayat(riwayat):
    with open(RIWAYAT_FILE, "w", encoding="utf-8") as file:
        json.dump(riwayat, file, indent=2, ensure_ascii=False)

def baca_hewan():
    if os.path.exists(HEWAN_FILE):
        with open(HEWAN_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def simpan_hewan(hewan):
    with open(HEWAN_FILE, "w", encoding="utf-8") as file:
        json.dump(hewan, file, indent=2, ensure_ascii=False)

# ---------- HEWAN PELIHARAAN ----------
def buat_hewan():
    nama = input("Beri nama hewan peliharaanmu: ")
    hewan = {"nama": nama, "terakhir_baca": date.today().isoformat(), "total_baca": 0}
    simpan_hewan(hewan)
    return hewan

def kondisi_hewan(hewan):
    bolos = (date.today() - date.fromisoformat(hewan["terakhir_baca"])).days
    if bolos <= 1:
        return "Sehat"
    elif bolos == 2:
        return "Sakit"
    elif bolos == 3:
        return "Sakit parah"
    return "Mati"

def rawat_hewan(hewan):
    hewan["terakhir_baca"] = date.today().isoformat()
    hewan["total_baca"] += 1
    simpan_hewan(hewan)
    print(HIJAU + f"{hewan['nama']} senang kamu membaca 🐾" + RESET)

#---------- MENU 1: CARI BUKU ----------
def cari_buku():
    data_buku = baca_data()
    if len(data_buku) == 0:
        print(MERAH + "Belum ada data buku 🙁." + RESET)
        return

    kata_kunci = input("Masukkan judul buku yang dicari: ")
    ditemukan = 0
    for buku in data_buku:
        if kata_kunci.lower() in buku["judul"].lower():
            print(f"- {buku['judul']} | {buku['penulis']} | {buku['jumlah_halaman']} hlm | {buku['genre']}")
            ditemukan += 1

    if ditemukan == 0:
        print(MERAH + "Buku tidak ditemukan." + RESET)
    else:
        print(HIJAU + f"{ditemukan} buku ditemukan." + RESET)

# ---------- MENU 2: TAMBAH BUKU ----------
def tambah_buku():
    data_buku = baca_data()

    judul = input("Judul buku     : ")
    penulis = input("Penulis        : ")
    genre = input("Genre          : ")

    halaman = input("Jumlah halaman : ")
    while not halaman.isdigit():
        print(MERAH + "⚠️ Harus berupa angka!" + RESET)
        halaman = input("Jumlah halaman : ")

    buku_baru = {
        "judul": judul,
        "penulis": penulis,
        "jumlah_halaman": int(halaman),
        "genre": genre
    }
    data_buku.append(buku_baru)
    simpan_data(data_buku)
    print(HIJAU + "Buku berhasil ditambahkan!" + RESET)

# ---------- MENU 3: TAMPILKAN DAFTAR BUKU ----------
def tampilkan_daftar():
    data_buku = baca_data()
    if len(data_buku) == 0:
        print(MERAH + "Belum ada data buku." + RESET)
        return

    print(HIJAU + "=" * 79 + RESET)
    print(KUNING + f"|{'No':<4}|{'Judul':<25}| {'Hlm':<6}|{'Penulis':<20}|{'Genre':<18}|" + RESET)
    print(HIJAU + "=" * 79 + RESET)

    nomor = 1
    for buku in data_buku:
        print(f"|{nomor:<4}|{buku['judul'][:23]:<25}|{buku['jumlah_halaman']:<6}|{buku['penulis'][:18]:<20}|{buku['genre'][:16]:<18}|")
        nomor += 1
        print("-" * 79)
    print(HIJAU + "=" * 79 + RESET)
# ---------- MENU 4: RIWAYAT MEMBACA ----------
def riwayat_membaca(hewan):
    print("1. Lihat riwayat")
    print("2. Catat buku yang sudah selesai dibaca")
    sub = input("Pilih (1/2): ")
    riwayat = baca_riwayat()

    if sub == "1":
        if len(riwayat) == 0:
            print(MERAH + "Riwayat masih kosong." + RESET)
        else:
            for item in riwayat:
                print(f"- {item['judul']} (selesai: {item['tanggal']})")
    elif sub == "2":
        judul = input("Judul buku yang selesai dibaca: ")
        tanggal = input("Tanggal selesai (contoh 11-11-2026): ")
        riwayat.append({"judul": judul, "tanggal": tanggal})
        simpan_riwayat(riwayat)
        rawat_hewan(hewan) 
        print(HIJAU + "Riwayat berhasil dicatat!" + RESET)
    else:
        print(MERAH + "Pilihan tidak valid." + RESET)
# ---------- PROGRAM UTAMA ----------
hewan = baca_hewan()
if hewan is None:
    hewan = buat_hewan()
elif kondisi_hewan(hewan) == "Mati":
    print(MERAH + f"{hewan['nama']} mati 🪦 karena lama tidak dirawat." + RESET)
    hewan = buat_hewan()

tampilan_menu(hewan)
pilihan = input("Pilih menu (1-5): ")

while pilihan != "5":
    print()
    if pilihan == "1":
        cari_buku()
    elif pilihan == "2":
        tambah_buku()
    elif pilihan == "3":
        tampilkan_daftar()
    elif pilihan == "4":
        riwayat_membaca(hewan)
    else:
        print(MERAH + "⚠️ Pilihan tidak valid, pilih 1-5." + RESET)

    print()
    tampilan_menu(hewan)
    pilihan = input("Pilih menu (1-5): ")

print(KUNING + "Terima kasih, sampai jumpa 🤍!" + RESET)