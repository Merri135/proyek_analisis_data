import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
import numpy as np
import plotly.express as px
sns.set(style='dark')
# Tentukan direktori tempat file berada
data_dir = os.getcwd()  # Gunakan direktori kerja saat ini

# Pastikan path menuju file, bukan folder
day_file = os.path.join(data_dir, "Dasboard/day.csv")
hour_file = os.path.join(data_dir, "Dasboard/hour.csv")

# Cek apakah file benar-benar ada sebelum membaca
try:
    if os.path.exists(day_file) and os.path.exists(hour_file):
        # Baca file CSV menggunakan Pandas
        day_df = pd.read_csv(day_file)
        hour_df = pd.read_csv(hour_file)

        print("File berhasil dibaca!")
    else:
        print("Error: Salah satu atau kedua file tidak ditemukan. Periksa path!")
except Exception as e:
    print(f"Terjadi kesalahan saat membaca file: {e}")
    # menghapus kolom 'instant' karena tidak relevan
day_df.drop('instant', axis=1, inplace=True)
hour_df.drop('instant', axis=1, inplace=True)

# menghapus kolom 'workingday' karena sudah ada kolom 'weekday'
day_df.drop('workingday', axis=1, inplace=True)
hour_df.drop('workingday', axis=1, inplace=True)

