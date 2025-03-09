import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    day_df = pd.read_csv("day.csv", parse_dates=["dteday"])
    hour_df = pd.read_csv("hour.csv", parse_dates=["dteday"])
    return day_df, hour_df

day_df, hour_df = load_data()

# Konversi kolom numerik menjadi kategori dengan label deskriptif
category_mappings = {
    "season": {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"},
    "yr": {0: "2011", 1: "2012"},
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
st.subheader("Pengguna Registered vs Casual Berdasarkan Season dan Year")
fig, ax = plt.subplots()
sns.barplot(x='season', y='casual', data=df_filtered, color='red', label='Casual')
sns.barplot(x='season', y='registered', data=df_filtered, color='blue', label='Registered')
ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Pengguna")
ax.legend()
st.pyplot(fig)

fig, ax = plt.subplots()
sns.barplot(x='yr', y='casual', data=df_filtered, color='red', label='Casual')
sns.barplot(x='yr', y='registered', data=df_filtered, color='blue', label='Registered')
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Pengguna")
ax.legend()
st.pyplot(fig)

# Pengaruh cuaca terhadap penyewaan sepeda
st.subheader("Pengaruh Cuaca terhadap Penyewaan Sepeda")
fig, ax = plt.subplots()
sns.barplot(x='weathersit', y='cnt', data=df_filtered, palette="coolwarm")
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Pengaruh cuaca berdasarkan season dan weekday
st.subheader("Pengaruh Cuaca Berdasarkan Musim dan Hari dalam Seminggu")
fig, ax = plt.subplots()
sns.barplot(x='season', y='cnt', hue='weathersit', data=df_filtered, palette="coolwarm")
ax.set_xlabel("Musim")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

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
st.write(df_filtered.describe())
