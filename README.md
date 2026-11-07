# Data Processing Pipeline Assignment - Automotive Dataset

## 1. Deskripsi Singkat Dataset
Dataset ini berisi data spesifikasi teknis, karakteristik fisik, konsumsi bahan bakar, tingkat risiko asuransi (`symboling` & `normalized-losses`), serta harga jual (`price`) dari berbagai merek kendaraan bermotor (mobil). Dataset mentah yang diterima oleh tim AI (`automobileEDA_dirty_training.csv`) masih memiliki berbagai permasalahan kualitas data—seperti nilai kosong (*missing values*), duplikasi baris, ketidakkonsistenan penulisan kategori, perbedaan skala numerik, dan tipe data yang belum sesuai—sehingga memerlukan pemrosesan melalui pipeline ETL sebelum siap digunakan untuk analisis atau pemodelan *machine learning*.

## 2. Sumber Dataset
* **Dataset Utama (Input Mentah)**: `automobileEDA_dirty_training.csv` (dimodifikasi dari *UCI Machine Learning Repository: Automobile Dataset* untuk simulasi kasus *dirty data* pada assignment).
* **Dataset Referensi Original**: `automobileEDA.csv`
* **Dataset Referensi Hasil Akhir**: `automobile_processed.csv`

---

## 3. Struktur Folder Project

```text
data-pipeline-assignment/
├── data/
│   ├── raw/
│   │   └── automobileEDA_dirty_training.csv
│   └── processed/
│       └── automobileEDA_processed.csv
├── src/
│   └── pipeline.py
├── documentation/
│   └── data-flow-diagram.png
├── README.md
└── requirements.txt
```

---

## 4. Penjelasan Singkat Alur ETL & Data Flow Diagram

Pipeline dibangun mengikuti arsitektur **ETL (Extract, Transform, Load)** yang modular di dalam `src/pipeline.py`:

| Tahap ETL | Fungsi di `pipeline.py` | Deskripsi Proses dalam Assignment |
| :--- | :--- | :--- |
| **Extract** | `load_data()` | Membaca dataset CSV mentah dari `data/raw/automobileEDA_dirty_training.csv` tanpa mengubah file aslinya. |
| **Transform** | `inspect_data()`, `clean_data()`, `transform_data()` | Memeriksa kondisi awal dataset, membersihkan duplikat/missing values/inkonsistensi teks, serta melakukan normalisasi (*Min-Max Scaling*) dan *encoding* fitur kategorikal. |
| **Load** | `save_data()` | Menyimpan *processed dataset* secara otomatis ke `data/processed/automobileEDA_processed.csv`. |

**Alur Pengolahan Data (Data Flow Diagram):**
`Raw Dataset` $ightarrow$ `Load Data` $ightarrow$ `Data Inspection` $ightarrow$ `Data Cleaning` $ightarrow$ `Data Transformation` $ightarrow$ `Processed Dataset`

*(Visualisasi diagram tersimpan di `documentation/data-flow-diagram.png`)*

---

## 5. Kondisi Awal Dataset & Permasalahan yang Ditemukan

Berdasarkan hasil eksekusi fungsi `inspect_data()` pada dataset mentah (`data/raw/automobileEDA_dirty_training.csv`):

* **Ukuran Awal Dataset**: `205 baris x 30 kolom`.
* **Jumlah Baris yang Terduplikasi**: Terdapat **4 baris duplikat** (baris indeks `201, 202, 203, 204` merupakan duplikat identik dari baris `5, 25, 60, 100`).
* **Kolom yang Memiliki Missing Values** (Total **17 nilai kosong** pada dataset awal):
  * `stroke`: 4 nilai kosong (`NaN`)
  * `horsepower`: 3 nilai kosong (`NaN`)
  * `price`: 3 nilai kosong (`NaN`)
  * `transaction_date`: 2 nilai kosong (`NaN`)
  * `make`: 2 nilai kosong (`NaN` — 1 di antaranya berada pada baris duplikat)
  * `num-of-doors`: 2 nilai kosong (`NaN`)
  * `horsepower-binned`: 1 nilai kosong (`NaN`)
