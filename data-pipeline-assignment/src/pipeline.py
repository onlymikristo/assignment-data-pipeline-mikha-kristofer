import os
import pandas as pd
import numpy as np


# =====================================================================
# TAHAP EXTRACT (E)
# =====================================================================
def load_data(input_path: str) -> pd.DataFrame:
    """1. Function untuk membaca dataset CSV mentah dari folder data/raw/."""
    print("=" * 70)
    print("ETL - EXTRACT: MEMBACA DATASET MENTAH")
    print("=" * 70)
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File input tidak ditemukan: {input_path}")

    df = pd.read_csv(input_path)
    print(f"Dataset berhasil dimuat dari: {input_path}")
    return df


# =====================================================================
# TAHAP TRANSFORM (T) - INSPECT, CLEAN, & TRANSFORM
# =====================================================================
def inspect_data(df: pd.DataFrame) -> None:
    """2. Function untuk memeriksa kondisi awal dataset dan menampilkannya ke terminal."""
    print("\n" + "=" * 70)
    print("ETL - TRANSFORM (1/3): PEMERIKSAAN KONDISI AWAL DATASET (INSPECTION)")
    print("=" * 70)

    print("\n[1] Lima Baris Pertama Dataset:")
    print(df.head())

    print(f"\n[2] Ukuran Dataset (Baris, Kolom): {df.shape[0]} baris x {df.shape[1]} kolom")

    print("\n[3] Nama Setiap Kolom:")
    print(list(df.columns))

    print("\n[4] Tipe Data Setiap Kolom:")
    print(df.dtypes)

    print("\n[5] Jumlah Missing Values pada Setiap Kolom:")
    missing_counts = df.isnull().sum()
    print(missing_counts[missing_counts > 0])
    print(f"Total Missing Values Keseluruhan: {missing_counts.sum()}")

    print(f"\n[6] Jumlah Duplicate Records: {df.duplicated().sum()} baris")

    print("\n[7] Nilai Unik pada Kolom Kategorikal yang Relevan:")
    cat_cols = [
        'make', 'aspiration', 'num-of-doors', 'body-style', 'drive-wheels',
        'engine-location', 'engine-type', 'num-of-cylinders', 'fuel-system',
        'horsepower-binned'
    ]
    for col in cat_cols:
        if col in df.columns:
            print(f"  - {col}: {df[col].unique().tolist()}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """3. Function untuk melakukan data cleaning berdasarkan temuan inspeksi."""
    print("\n" + "=" * 70)
    print("ETL - TRANSFORM (2/3): DATA CLEANING")
    print("=" * 70)

    df_clean = df.copy()

    rows_before = df_clean.shape[0]
    cols_before = df_clean.shape[1]
    missing_before = df_clean.isnull().sum()
    dup_count = df_clean.duplicated().sum()

    changed_cols = []

    # 1. Menghapus duplicate records
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)

    # 2. Menghapus kolom transaction_date yang formatnya tidak konsisten & tidak relevan
    if 'transaction_date' in df_clean.columns:
        df_clean = df_clean.drop(columns=['transaction_date'])
        changed_cols.append('transaction_date (dihapus karena tidak relevan & format tidak konsisten)')

    # 3. Menghapus spasi tidak diperlukan & menyeragamkan penulisan kategorikal (lowercase)
    str_cols = [
        'make', 'aspiration', 'num-of-doors', 'body-style', 'drive-wheels',
        'engine-location', 'engine-type', 'num-of-cylinders', 'fuel-system'
    ]
    for col in str_cols:
        before_vals = df_clean[col].copy()
        df_clean[col] = df_clean[col].astype(str).str.strip().str.lower().replace('nan', np.nan)
        if not before_vals.equals(df_clean[col]):
            changed_cols.append(f"{col} (standardisasi lowercase & hapus trailing whitespace)")

    # 4. Menangani missing values pada kolom numerik menggunakan median
    num_missing_cols = ['stroke', 'horsepower', 'price']
    for col in num_missing_cols:
        median_val = df_clean[col].median()
        df_clean[col] = df_clean[col].fillna(median_val)
        changed_cols.append(f"{col} (imputasi missing value dengan median={median_val:.2f})")

    # 5. Menangani missing values pada kolom kategorikal menggunakan modus (mode)
    cat_missing_cols = ['make', 'num-of-doors', 'horsepower-binned']
    for col in cat_missing_cols:
        mode_val = df_clean[col].mode()[0]
        df_clean[col] = df_clean[col].fillna(mode_val)
        changed_cols.append(f"{col} (imputasi missing value dengan modus='{mode_val}')")

    # 6. Memperbaiki tipe data yang belum sesuai (teks kata angka -> numerik float)
    doors_map = {'two': 2, 'four': 4}
    cylinders_map = {
        'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'eight': 8, 'twelve': 12
    }
    df_clean['num-of-doors'] = df_clean['num-of-doors'].map(doors_map).astype(float)
    df_clean['num-of-cylinders'] = df_clean['num-of-cylinders'].map(cylinders_map).astype(float)
    changed_cols.append("num-of-doors & num-of-cylinders (konversi teks kata angka ke tipe numerik)")

    rows_after = df_clean.shape[0]
    cols_after = df_clean.shape[1]
    missing_after = df_clean.isnull().sum()

    print(f"\n[1] Jumlah Data Sebelum Cleaning : {rows_before} baris x {cols_before} kolom")
    print(f"    Jumlah Data Sesudah Cleaning : {rows_after} baris x {cols_after} kolom")
    print(f"\n[2] Jumlah Baris Terduplikasi yang Dihapus: {dup_count} baris")

    print("\n[3] Jumlah Missing Values Sebelum vs Sesudah Cleaning:")
    missing_summary = pd.DataFrame({
        'Sebelum_Cleaning': missing_before[missing_before > 0],
        'Sesudah_Cleaning': [
            missing_after[c] if c in missing_after.index else 0
            for c in missing_before[missing_before > 0].index
        ]
    })
    print(missing_summary)
    print(f"Total Missing Values Sesudah Cleaning: {missing_after.sum()}")

    print("\n[4] Kolom yang Mengalami Perubahan:")
    for item in changed_cols:
        print(f"  - {item}")

    return df_clean


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """4. Function untuk melakukan data transformation (Min-Max Scaling & Encoding)."""
    print("\n" + "=" * 70)
    print("ETL - TRANSFORM (3/3): DATA TRANSFORMATION")
    print("=" * 70)

    df_trans = df.copy()

    # Simpan sampel nilai sebelum transformasi untuk perbandingan
    sample_before = df_trans[[
        'price', 'horsepower', 'curb-weight',
        'horsepower-binned', 'body-style', 'make'
    ]].head(5).copy()

    # 1. Ordinal Encoding untuk horsepower-binned
    hp_ordinal_map = {'Low': 0, 'Medium': 1, 'High': 2}
    df_trans['horsepower_ordinal'] = df_trans['horsepower-binned'].map(hp_ordinal_map)
    df_trans = df_trans.drop(columns=['horsepower-binned'])

    # 2. One-Hot Encoding untuk kolom kategorikal nominal
    ohe_cols = [
        'body-style', 'drive-wheels', 'aspiration',
        'engine-type', 'engine-location', 'fuel-system'
    ]
    df_trans = pd.get_dummies(df_trans, columns=ohe_cols, dtype=int)

    # 3. Frequency Encoding untuk kolom 'make'
    make_freq = df_trans['make'].value_counts(normalize=True)
    df_trans['make_freq'] = df_trans['make'].map(make_freq)
    df_trans = df_trans.drop(columns=['make'])

    # 4. Min-Max Scaling (rentang 0 hingga 1) pada kolom numerik
    scale_cols = [
        'symboling', 'num-of-doors', 'curb-weight', 'num-of-cylinders',
        'engine-size', 'horsepower', 'peak-rpm', 'city-mpg',
        'highway-mpg', 'price'
    ]
    for col in scale_cols:
        min_val = df_trans[col].min()
        max_val = df_trans[col].max()
        df_trans[col] = (df_trans[col] - min_val) / (max_val - min_val)

    sample_after = df_trans[[
        'price', 'horsepower', 'curb-weight',
        'horsepower_ordinal', 'body-style_convertible',
        'body-style_hatchback', 'make_freq'
    ]].head(5).copy()

    print("\n[1] Perbandingan Nilai Sebelum Transformasi (5 Baris Pertama):")
    print(sample_before.to_string())

    print("\n[2] Perbandingan Nilai Sesudah Transformasi (5 Baris Pertama):")
    print(sample_after.to_string())

    print(f"\n[3] Ukuran Dataset Setelah Transformasi: {df_trans.shape[0]} baris x {df_trans.shape[1]} kolom")

    return df_trans


# =====================================================================
# TAHAP LOAD (L)
# =====================================================================
def save_data(df: pd.DataFrame, output_path: str) -> None:
    """5. Function untuk menyimpan hasil olahan ke folder data/processed/."""
    print("\n" + "=" * 70)
    print("ETL - LOAD: MENYIMPAN PROCESSED DATASET")
    print("=" * 70)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Processed dataset berhasil disimpan secara otomatis di: {output_path}")
    print(f"Dimensi Akhir Dataset: {df.shape[0]} baris x {df.shape[1]} kolom")
    print("=" * 70)


# =====================================================================
# RUNNER PIPELINE UTAMA
# =====================================================================
def run_pipeline(input_path: str, output_path: str) -> pd.DataFrame:
    """Menjalankan keseluruhan alur ETL pipeline dari awal sampai akhir."""
    # Extract
    raw_df = load_data(input_path)

    # Transform (Inspect -> Clean -> Transform)
    inspect_data(raw_df)
    cleaned_df = clean_data(raw_df)
    transformed_df = transform_data(cleaned_df)

    # Load
    save_data(transformed_df, output_path)
    return transformed_df


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'automobileEDA_dirty_training.csv')
    OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'automobileEDA_processed.csv')

    run_pipeline(INPUT_FILE, OUTPUT_FILE)
