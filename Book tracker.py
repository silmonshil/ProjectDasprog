import json
import os
from datetime import date, timedelta

# ---------- LOKASI FILE DATA ----------
FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(FOLDER, "Data buku.json")                # daftar semua buku (katalog)
RIWAYAT_FILE = os.path.join(FOLDER, "Riwayat membaca.json")  # riwayat buku yang selesai dibaca (rak Sudah dibaca)
PET_FILE = os.path.join(FOLDER, "Hewan.json")                # data Streak Pet
RAK_FILE = os.path.join(FOLDER, "Rak buku.json")             # rak ingin, sedang, dan favorit (dibuat otomatis)

# ---------- WARNA ----------
MERAH = "\033[31m"
HIJAU = "\033[32m"
KUNING = "\033[33m"
BIRU = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
RESET = "\033[0m"

# Kode rak -> nama yang ditampilkan
NAMA_RAK = {"ingin": "Ingin dibaca", "sedang": "Sedang dibaca", "sudah": "Sudah dibaca"}


# ---------- JUDUL ----------
def tampilkan_judul(teks, warna="35"):  # 35 itu kode warna ungu dari ANSI escape code
    kode_warna = f"\033[{warna}m"
    reset_warna = "\033[0m"
    garis = "=" * (len(teks) + 18)
    print(f"{kode_warna}{garis}")
    print(f"{kode_warna}{teks.center(len(garis))}")
    print(f"{kode_warna}{garis}{reset_warna}")


# ---------- TAMPILAN MENU ----------
def tampilan_menu(pet):
    print(CYAN + "=" * 5 + " MENU BOOK TRACKER " + "=" * 5 + RESET)
    print(f"{emoji_pet(pet)} {pet['nama']} - {kondisi_pet(pet)} 🔥 {streak_sekarang(pet)} hari")
    print(MAGENTA + "1." + RESET + "🔎 Cari Buku ")
    print(MAGENTA + "2." + RESET + "🗃️  Rak Buku ")
    print(MAGENTA + "3." + RESET + "📑 Sedang dibaca ")
    print(MAGENTA + "4." + RESET + "🔥 Streak ")
    print(MAGENTA + "5." + RESET + "🚪 Keluar")


# ---------- FUNGSI BANTU: DAFTAR BUKU (Data buku.json) ----------
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
        data = data.get("buku", [])

    # Daftar buku hanya berisi identitas buku. Isian lama tentang rak dibuang.
    for buku in data:
        for kunci_lama in ("rak", "halaman_dibaca", "favorit"):
            buku.pop(kunci_lama, None)
    return data

def simpan_data(data_buku):
    with open(FILE, "w", encoding="utf-8") as file:
        json.dump({"buku": data_buku}, file, indent=2, ensure_ascii=False)

def temukan_buku(data_buku, kata_kunci):
    """Cari satu buku di daftar buku. Judul yang persis sama didahulukan."""
    kata_kunci = kata_kunci.lower()
    for buku in data_buku:
        if buku["judul"].lower() == kata_kunci:
            return buku
    for buku in data_buku:
        if kata_kunci in buku["judul"].lower():
            return buku
    return None

def penulis_dari(data_buku, judul):
    for buku in data_buku:
        if buku["judul"] == judul:
            return buku["penulis"]
    return "-"

def hitung_persen(dibaca, jumlah_halaman):
    return dibaca * 100 // jumlah_halaman