* **Kolom dengan Tipe Data yang Belum Sesuai**:
  * `num-of-doors` (`'two'`, `'four'`) dan `num-of-cylinders` (`'two'`, `'three'`, `'four'`, `'five'`, `'six'`, `'eight'`, `'twelve'`) masih bertipe `object` (string), padahal merepresentasikan kuantitas numerik.
  * `transaction_date` bertipe `object` dengan format penanggalan yang tercampur (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`, `DD-MMM-YYYY`).
* **Penulisan Kategori yang Belum Konsisten**:
  * `make`: Terdapat perbedaan huruf kapital dan spasi berlebih di akhir kata (*trailing whitespace*), seperti `'ALFA-ROMERO'`, `'BMW'`, `'Audi'`, `'dodge  '`, `'mercury  '`, dan `'porsche  '`.
  * `body-style`: Penulisan tidak seragam antara `'sedan'`, `'SEDAN'`, dan `'Sedan'`.
  * `drive-wheels`: Penulisan huruf besar/kecil tidak konsisten pada `'rwd'` vs `'RWD'` serta `'AWD'`.
  * `fuel-system`: Penulisan tidak seragam antara `'mpfi'`, `'MPFI'`, dan `'Mpfi'`.
* **Permasalahan Lain yang Ditemukan**:
  * **Kolom tidak relevan**: Kolom `transaction_date` tidak berkaitan dengan spesifikasi teknis maupun harga mobil.
  * **Skala nilai numerik belum seragam**: Fitur seperti `price` (`5118 - 45400`) dan `curb-weight` (`1488 - 4066`) memiliki rentang ribuan hingga puluhan ribu, sedangkan `symboling` (`-2 - 3`) dan `length` (`0.67 - 1.00`) bernilai satuan kecil.
  * **Data kategorikal masih berbentuk teks**: Fitur `body-style`, `drive-wheels`, `aspiration`, `engine-type`, `engine-location`, `fuel-system`, `horsepower-binned`, dan `make` masih berupa teks sehingga belum siap dimasukkan ke model *machine learning*.

---

## 6. Cleaning yang Dilakukan Beserta Alasannya

Diimplementasikan melalui fungsi `clean_data()` di dalam `src/pipeline.py`:

| Permasalahan | Kolom yang Dibersihkan | Metode Cleaning yang Digunakan | Alasan Pemilihan Metode |
| :--- | :--- | :--- | :--- |
| **Duplicate Records** | Seluruh kolom (4 baris) | Menghapus baris duplikat menggunakan `drop_duplicates()` | Baris yang 100% identik tidak memberikan informasi tambahan dan dapat memicu bias pada analisis statistik maupun pelatihan model. |
| **Kolom Tidak Relevan & Format Tanggal Tidak Konsisten** | `transaction_date` | Menghapus kolom (`drop(columns=['transaction_date'])`) | Tanggal pencatatan transaksi tidak relevan terhadap karakteristik kendaraan, memiliki format tidak konsisten, serta mengandung *missing values*. |
| **Spasi Berlebih & Huruf Tidak Konsisten** | `make`, `aspiration`, `num-of-doors`, `body-style`, `drive-wheels`, `engine-location`, `engine-type`, `num-of-cylinders`, `fuel-system` | Menghapus spasi di awal/akhir (`str.strip()`) dan menyeragamkan huruf menjadi *lowercase* (`str.lower()`) | Mencegah satu kategori yang sama terpecah menjadi beberapa kategori berbeda saat proses *encoding* (contoh: `'Sedan'`, `'SEDAN'`, dan `'sedan'` disatukan menjadi `'sedan'`). |
| **Missing Values Numerik** | `stroke` (4), `horsepower` (3), `price` (3) | Imputasi menggunakan **Median** (`stroke`: `3.29`, `horsepower`: `95.00`, `price`: `10270.00`) | Distribusi fitur numerik otomotif (terutama `price` dan `horsepower`) bersifat *skewed* (menceng) dan memiliki *outlier*. Median lebih tahan (*robust*) terhadap *outlier* dibandingkan *mean*, serta menjaga ukuran sampel tetap utuh. |
| **Missing Values Kategorikal** | `make` (1), `num-of-doors` (2), `horsepower-binned` (1) | Imputasi menggunakan **Modus / Mode** (`make`: `'toyota'`, `num-of-doors`: `'four'`, `horsepower-binned`: `'Low'`) | Karena jumlah baris kosong sangat sedikit (1–2 baris), pengisian dengan kategori yang paling sering muncul (*modus*) mempertahankan keutuhan baris data tanpa mendistorsi proporsi kategori. |
| **Tipe Data Kata Angka** | `num-of-doors`, `num-of-cylinders` | Mapping kata ke angka (`'two'`: `2`, `'four'`: `4`, dst.) dan konversi ke `float` | Jumlah pintu dan jumlah silinder merupakan variabel kuantitatif yang perlu direpresentasikan secara numerik agar dapat dihitung dan dinormalisasi. |

---

## 7. Transformasi yang Dilakukan

Diimplementasikan melalui fungsi `transform_data()` di dalam `src/pipeline.py`:

1. **Normalisasi Numerik dengan *Min-Max Scaling***:
   * **Kolom yang Ditransformasi**: `symboling`, `num-of-doors`, `curb-weight`, `num-of-cylinders`, `engine-size`, `horsepower`, `peak-rpm`, `city-mpg`, `highway-mpg`, dan `price`.
   * **Metode**: *Min-Max Scaling* ke rentang `[0, 1]` dengan rumus $X_{	ext{scaled}} = rac{X - X_{\min}}{X_{\max} - X_{\min}}$.
   * **Alasan Pemilihan**: Menyeragamkan rentang nilai antar fitur numerik agar fitur dengan angka besar (seperti `price` dan `curb-weight`) tidak mendominasi bobot perhitungan model.
2. **Ordinal Encoding**:
   * **Kolom yang Ditransformasi**: `horsepower-binned` $ightarrow$ menghasilkan kolom baru `horsepower_ordinal` (kolom asli dihapus).
   * **Metode**: Pemetaan berurutan (`'Low': 0`, `'Medium': 1`, `'High': 2`).
   * **Alasan Pemilihan**: Kategori pada `horsepower-binned` memiliki tingkatan urutan yang jelas (rendah, sedang, tinggi).
3. **One-Hot Encoding**:
   * **Kolom yang Ditransformasi**: `body-style`, `drive-wheels`, `aspiration`, `engine-type`, `engine-location`, dan `fuel-system`.
   * **Metode**: `pd.get_dummies(..., dtype=int)` yang menghasilkan 27 kolom biner (`0`/`1`) baru.
   * **Alasan Pemilihan**: Keenam fitur tersebut bersifat nominal (tanpa urutan tingkatan) dengan kardinalitas rendah (2–8 kategori unik).
4. **Frequency Encoding**:
   * **Kolom yang Ditransformasi**: `make` $ightarrow$ menghasilkan kolom baru `make_freq` (kolom asli dihapus).
   * **Metode**: Mengganti nama merek mobil dengan proporsi frekuensi kemunculannya (`value_counts(normalize=True)`).
   * **Alasan Pemilihan**: Kolom `make` memiliki 22 kategori unik; *Frequency Encoding* menghindari penambahan 22 kolom baru yang terlalu *sparse* sekaligus mempertahankan informasi distribusi merek.

---

## 8. Contoh Hasil Sebelum dan Sesudah Transformasi

Berikut adalah perbandingan nilai pada 5 baris pertama sebelum dan sesudah proses transformasi:

| Indeks | `price` (Sebelum) | `price` (Sesudah Min-Max) | `horsepower` (Sebelum) | `horsepower` (Sesudah Min-Max) | `curb-weight` (Sebelum) | `curb-weight` (Sesudah Min-Max) | `horsepower-binned` (Sebelum) | `horsepower_ordinal` (Sesudah) | `body-style` (Sebelum) | `body-style_convertible` (Sesudah) | `make` (Sebelum) | `make_freq` (Sesudah) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 13495.0 | 0.207959 | 111.0 | 0.294393 | 2548 | 0.411171 | Medium | 1 | convertible | 1 | alfa-romero | 0.014925 |
| **1** | 16500.0 | 0.282558 | 111.0 | 0.294393 | 2548 | 0.411171 | Medium | 1 | convertible | 1 | alfa-romero | 0.014925 |
| **2** | 16500.0 | 0.282558 | 154.0 | 0.495327 | 2823 | 0.517843 | Medium | 1 | hatchback | 0 | alfa-romero | 0.014925 |
| **3** | 13950.0 | 0.219254 | 102.0 | 0.252336 | 2337 | 0.329325 | Medium | 1 | sedan | 0 | audi | 0.034826 |
| **4** | 17450.0 | 0.306142 | 115.0 | 0.313084 | 2824 | 0.518231 | Medium | 1 | sedan | 0 | audi | 0.034826 |

---

## 9. Jumlah Data Sebelum dan Sesudah Diproses

| Tahap Pemrosesan | Jumlah Baris | Jumlah Kolom | Total Missing Values | Jumlah Baris Duplikat |
| :--- | :---: | :---: | :---: | :---: |
| **Dataset Awal (Raw Data)** | 205 | 30 | 17 | 4 |
| **Sesudah Data Cleaning** | 201 | 29 | 0 | 0 |
| **Sesudah Data Transformation (Processed Data)** | **201** | **50** | **0** | **0** |

---

## 10. Cara Menginstal Dependency & Menjalankan Pipeline

1. **Instalasi Dependency**:
   Pastikan Python telah terpasang, lalu jalankan perintah berikut dari direktori utama proyek untuk menginstal library yang tercantum di `requirements.txt` (`pandas` dan `numpy`):
   ```bash
   pip install -r requirements.txt
   ```

2. **Menjalankan `pipeline.py`**:
   Eksekusi script pipeline dengan perintah berikut:
   ```bash
   python src/pipeline.py
   ```

3. **Lokasi Processed Dataset**:
   * **Dataset Mentah (Tidak Diubah)**: `data/raw/automobileEDA_dirty_training.csv`
   * **Dataset Hasil Olahan (Otomatis Dihasilkan)**: `data/processed/automobileEDA_processed.csv`
