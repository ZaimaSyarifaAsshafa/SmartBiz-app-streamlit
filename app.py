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

        submit = st.form_submit_button("🚀 Getting Started!", disabled=not st.session_state.valid_file)
        if submit:
            st.session_state.info = {"nama": nama, "jenis": jenis, "tahun": tahun}
            st.session_state.page = "dashboard"
            st.experimental_rerun()

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

    st.title("📊 Dashboard Analisis Bisnis - SmartBiz")
    st.markdown("Selamat datang kembali, berikut ini analisis data usaha kamu!")

    # INFO USAHA
    st.subheader("📋 Informasi Usaha")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Nama Usaha:** {info['nama']}")
    with col2:
        st.markdown(f"**Jenis Usaha:** {info['jenis']}")
    with col3:
        usia = datetime.now().year - int(info['tahun'])
        st.markdown(f"**Usia Usaha:** {usia} tahun")

    # PREPROCESS
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df.sort_values("Tanggal", inplace=True)

    # FILTER
    st.subheader("🔍 Filter Data")
    col1, col2 = st.columns(2)
    with col1:
        tanggal_min = df["Tanggal"].min()
        tanggal_max = df["Tanggal"].max()
        date_range = st.date_input("Pilih Rentang Tanggal", [tanggal_min, tanggal_max])
    with col2:
        kategori_list = df["Kategori"].unique().tolist()
        kategori_filter = st.multiselect("Pilih Kategori Produk", kategori_list, default=kategori_list)

    filtered_df = df[
        (df["Tanggal"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
        (df["Kategori"].isin(kategori_filter))
    ]

    # VISUALISASI
    st.subheader("📈 Visualisasi Penjualan")
    tab1, tab2, tab3 = st.tabs(["Total Penjualan per Bulan", "Produk Terlaris", "Transaksi per Kategori"])

    with tab1:
        monthly = filtered_df.copy()
        monthly["Bulan"] = monthly["Tanggal"].dt.to_period("M").astype(str)
        grafik = monthly.groupby("Bulan")["Total"].sum().reset_index()
        fig = px.bar(grafik, x="Bulan", y="Total", title="Total Penjualan per Bulan", color_discrete_sequence=["#1f77b4"])
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        top_produk = filtered_df.groupby("Nama Produk")["Total"].sum().sort_values(ascending=False).head(10).reset_index()
        fig2 = px.bar(top_produk, x="Total", y="Nama Produk", orientation='h', title="Top 10 Produk Terlaris", color_discrete_sequence=["#2ca02c"])
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        kategori_count = filtered_df["Kategori"].value_counts().reset_index()
        kategori_count.columns = ["Kategori", "Jumlah Transaksi"]
        fig3 = px.pie(kategori_count, values="Jumlah Transaksi", names="Kategori", title="Distribusi Transaksi per Kategori")
        st.plotly_chart(fig3, use_container_width=True)

    # INSIGHT
    st.subheader("💡 Insight Sistem")
    total_transaksi = filtered_df.shape[0]
    total_penjualan = filtered_df["Total"].sum()
    produk_terlaris = filtered_df.groupby("Nama Produk")["Total"].sum().idxmax()

    st.markdown(f"""
    - Jumlah transaksi pada periode ini: **{total_transaksi}**
    - Total nilai penjualan: **Rp {total_penjualan:,.0f}**
    - Produk dengan penjualan tertinggi: **{produk_terlaris}**
    """)

    # FUTURE FEATURE PLACEHOLDER
    st.markdown("📥 **Download Laporan Bisnis** (fitur dalam pengembangan)")
    st.markdown("🤖 **Butuh konsultasi bisnis?** Chat dengan AI (akan segera tersedia)")

    st.markdown("---")
    st.markdown("Terima kasih telah menggunakan SmartBiz! Hubungi kami di @smartbiz_support.gmail.com.")
    st.markdown("---\nMade with ❤️ by SmartBiz Team")

    if st.button("⬅️ Kembali ke Home"):
        st.session_state.page = "home"
        st.experimental_rerun()

# ---------- ROUTING ---------- #
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "dashboard":
    dashboard_page()   