# ---------- FUNGSI BANTU: RAK BUKU (Riwayat membaca.json dan Rak buku.json) ----------
def baca_riwayat():
    if os.path.exists(RIWAYAT_FILE):
        try:
            with open(RIWAYAT_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

def simpan_riwayat(riwayat):
    with open(RIWAYAT_FILE, "w", encoding="utf-8") as file:
        json.dump(riwayat, file, indent=2, ensure_ascii=False)

def tanggal_selesai():
    """Judul (huruf kecil) -> tanggal selesai dibaca, diambil dari Riwayat membaca.json."""
    return {item["judul"].lower(): item["tanggal"] for item in baca_riwayat()}

def baca_rak():
    rak_data = {}
    if os.path.exists(RAK_FILE):
        try:
            with open(RAK_FILE, "r", encoding="utf-8") as file:
                rak_data = json.load(file)
        except json.JSONDecodeError:
            rak_data = {}
    rak_data.setdefault("ingin", [])
    rak_data.setdefault("sedang", {})   # judul -> halaman yang sudah dibaca
    rak_data.setdefault("favorit", [])

    # Rak Sudah dibaca diambil dari Riwayat membaca.json.
    # Judul di riwayat disamakan dengan judul di daftar buku (huruf besar/kecil tidak dibedakan).
    data_buku = baca_data()
    rak_data["sudah"] = []
    for item in baca_riwayat():
        judul = item["judul"]
        for buku in data_buku:
            if buku["judul"].lower() == judul.lower():
                judul = buku["judul"]
                break
        rak_data["sudah"].append(judul)
    return rak_data

def simpan_rak(rak_data):
    isi_rak = {"ingin": rak_data["ingin"], "sedang": rak_data["sedang"], "favorit": rak_data["favorit"]}
    with open(RAK_FILE, "w", encoding="utf-8") as file:
        json.dump(isi_rak, file, indent=2, ensure_ascii=False)

    # Buku yang baru selesai dibaca dicatat ke Riwayat membaca.json (judul dan tanggal selesai).
    riwayat = baca_riwayat()
    tercatat = [item["judul"].lower() for item in riwayat]
    ada_baru = False
    for judul in rak_data["sudah"]:
        if judul.lower() not in tercatat:
            riwayat.append({"judul": judul, "tanggal": date.today().strftime("%d-%m-%Y")})
            ada_baru = True
    if ada_baru:
        simpan_riwayat(riwayat)

def rak_dari(rak_data, judul):
    """Buku ini ada di rak mana? (None kalau belum masuk rak mana pun)"""
    if judul in rak_data["sedang"]:
        return "sedang"
    if judul in rak_data["sudah"]:
        return "sudah"
    if judul in rak_data["ingin"]:
        return "ingin"
    return None

def pindah_rak(rak_data, judul, tujuan):
    """Pindahkan buku ke rak tujuan (ingin / sedang / sudah). Satu buku hanya di satu rak."""
    if judul in rak_data["ingin"]:
        rak_data["ingin"].remove(judul)
    rak_data["sedang"].pop(judul, None)
    if judul in rak_data["sudah"]:
        rak_data["sudah"].remove(judul)

    if tujuan == "ingin":
        rak_data["ingin"].append(judul)
    elif tujuan == "sedang":
        rak_data["sedang"][judul] = 0
    else:
        rak_data["sudah"].append(judul)

def jadikan_favorit(rak_data, judul):
    if judul not in rak_data["favorit"]:
        rak_data["favorit"].append(judul)

def tampilkan_rak(nama_rak, daftar_judul, data_buku, tanggal=None):
    print(BIRU + f"List buku {nama_rak.lower()}:" + RESET)
    if len(daftar_judul) == 0:
        print(MERAH + "Rak ini masih kosong." + RESET)
        return
    nomor = 1
    for judul in daftar_judul:
        baris = f"{nomor}. {judul} - {penulis_dari(data_buku, judul)}"
        if tanggal and judul.lower() in tanggal:
            baris += f" (selesai: {tanggal[judul.lower()]})"
        print(baris)
        nomor += 1


# ---------- FUNGSI BANTU: STREAK PET (Hewan.json) ----------
def baca_pet():
    if os.path.exists(PET_FILE):
        with open(PET_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def simpan_pet(pet):
    with open(PET_FILE, "w", encoding="utf-8") as file:
        json.dump(pet, file, indent=2, ensure_ascii=False)


# ---------- STREAK PET ----------
def buat_pet():
    nama = input("Beri nama Streak Pet kamu: ")
    kemarin = (date.today() - timedelta(days=1)).isoformat()
    pet = {"nama": nama, "terakhir_baca": kemarin, "total_baca": 0, "streak": 0}
    simpan_pet(pet)
    return pet

def kondisi_pet(pet):
    bolos = (date.today() - date.fromisoformat(pet["terakhir_baca"])).days
    if bolos <= 1:
        return "Sehat"
    elif bolos == 2:
        return "Sakit"
    elif bolos == 3:
        return "Sakit parah"
    return "Mati"

def nyawa_pet(pet):
    kondisi = kondisi_pet(pet)
    if kondisi == "Sehat":
        return 3
    elif kondisi == "Sakit":
        return 2
    elif kondisi == "Sakit parah":
        return 1
    return 0

def emoji_pet(pet):
    return ["🥚", "🐣", "🐥", "🐔"][min(pet["total_baca"] // 3, 3)]

def streak_sekarang(pet):
    hari_ini = date.today().isoformat()
    kemarin = (date.today() - timedelta(days=1)).isoformat()
    if pet["terakhir_baca"] == hari_ini or pet["terakhir_baca"] == kemarin:
        return pet["streak"]
    return 0  # bolos, streak putus

def rawat_pet(pet):
    hari_ini = date.today().isoformat()
    kemarin = (date.today() - timedelta(days=1)).isoformat()
    if pet["terakhir_baca"] != hari_ini:  # baru baca pertama kali hari ini
        if pet["terakhir_baca"] == kemarin:
            pet["streak"] += 1  # kemarin baca juga, streak lanjut
        else:
            pet["streak"] = 1   # sempat bolos, mulai lagi dari 1
        pet["total_baca"] += 1
    pet["terakhir_baca"] = hari_ini
    simpan_pet(pet)
    print(HIJAU + f"{pet['nama']} senang kamu membaca 🐾" + RESET)


# ---------- TAMBAH BUKU (dipakai menu 1, 2, dan 3) ----------
def tambah_buku(judul_awal="", tanya_rak=True):
    data_buku = baca_data()

    if judul_awal:
        judul = judul_awal
        print(f"Judul buku     : {judul}")
    else:
        judul = input("Judul buku     : ")
    penulis = input("Penulis        : ")
    genre = input("Genre          : ")

    halaman = input("Jumlah halaman : ")
    while not halaman.isdigit() or halaman == "0":
        print(MERAH + "⚠️ Harus berupa angka lebih dari 0!" + RESET)
        halaman = input("Jumlah halaman : ")

    buku_baru = {
        "judul": judul,
        "penulis": penulis,
        "jumlah_halaman": int(halaman),
        "genre": genre
    }
    data_buku.append(buku_baru)
    simpan_data(data_buku)
    print(HIJAU + "Buku berhasil ditambahkan ke daftar buku!" + RESET)

    if tanya_rak:
        print("\nMasukkan ke rak mana?")
        print("1. Ingin dibaca")
        print("2. Sedang dibaca")
        print("3. Sudah dibaca")
        print("4. Favorit")
        pilih_rak = input("Pilih rak (1-4): ")
        while pilih_rak not in ("1", "2", "3", "4"):
            print(MERAH + "⚠️ Pilih angka 1 sampai 4!" + RESET)
            pilih_rak = input("Pilih rak (1-4): ")

        rak_data = baca_rak()
        if pilih_rak == "1":
            pindah_rak(rak_data, judul, "ingin")
        elif pilih_rak == "2":
            pindah_rak(rak_data, judul, "sedang")
        else:
            pindah_rak(rak_data, judul, "sudah")
            if pilih_rak == "4":
                jadikan_favorit(rak_data, judul)
        simpan_rak(rak_data)
        nama_rak = ["Ingin dibaca", "Sedang dibaca", "Sudah dibaca", "Favorit"][int(pilih_rak) - 1]
        print(HIJAU + f"Buku masuk ke rak {nama_rak}!" + RESET)
    return buku_baru


# ---------- MENU 1: CARI BUKU ----------
def cari_buku():
    data_buku = baca_data()
    if len(data_buku) == 0:
        print(MERAH + "Belum ada data buku 🙁." + RESET)
        print(KUNING + "Ayo tambahkan buku!" + RESET)
        tambah_buku()
        return

    rak_data = baca_rak()
    kata_kunci = input("Masukkan judul buku yang dicari: ")
    ditemukan = 0
    for buku in data_buku:
        if kata_kunci.lower() in buku["judul"].lower():
            status = rak_dari(rak_data, buku["judul"])
            nama_rak = NAMA_RAK[status] if status else "Belum masuk rak"
            print(f"- {buku['judul']} | {buku['penulis']} | {buku['jumlah_halaman']} hlm | {buku['genre']} | {nama_rak}")
            ditemukan += 1

    if ditemukan == 0:
        print(MERAH + "Buku tidak ditemukan." + RESET)
        print(KUNING + "Ayo tambahkan buku!" + RESET)
        tambah_buku()
        
    else:
        print(HIJAU + f"{ditemukan} buku ditemukan." + RESET)
        jawab = input('\nIngin membuka menu Rak Buku? (y/n): ')
        if jawab.lower() == "y":
            print()
            rak_buku()

# ---------- MENU 2: RAK BUKU ----------
def ingin_dibaca():
    data_buku = baca_data()
    rak_data = baca_rak()
    tampilkan_rak("Ingin dibaca", rak_data["ingin"], data_buku)

    kata_kunci = input("\nKetik judul buku yang ingin dibaca (0 = kembali): ")
    if kata_kunci == "0" or kata_kunci == "":
        return

    buku = temukan_buku(data_buku, kata_kunci)
    if buku is None:
        print(MERAH + "Buku belum ada di daftar buku." + RESET)
        print(KUNING + "Ayo tambahkan datanya dulu!" + RESET)
        buku = tambah_buku(kata_kunci, tanya_rak=False)

    judul = buku["judul"]
    status = rak_dari(rak_data, judul)
    if status is None:
        pindah_rak(rak_data, judul, "ingin")
        simpan_rak(rak_data)
        print(HIJAU + f"'{judul}' masuk ke rak Ingin dibaca!" + RESET)
        print()
        tampilkan_rak("Ingin dibaca", rak_data["ingin"], baca_data())
    else:
        print(KUNING + f"'{judul}' sudah ada di rak {NAMA_RAK[status]}." + RESET)

def daftar_buku():
    """Membuka semua data buku yang tersimpan di Data buku.json (dalam bentuk tabel)."""
    data_buku = baca_data()
    if len(data_buku) == 0:
        print(MERAH + "Belum ada data buku." + RESET)
        return

    rak_data = baca_rak()
    print(HIJAU + "=" * 76 + RESET)
    print(KUNING + f"|{'No':<3}|{'Judul':<20}|{'Penulis':<16}|{'Hlm':<5}|{'Genre':<12}|{'Rak':<13}|" + RESET)
    print(HIJAU + "=" * 76 + RESET)

    nomor = 1
    for buku in data_buku:
        status = rak_dari(rak_data, buku["judul"])
        nama_rak = NAMA_RAK[status] if status else "-"
        print(f"|{nomor:<3}|{buku['judul'][:20]:<20}|{buku['penulis'][:16]:<16}|{buku['jumlah_halaman']:<5}|{buku['genre'][:12]:<12}|{nama_rak:<13}|")
        nomor += 1
        print("-" * 76)
    print(HIJAU + "=" * 76 + RESET)

def rak_buku():
    pilihan = ""
    while pilihan != "5":
        data_buku = baca_data()
        rak_data = baca_rak()

        print(BIRU + "=" * 5 + " RAK BUKU " + "=" * 5 + RESET)
        print(f"1. Ingin dibaca ({len(rak_data['ingin'])})")
        print(f"2. Sudah dibaca ({len(rak_data['sudah'])})")
        print(f"3. Favorit ({len(rak_data['favorit'])})")
        print(f"4. Daftar buku ({len(data_buku)})")
        print("5. Kembali ke menu")
        pilihan = input("Pilih (1-5): ")
        print()

        if pilihan == "1":
            ingin_dibaca()
        elif pilihan == "2":
            tampilkan_rak("Sudah dibaca", rak_data["sudah"], data_buku, tanggal_selesai())
        elif pilihan == "3":
            tampilkan_rak("Favorit", rak_data["favorit"], data_buku)
        elif pilihan == "4":
            daftar_buku()
        elif pilihan != "5":
            print(MERAH + "Pilihan tidak valid, pilih 1-5." + RESET)
        print()


# ---------- MENU 3: SEDANG DIBACA ----------
def sedang_dibaca(pet):
    data_buku = baca_data()
    rak_data = baca_rak()
    print(BIRU + "=" * 5 + " SEDANG DIBACA " + "=" * 5 + RESET)

    # Tampilkan buku yang sedang dibaca
    if len(rak_data["sedang"]) == 0:
        print("Belum ada buku yang sedang dibaca.")
    else:
        for judul, dibaca in rak_data["sedang"].items():
            data = temukan_buku(data_buku, judul)
            if data is not None:
                print(f"- {judul} ({hitung_persen(dibaca, data['jumlah_halaman'])}%)")

    kata_kunci = input("\nKetik judul buku (0 = kembali ke menu): ")
    if kata_kunci == "0" or kata_kunci == "":
        return

    # Cari bukunya
    buku = temukan_buku(data_buku, kata_kunci)

    # Tidak ketemu -> tambahkan buku
    if buku is None:
        print(MERAH + "Buku tidak ditemukan." + RESET)
        print(KUNING + "Ayo tambahkan buku!" + RESET)
        tambah_buku(kata_kunci)
        return

    judul = buku["judul"]
    status = rak_dari(rak_data, judul)
    if status == "sedang":
        dibaca = rak_data["sedang"][judul]
    elif status == "sudah":
        dibaca = buku["jumlah_halaman"]
    else:
        dibaca = 0

    # Ketemu -> tampilkan identitas
    print(HIJAU + "=" * 5 + " IDENTITAS BUKU " + "=" * 5 + RESET)
    print(f"Judul   : {judul}")
    print(f"Penulis : {buku['penulis']}")
    print(f"Genre   : {buku['genre']}")
    print(f"Halaman : {buku['jumlah_halaman']}")
    print(f"Rak     : {NAMA_RAK[status] if status else 'Belum masuk rak'}")
    print(f"Dibaca  : {dibaca} halaman ({hitung_persen(dibaca, buku['jumlah_halaman'])}%)")

    if status == "sudah":
        print(HIJAU + "Buku ini sudah selesai dibaca 🎉" + RESET)
        return

    # Buku yang dipilih otomatis pindah ke rak "Sedang dibaca"
    if status != "sedang":
        pindah_rak(rak_data, judul, "sedang")
        simpan_rak(rak_data)

    # Input halaman yang sudah dibaca
    halaman = input("Halaman yang sudah dibaca (total): ")
    while not halaman.isdigit() or int(halaman) > buku["jumlah_halaman"]:
        print(MERAH + f"⚠️ Isi angka 0 sampai {buku['jumlah_halaman']}!" + RESET)
        halaman = input("Halaman yang sudah dibaca (total): ")
    halaman = int(halaman)

    if halaman <= dibaca:
        print(KUNING + "Belum ada halaman baru, streak belum bertambah." + RESET)
        return

    # Hitung dan tampilkan progres
    rak_data["sedang"][judul] = halaman
    persen = hitung_persen(halaman, buku["jumlah_halaman"])
    terisi = persen // 10
    print(f"Progres : {'█' * terisi}{'░' * (10 - terisi)} {persen}%")

    # Kalau sudah 100%, pindah ke rak "Sudah dibaca"
    if halaman == buku["jumlah_halaman"]:
        pindah_rak(rak_data, judul, "sudah")
        print(HIJAU + "🎉 Selamat, buku ini selesai dibaca!" + RESET)
        jawab = input("Jadikan buku favorit? (y/n): ")
        if jawab.lower() == "y":
            jadikan_favorit(rak_data, judul)
            print(HIJAU + "⭐ Masuk ke rak Favorit!" + RESET)

    simpan_rak(rak_data)
    rawat_pet(pet)
    print(f"🔥 Streak: {streak_sekarang(pet)} hari")


# ---------- MENU 4: STREAK ----------
def menu_streak(pet):
    nyawa = nyawa_pet(pet)
    print(BIRU + "=" * 5 + " STREAK " + "=" * 5 + RESET)
    print(f"{emoji_pet(pet)} {pet['nama']}")
    print(f"🔥 Streak : {streak_sekarang(pet)} hari")
    print(f"Nyawa  : {'❤️ ' * nyawa}{'🖤 ' * (3 - nyawa)} ({kondisi_pet(pet)})")
    print("1. Rawat streak (baca buku)")
    print("2. Kembali ke menu")
    pilihan = input("Pilih (1/2): ")

    if pilihan == "1":
        sedang_dibaca(pet)
    elif pilihan != "2":
        print(MERAH + "Pilihan tidak valid." + RESET)


# ---------- PROGRAM UTAMA ----------
tampilkan_judul("📚 Selamat datang di Book Tracker 📚")
print()

pet = baca_pet()
if pet is None:
    pet = buat_pet()
elif kondisi_pet(pet) == "Mati":
    print(MERAH + f"{pet['nama']} mati 🪦 karena lama tidak dirawat." + RESET)
    pet = buat_pet()
pet.setdefault("streak", 0)  # Hewan.json yang belum punya isian streak

tampilan_menu(pet)
pilihan = input("Pilih Menu 1-5: ")

while pilihan != "5":
    print()
    if pilihan == "1":
        cari_buku()
    elif pilihan == "2":
        rak_buku()
    elif pilihan == "3":
        sedang_dibaca(pet)
    elif pilihan == "4":
        menu_streak(pet)
    else:
        print(MERAH + "Tidak valid, pilih 1-5" + RESET)

    print()
    tampilan_menu(pet)
    pilihan = input("Pilih Menu 1-5: ")

print(KUNING + "Terimakasih, sampai jumpa!" + RESET)
