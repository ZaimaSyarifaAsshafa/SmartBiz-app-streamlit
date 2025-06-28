import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import plotly.express as px

# ---------- SETUP ---------- #
st.set_page_config(page_title="SmartBiz", layout="wide", initial_sidebar_state="collapsed")
blue_sky = "#87CEEB"
st.markdown(f"<style>body {{ background-color: {blue_sky}; }}</style>", unsafe_allow_html=True)

# ---------- SESSION STATE ---------- #
if "page" not in st.session_state:
    st.session_state.page = "home"
if "valid_file" not in st.session_state:
    st.session_state.valid_file = False
if "df" not in st.session_state:
    st.session_state.df = None
if "info" not in st.session_state:
    st.session_state.info = {}

# ---------- HALAMAN: HOME ---------- #
def home_page():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("<h1 style='margin-bottom:0;'>SmartBiz</h1>", unsafe_allow_html=True)
    with col2:
        if st.button("❔ Panduan"):
            st.session_state["show_guide"] = True

    if st.session_state.get("show_guide", False):
        st.markdown("---")
        with st.expander("📘 Panduan Penggunaan", expanded=True):
            st.markdown("""
            **Langkah-langkah:**
            1. Isi informasi usaha: nama, jenis usaha, tahun berdiri.
            2. Upload file data transaksi (.csv/.xlsx) sesuai format.
            3. Jika format salah, gunakan template yang disediakan.
            4. Klik tombol **Getting Started!** untuk melihat analisis dashboard.
            """)
            if st.button("❌ Tutup Panduan"):
                st.session_state["show_guide"] = False

    # UPLOAD
    st.subheader("📤 Upload File Data Transaksi")
    file = st.file_uploader("Unggah file (.csv / .xlsx)", type=["csv", "xlsx"])
    if file:
        try:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
            required_columns = {"Tanggal", "Nama Customer", "Nama Produk", "Kategori", "Jumlah", "Harga", "Total"}
            if required_columns.issubset(df.columns):
                st.session_state.valid_file = True
                st.session_state.df = df
                st.success("✅ Successfully uploaded!")
            else:
                st.session_state.valid_file = False
                st.error("⚠️ Kolom tidak sesuai format. Gunakan file template di bawah.")
        except Exception as e:
            st.session_state.valid_file = False
            st.error(f"⚠️ Gagal membaca file: {e}")
    else:
        st.session_state.valid_file = False

    # FORM
    st.subheader("📋 Informasi Usaha")
    with st.form(key="info_form"):
        nama = st.text_input("Nama Usaha")
        jenis = st.selectbox("Jenis Usaha", ["Makanan", "Fashion", "Elektronik", "Jasa", "Lainnya"])
        tahun = st.number_input("Tahun Berdiri", min_value=1950, max_value=2025, step=1)

        submit = st.form_submit_button("🚀 Getting Started!")
        if submit:
            if not st.session_state.valid_file:
                st.warning("⚠️ Harap upload file data transaksi yang valid terlebih dahulu.")
            elif not nama.strip():
                st.warning("⚠️ Nama usaha harus diisi sebelum melanjutkan.")
            else:
                st.session_state.info = {"nama": nama, "jenis": jenis, "tahun": tahun}
                st.session_state.page = "dashboard"
                st.rerun()

    # DOWNLOAD TEMPLATE
    st.markdown("### 📥 Unduh Format Template:")
    colcsv, colsheet = st.columns(2)
    template_data = pd.DataFrame({
        "Tanggal": ["2024-01-01"],
        "Nama Customer": ["Contoh Pelanggan"],
        "Nama Produk": ["Contoh Produk"],
        "Kategori": ["Minuman"],
        "Jumlah": [5],
        "Harga": [10000],
        "Total": [50000]
    })
    with colcsv:
        csv_buffer = template_data.to_csv(index=False)
        st.download_button("📎 Format CSV", csv_buffer, "format_template.csv", mime="text/csv")
    with colsheet:
        excel_bytes = BytesIO()
        template_data.to_excel(excel_bytes, index=False)
        st.download_button("📄 Excel Format", excel_bytes.getvalue(), "format_template.xlsx")

    st.markdown("---")  
    st.markdown("""<footer style='text-align: center; padding: 10px;'><p>© 2025 SmartBiz. All rights reserved.</p></footer>""", unsafe_allow_html=True)

