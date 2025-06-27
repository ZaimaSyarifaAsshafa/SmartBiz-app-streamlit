import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SmartBiz UMKM Dashboard", layout="wide")

st.title("📊 SmartBiz UMKM Dashboard")
st.subheader("Upload file transaksi UMKM kamu dan lihat insightnya!")

uploaded_file = st.file_uploader("📁 Upload file CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    st.write("### 🧾 Data Preview")
    st.dataframe(df.head())

    st.write("### 📅 Filter Waktu")
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])  # pastikan kolom waktu ada
    start_date = st.date_input("Start Date", df['Tanggal'].min())
    end_date = st.date_input("End Date", df['Tanggal'].max())
    df_filtered = df[(df['Tanggal'] >= pd.to_datetime(start_date)) & (df['Tanggal'] <= pd.to_datetime(end_date))]

    st.write("### 💸 Total Penjualan")
    total = df_filtered['Total'].sum()
    st.metric("Total Penjualan (Rp)", f"{total:,.0f}")

    st.write("### 📈 Trend Penjualan")
    fig = px.line(df_filtered, x='Tanggal', y='Total', title='Trend Penjualan Harian')
    st.plotly_chart(fig, use_container_width=True)