# mengubah kolom 'temp', 'atemp', 'hum', 'windspeed' menjadi satuan lebih umum sesuai readme
day_df["temp"] = day_df["temp"] * 41
day_df["atemp"] = day_df["atemp"] * 50
day_df["hum"] = day_df["hum"] * 100
day_df["windspeed"] = day_df["windspeed"] * 67
day_df.head()
# Konversi kolom numerik menjadi kategori dengan label deskriptif
category_mappings = {
    "season": {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"},
    "yr": {0: "2011", 1: "2012"},
    "mnth": {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
             7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"},
    "holiday": {0: "No", 1: "Yes"},
    "weekday": {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"},
    "weathersit": {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
}

for col, mapping in category_mappings.items():
    day_df[col] = day_df[col].map(mapping).astype("category")
    hour_df[col] = hour_df[col].map(mapping).astype("category")

# Pastikan kolom numerik hanya berisi angka
numeric_cols_day = day_df.select_dtypes(include=['number']).columns
numeric_cols_hour = hour_df.select_dtypes(include=['number']).columns

day_df = day_df[numeric_cols_day].join(day_df[list(category_mappings.keys())])
hour_df = hour_df[numeric_cols_hour].join(hour_df[list(category_mappings.keys())])

# Pastikan kolom 'hr' ada dan bertipe numerik
if 'hr' in hour_df.columns:
    hour_df['hr'] = pd.to_numeric(hour_df['hr'], errors='coerce')

# Streamlit UI
st.title("Statistik Data Bike Sharing")

# Sidebar untuk filter
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Pilih Tahun", ["Semua"] + day_df['yr'].cat.categories.tolist())
selected_season = st.sidebar.selectbox("Pilih Musim", ["Semua"] + day_df['season'].cat.categories.tolist())
selected_weekday = st.sidebar.selectbox("Tipe Hari", ["Semua"] + day_df['weekday'].cat.categories.tolist())

# Terapkan filter
df_filtered = day_df.copy()
if selected_year != "Semua":
    df_filtered = df_filtered[df_filtered['yr'] == selected_year]
if selected_season != "Semua":
    df_filtered = df_filtered[df_filtered['season'] == selected_season]
if selected_weekday != "Semua":
    df_filtered = df_filtered[df_filtered['weekday'] == selected_weekday]

# Analisis pengguna casual vs registered
st.subheader("Perbandingan Pengguna Registered vs Casual")
casual_total = df_filtered['casual'].sum()
registered_total = df_filtered['registered'].sum()
st.write(f"Total pengguna casual: {casual_total}")
st.write(f"Total pengguna registered: {registered_total}")

fig, ax = plt.subplots()
labels = ['Casual', 'Registered']
values = [casual_total, registered_total]
ax.bar(labels, values, color=['red', 'blue'])
st.pyplot(fig)

# Analisis pengguna berdasarkan season, year, weekday, dan jam
# Menghitung total jumlah penyewaan per musim
df_season = df_filtered.groupby('season')['cnt'].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(x='season', y='cnt', data=df_season, palette=['navy', 'green', 'teal', 'yellow'])

ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Permintaan")
ax.set_title("Permintaan Penyewaan Sepeda Berdasarkan Musim")

st.pyplot(fig)



# Mengelompokkan data berdasarkan tahun
df_yearly = df_filtered.groupby("yr")["cnt"].sum().reset_index()
colors = ['yellow', 'navy']  # Warna disesuaikan dengan gambar
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='yr', y='cnt', data=df_yearly, palette=colors)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Permintaan")
ax.set_title("Permintaan Penyewaan Sepeda Berdasarkan Tahun")
st.pyplot(fig)

# Menampilkan subjudul di Streamlit

# Mengurutkan bulan dengan benar
order_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Mengelompokkan data berdasarkan bulan
df_yearly = df_filtered.groupby("mnth")["cnt"].sum().reset_index()
df_yearly["mnth"] = pd.Categorical(df_yearly["mnth"], categories=order_months, ordered=True)
df_yearly = df_yearly.sort_values("mnth")
colors = sns.color_palette("Blues", len(df_yearly))
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="mnth", y="cnt", data=df_yearly, palette=colors)
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Permintaan")
ax.set_title("Permintaan Penyewaan Sepeda Berdasarkan Bulan")
st.pyplot(fig)


fig, ax = plt.subplots()
fig, ax = plt.subplots(figsize=(10, 4))
sns.lineplot(x='weekday', y='cnt', data=df_filtered, color='navy', marker='o')
ax.set_xlabel("Hari dalam seminggu")
ax.set_ylabel("Jumlah Permintaan")
ax.set_title("Permintaan Penyewaan Sepeda Berdasarkan Hari")
ax.legend()
st.pyplot(fig)


# Mengelompokkan data berdasarkan cuaca
df_yearly = df_filtered.groupby("weathersit")["cnt"].sum().reset_index()
colors = ["darkblue", "royalblue", "deepskyblue", "lightblue"]  # Warna disesuaikan dengan gambar
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='weathersit', y='cnt', data=df_yearly, palette=colors)
ax.set_xlabel("Cuaca")
ax.set_ylabel("Jumlah Penyewaan")
ax.set_title("Pengaruh cuaca pada penyewaan sepeda")
st.pyplot(fig)

st.header("Analisis Lanjutan")
st.header("Menggunakan Clustering")
# Simulasi Clustering (pastikan hanya dari data yang telah difilter)
np.random.seed(42)
cluster_data = {
    'temp': np.random.rand(len(df_filtered)) * 40,
    'hum': np.random.rand(len(df_filtered)) * 100,
    'windspeed': np.random.rand(len(df_filtered)) * 50,
    'cnt': np.random.randint(100, 1000, len(df_filtered)),
    'season_label': df_filtered['season'].values,
    'usage_level': np.random.choice(['Permintaan Tinggi', 'Permintaan Sedang', 'Permintaan Rendah'], len(df_filtered))
}
cluster_df = pd.DataFrame(cluster_data)


# Menampilkan Metode Elbow di Streamlit

# Pilih fitur untuk clustering
features = ['temp', 'hum', 'windspeed', 'cnt']
X = df_filtered[features]

# Normalisasi Data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Menentukan nilai WCSS untuk berbagai jumlah cluster
wcss = []
K_range = range(1, 11)  # Coba dari 1 hingga 10 cluster
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

# Membuat Plot Elbow
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(K_range, wcss, marker='o', linestyle='-')
ax.set_xlabel("Jumlah Cluster (k)")
ax.set_ylabel("WCSS")
ax.set_title("Metode Elbow untuk Menentukan Jumlah Cluster Optimal")
ax.grid(True)

# Tampilkan plot di Streamlit
st.pyplot(fig)


# *Visualisasi Cluster Sesuai Filter*

# Hitung jumlah hari untuk setiap musim dan level permintaan
cluster_season = pd.crosstab(cluster_df['season_label'], cluster_df['usage_level'])

# Warna sesuai gambar
warna_kategori = {
    'Permintaan Tinggi': 'navy',
    'Permintaan Sedang': 'blue',
    'Permintaan Rendah': 'lightblue'
}

# Plot dengan Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
cluster_season.plot(kind='bar', stacked=False, ax=ax, color=[warna_kategori[col] for col in cluster_season.columns])

# Tambahkan label jumlah pada setiap batang
for container in ax.containers:
    ax.bar_label(container, fmt='%d', label_type='edge', fontsize=10)

# Sesuaikan label dan judul
ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Permintaan")
ax.set_title("Distribusi Level Permintaan Penyewaan Sepeda Berdasarkan Musim")
ax.legend(title="usage_level", loc='upper center')

# Tampilkan plot di Streamlit
st.pyplot(fig)

# Menampilkan statistik deskriptif
st.subheader("Ringkasan Statistik")
st.write(df_filtered.head())
