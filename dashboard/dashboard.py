import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

sns.set(style='dark')
# Tentukan direktori tempat file berada
data_dir = "D:\\proyek_analisis_data\\dashboard"

# Pastikan path menuju file, bukan folder
day_file = os.path.join(data_dir, "day.csv")  # path benar
hour_file = os.path.join(data_dir, "hour.csv")  # path benar

# Cek apakah file benar-benar ada sebelum membaca
if os.path.exists(day_file) and os.path.exists(hour_file):
    # Baca file CSV menggunakan Pandas
    day_df = pd.read_csv(day_file)
    hour_df = pd.read_csv(hour_file)

    print("File berhasil dibaca!")
else:
    print("Error: Salah satu atau kedua file tidak ditemukan. Periksa path!")

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

# Analisis pengguna berdasarkan season, year, dan weekday
st.subheader("Permintaan sewa sepeda Berdasarkan Musim")
fig, ax = plt.subplots()
sns.barplot(x='season', y='cnt', data=df_filtered, color='skyblue')
ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Permintaan")
ax.legend()
st.pyplot(fig)

st.subheader("Permintaan sewa sepeda Berdasarkan Tahun")
fig, ax = plt.subplots()
sns.barplot(x='yr', y='cnt', data=df_filtered, color='orange',)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Permintaan")
ax.legend()
st.pyplot(fig)

st.subheader("Permintaan sewa sepeda Berdasarkan Hari dalam Seminggu")
fig, ax = plt.subplots()
sns.lineplot(x='weekday', y='cnt', data=df_filtered, color='skyblue',)
ax.set_xlabel("Hari dalam Seminggu")
ax.set_ylabel("Jumlah Permintaan")
ax.legend()
st.pyplot(fig)

# Pengaruh cuaca terhadap penyewaan sepeda
st.subheader("Pengaruh Cuaca terhadap Penyewaan Sepeda")
fig, ax = plt.subplots()
order = ["Clear", "Mist/Cloudy", "Light Rain/Snow", "Heavy Rain/Snow"]  # Urutan kategori
sns.barplot(x='weathersit', y='cnt', data=df_filtered, palette="coolwarm", order=order)
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Pengaruh cuaca berdasarkan season dan weekday
st.subheader("Pengaruh Cuaca Berdasarkan Musim")
fig, ax = plt.subplots()
sns.barplot(x='season', y='cnt', hue='weathersit', data=df_filtered, palette="coolwarm")
ax.set_xlabel("Musim")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

st.subheader("Pengaruh Cuaca Berdasarkan Hari dalam Seminggu")
fig, ax = plt.subplots()
sns.barplot(x='weekday', y='cnt', hue='weathersit', data=df_filtered, palette="coolwarm")
ax.set_xlabel("Hari dalam Seminggu")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Pengaruh jam dalam sehari terhadap penyewaan sepeda
st.subheader("Pola Penyewaan Sepeda Berdasarkan Jam")
if 'hr' in hour_df.columns:
    fig, ax = plt.subplots()
    sns.lineplot(x='hr', y='cnt', data=hour_df, marker='o', color='g')
    ax.set_xlabel("Jam")
    ax.set_ylabel("Total Penyewaan")
    st.pyplot(fig)
else:
    st.write("Kolom 'hr' tidak ditemukan dalam dataset.")

# Menampilkan statistik deskriptif
st.subheader("Ringkasan Statistik")
st.write(df_filtered.head())
