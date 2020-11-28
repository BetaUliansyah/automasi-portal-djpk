# Automasi Data dari Portal APBD DJPK
[Portal APBD](http://www.djpk.kemenkeu.go.id/portal/data/apbd) yang disediakan DJPK - Kemenkeu, menyediakan data APBD dan TKDD untuk seluruh Pemda se-Indonesia. Namun di laman web tersebut, kita hanya bisa mengambil data satu per satu. 

Untuk mendapatkan data seluruh daerah, setidaknya ada 4 metode:
1. Metode Copas satu per satu
2. Metode Padat Karya: minta bantuan mahasiswa dari kelas-kelas yang diampu untuk melakukan metode 1 atau 2 di atas, lalu dikonsolidasi di Excel (menu Data, Consolidate)
3. Metode Automasi, yang digunakan di source code ini.

## Cara Pembuatan
Simulasikan pengambilan data untuk satu daerah menggunakan Chrome, lalu cek variabel-variabel apa saja yang dikirim melalui POST dengan membuka fitur Inspect, Networks, Headers.
![inspect POST variables](img/jaga-id.jpg)

Lakukan looping di python dengan kode daerah seluruh pemda di Indonesia sebagai iterasi.

## Cara Penggunaan
### A. Melalui Notebook
Salin kode python di repository ini ke Colab, dan jalankan dengan cara menekan tombol Run atau dengan menekan Ctrl - Enter. Tersedia link demo di bagian bawah tulisan ini.

### B. Melalui command line
Salin kode python ke file di komputer lokal Anda. Jalankan skrip python dengan perintah:
`python automasi-data-apbd-google-colab.py`

Skrip akan berjalan beberapa menit sebelum mengeluarkan hasil.

## Demo
Silakan salin notebook berikut ini ke akun Colab Anda: https://bit.ly/AutomasiPortalAPBD 
Jalankan kode Python dengan menekan tombol Run atau Ctrl-Enter

![menjalankan dengan Google Colab](img/jaga-colab.jpg)

## Menggunakan Data
Bagi yang tidak ingin repot menjalankan script Python, maka dapat langsung menggunakan data hasil running script yang kami lakukan. Data dapat diakses di [Folder Data](https://github.com/BetaUliansyah/automasi-portal-djpk/tree/main/data), data akan diupdate secara periodik. Pastikan menggunakan data terbaru yang kami upload.

## Cara Mengutip Data
Uiansyah, Beta. (2020). Dataset APBD dari Portal APBD DJPK [Dataset]. Retrieved from [https://github.com/BetaUliansyah/automasi-portal-djpk](https://github.com/BetaUliansyah/automasi-portal-djpk)
