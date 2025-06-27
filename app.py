import streamlit as st
import pandas as pd
import plotly.express as px
from transformers import pipeline

# Konfigurasi halaman
st.set_page_config(page_title="SmartBiz UMKM Dashboard", layout="wide")
st.title("📊 SmartBiz UMKM Dashboard")
st.subheader("Upload file transaksi UMKM kamu dan lihat insightnya!")

# Upload File
uploaded_file = st.file_uploader("📁 Upload file CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.title()  # Normalisasi header

    st.write("### 🧾 Data Preview")
    st.dataframe(df.head())

    # Filter Tanggal
    st.write("### 📅 Filter Waktu")
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])  # pastikan kolom waktu ada
    start_date = st.date_input("Start Date", df['Tanggal'].min())
    end_date = st.date_input("End Date", df['Tanggal'].max())
    df_filtered = df[(df['Tanggal'] >= pd.to_datetime(start_date)) & (df['Tanggal'] <= pd.to_datetime(end_date))]

    # Dashboard Analitik
    st.header("📊 Analisis Penjualan")
    st.metric("💰 Total Omzet", f"Rp {df_filtered['Total'].sum():,.0f}")

    # Produk Terlaris
    top_product = df_filtered.groupby("Nama Produk")["Jumlah"].sum().sort_values(ascending=False).head(5)
    st.subheader("🔥 Produk Terlaris")
    st.bar_chart(top_product)

    # Kategori Terlaris
    top_kategori = df_filtered.groupby("Kategori")["Jumlah"].sum().sort_values(ascending=False)
    st.subheader("🏷️ Kategori Paling Laku")
    st.bar_chart(top_kategori)

    # Trend Penjualan
    st.subheader("📈 Tren Penjualan Harian")
    trend = df_filtered.groupby("Tanggal")["Total"].sum().reset_index()
    fig = px.line(trend, x="Tanggal", y="Total", title="Trend Omzet Harian")
    st.plotly_chart(fig, use_container_width=True)

    # Rekomendasi AI
    if not top_product.empty and not top_kategori.empty:
        st.header("💡 Rekomendasi Cerdas dari AI")
        
        produk_teratas = top_product.index[0]
        kategori_teratas = top_kategori.index[0]
        total_omzet = df_filtered['Total'].sum()

        prompt = f"""
        Saya adalah pemilik UMKM. Data penjualan saya menunjukkan bahwa produk paling laku adalah {produk_teratas}, dan kategori terbanyak adalah {kategori_teratas}. Total omzet saya adalah Rp {total_omzet:,.0f}.
        Berikan saya rekomendasi bisnis berdasarkan informasi ini.
        """

        text_gen = pipeline("text-generation", model="gpt2", max_new_tokens=80)
        with st.spinner("AI sedang menganalisis..."):
            rekomendasi = text_gen(prompt)[0]['generated_text']
        st.success(rekomendasi)

        # Chatbot Mini
        st.header("🤖 Chat AI Bisnismu")
        user_question = st.text_input("Tanyakan tentang data kamu (misalnya: Apa produk terlaris bulan ini?)")

        if user_question:
            prompt_chat = f"""
            Saya adalah pemilik UMKM. Berikut ringkasan data saya:
            Produk teratas: {produk_teratas}
            Kategori favorit: {kategori_teratas}
            Total omzet: Rp {total_omzet:,.0f}

            Pertanyaan: {user_question}
            Jawab dengan jelas dan praktis.
            """
            chatbot = pipeline("text-generation", model="gpt2", max_new_tokens=80)
            response = chatbot(prompt_chat)[0]['generated_text']
            st.info(response)
    else:
        st.warning("❗ Tidak cukup data untuk menampilkan rekomendasi AI.")
else:
    st.info("Silakan upload file CSV untuk memulai analisis.")