# ---------- HALAMAN: DASHBOARD ---------- #
def dashboard_page():
    info = st.session_state.info
    df = st.session_state.df.copy()
    
    st.markdown("## 📊 Dashboard Analisis Bisnis - SmartBiz")
    st.markdown("Berikut ini analisis bisnis kamu")

    # --- Informasi Usaha
    st.markdown("### 📋 Informasi Usaha")
    col1, col2, col3 = st.columns(3)
    with col1: st.write(f"**Nama Usaha:** {info['nama']}")
    with col2: st.write(f"**Jenis Usaha:** {info['jenis']}")
    with col3: st.write(f"**Usia Usaha:** {datetime.now().year - int(info['tahun'])} tahun")

    # --- Preprocessing
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df.sort_values("Tanggal", inplace=True)

    # --- Filter
    st.markdown("### 🔍 Filter Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        date_range = st.date_input("Rentang Tanggal", [df["Tanggal"].min(), df["Tanggal"].max()])
    with col2:
        kategori_filter = st.multiselect("Jenis Produk", df["Kategori"].unique().tolist(), default=df["Kategori"].unique().tolist())
    with col3:
        # Multiselect tanpa default (kosong) artinya awalnya semua ditampilkan
        customer_filter = st.multiselect("Nama Customer", df["Nama Customer"].unique().tolist())

    # Terapkan filter jika tanggal valid
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

        # Filter tanggal & kategori dulu
        filtered_df = df[
            df["Tanggal"].between(start_date, end_date) &
            df["Kategori"].isin(kategori_filter)
        ]

        # Kalau user milih customer, baru di-filter berdasarkan itu
        if customer_filter:
            filtered_df = filtered_df[filtered_df["Nama Customer"].isin(customer_filter)]
    else:
        filtered_df = df.copy()

    # --- Tabel Data Penjualan
    st.markdown("### 🧾 Data Penjualan")
    st.dataframe(filtered_df, use_container_width=True, height=300)

    # --- Ringkasan Bisnis
    st.markdown("### 📌 Ringkasan Bisnis")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("💰 Omset", f"Rp {filtered_df['Total'].sum():,.0f}")
    with col2:
        st.metric("📦 Total Order", f"{filtered_df.shape[0]}")
    with col3:
        st.metric("🧍 Total Customer", f"{filtered_df['Nama Customer'].nunique()}")
    with col4:
        avg_order = filtered_df['Total'].mean() if not filtered_df.empty else 0
        st.metric("🧮 AOV", f"Rp {avg_order:,.0f}")
    with col5:
        st.metric("🛒 Produk Unik Terjual", f"{filtered_df['Nama Produk'].nunique()}")

    # --- 2 Kolom Visualisasi PIE
    st.markdown("### 📊 Distribusi Penjualan")
    col1, col2 = st.columns(2)
    with col1:
        pie1 = filtered_df.groupby("Nama Produk")["Total"].sum().reset_index()
        st.plotly_chart(px.pie(pie1, names="Nama Produk", values="Total", title="Omset per Produk"), use_container_width=True)
    with col2:
        pie2 = filtered_df.groupby("Nama Produk")["Jumlah"].sum().reset_index()
        st.plotly_chart(px.pie(pie2, names="Nama Produk", values="Jumlah", title="Order per Produk"), use_container_width=True)

    # --- Horizontal Bar Charts
    custom_blue = [
    [0.0, "#a6c8ff"],   # biru muda, tapi tetap kelihatan
    [0.5, "#468df2"],   # biru sedang
    [1.0, "#1d4ed8"]    # biru gelap
    ]

    st.markdown("### 🥇 Ranking Produk & Pelanggan")
    col1, col2 = st.columns(2)

    with col1:
        rank_qty = filtered_df.groupby("Nama Produk")["Jumlah"].sum().sort_values(ascending=False).head(10).reset_index()
        fig1 = px.bar(
            rank_qty,
            x="Jumlah",
            y="Nama Produk",
            orientation="h",
            color="Jumlah",
            color_continuous_scale=custom_blue,
            title="TOP Product (by Order)",
            category_orders={"Nama Produk": rank_qty["Nama Produk"].tolist()}
        )
        fig1.update_coloraxes(showscale=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        rank_cat = filtered_df.groupby("Kategori")["Jumlah"].count().sort_values(ascending=False).reset_index()
        fig2 = px.bar(
            rank_cat,
            x="Jumlah",
            y="Kategori",
            orientation="h",
            color="Jumlah",
            color_continuous_scale=custom_blue,
            title="TOP Product Category (by Order)",
            category_orders={"Kategori": rank_cat["Kategori"].tolist()}
        )
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Loyal customer
    loyal = filtered_df.groupby("Nama Customer")["Total"].sum().sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(
        loyal,
        x="Total",
        y="Nama Customer",
        orientation="h",
        color="Total",
        color_continuous_scale=custom_blue,
        title="TOP Loyal Customer (by Total Spending)",
        category_orders={"Nama Customer": loyal["Nama Customer"].tolist()}
    )
    fig3.update_coloraxes(showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    # --- Line & Bar Chart: Order by Waktu
    st.markdown("### ⏰ Pola Pemesanan")
    col1, col2 = st.columns(2)
    with col1:
        df_daily = filtered_df.groupby("Tanggal")["Jumlah"].sum().reset_index()
        st.plotly_chart(px.line(df_daily, x="Tanggal", y="Jumlah", title="Order Harian"), use_container_width=True)
    with col2:
        df_monthly = filtered_df.copy()
        df_monthly["Bulan"] = df_monthly["Tanggal"].dt.to_period("M").astype(str)
        monthly_order = df_monthly.groupby("Bulan")["Jumlah"].sum().reset_index()
        st.plotly_chart(px.bar(monthly_order, x="Bulan", y="Jumlah", title="Order Bulanan"), use_container_width=True)

    # --- Order per Hari dalam Minggu
    st.markdown("### 📅 Pola Order per Hari")
    df_day = filtered_df.copy()
    df_day["Hari"] = df_day["Tanggal"].dt.day_name()
    df_day_avg = df_day.groupby("Hari")["Jumlah"].mean().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]).reset_index()
    st.plotly_chart(px.bar(df_day_avg, x="Hari", y="Jumlah", title="Rata-rata Order per Hari"), use_container_width=True)

    # --- Insight
    bulan_tertinggi = monthly_order.loc[monthly_order['Jumlah'].idxmax(), 'Bulan'] if not monthly_order.empty else "Data tidak tersedia"
    produk_terlaris = pie1.loc[pie1['Total'].idxmax(), 'Nama Produk'] if not pie1.empty else "Data tidak tersedia"
    pelanggan_loyal = loyal.loc[0, 'Nama Customer'] if not loyal.empty else "Data tidak tersedia"

    # Insight tambahan
    total_sales = filtered_df["Total"].sum()
    top_produk_jumlah = pie2.loc[pie2['Jumlah'].idxmax(), 'Nama Produk'] if not pie2.empty else "Data tidak tersedia"
    total_transaksi = filtered_df.shape[0]
    aov = filtered_df["Total"].mean() if not filtered_df.empty else 0
    jumlah_customer = filtered_df["Nama Customer"].nunique()

    top3_produk = pie1.sort_values("Total", ascending=False).head(3)["Nama Produk"].tolist()
    top_kategori = rank_cat.sort_values("Jumlah", ascending=False).head(1)["Kategori"].values[0] if not rank_cat.empty else "-"
    transaksi_harian = df_day_avg["Jumlah"].mean() if not df_day_avg.empty else 0
    hari_terbanyak = df_day_avg.loc[df_day_avg["Jumlah"].idxmax(), "Hari"] if not df_day_avg.empty else "-"
    hari_tersibuk_value = df_day_avg["Jumlah"].max() if not df_day_avg.empty else 0

    # Insight ditampilkan
    st.markdown("### 💡 Insight Summary")
    st.info(f"""
    ✅ **Bulan Tertinggi**: Puncak aktivitas penjualan terjadi di bulan **{bulan_tertinggi}** — bisa menjadi momentum untuk promosi musiman atau bundling produk.
    
    🔝 **Produk Terlaris**: Produk dengan omset tertinggi adalah **{produk_terlaris}**.
    
    🏆 **3 produk dengan kontribusi omset terbesar** adalah: `{', '.join(top3_produk)}` — pertimbangkan untuk dijadikan fokus utama promosi atau stok buffer.
    
    👥 **Customer Loyal**: Pelanggan dengan pembelanjaan tertinggi adalah **{pelanggan_loyal}** — dapat dimasukkan ke program loyalitas atau penawaran eksklusif.
    
    📦 **Kategori Terpopuler**: Kategori produk yang paling sering dipesan adalah **{top_kategori}** — ini bisa jadi andalan lini produk utama.
    
    🕐 **Hari Tersibuk**: Penjualan paling ramai terjadi setiap hari **{hari_terbanyak}** (rata-rata `{hari_tersibuk_value:.1f}` order/hari).  
    
    Gunakan hari tersebut untuk promosi terbatas seperti “Happy Hour” atau “Diskon Khusus Hari Ini”.
    
    📉 **Hari Sepi?** Hari dengan aktivitas order terendah bisa dianalisis lebih lanjut untuk mencari tahu penyebabnya (misal: jadwal buka, promosi kurang, cuaca, dll).
    
    💰 **AOV & Omset**: Rata-rata transaksi sebesar `Rp {aov:,.0f}`, dan total omset `Rp {total_sales:,.0f}` — dapat digunakan sebagai acuan untuk target bulanan atau benchmarking kinerja toko.
    
    🛒 **Total Transaksi**: Terdapat `{total_transaksi}` transaksi dari `{jumlah_customer}` pelanggan unik — pertimbangkan untuk meningkatkan retensi pelanggan melalui program loyalitas atau promosi khusus
    """)

    # --- Placeholder ML & Chatbot
    st.markdown("### 🧠 Rekomendasi AI")
    st.warning("Fitur rekomendasi berbasis Machine Learning akan segera tersedia!")

    st.markdown("### 🤖 Chatbot Konsultasi Bisnis")
    st.warning("Fitur chatbot integrasi Hugging Face sedang dikembangkan.")

    if st.button("⬅️ Kembali ke Home"):
        st.session_state.page = "home"
        st.rerun()

# ---------- ROUTING ---------- #
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "dashboard":
    dashboard_page()   