import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import plotly.express as px
import base64

st.set_page_config(
    page_title='SmartBiz UMKM Dashboard',
    page_icon="📈",  
    initial_sidebar_state="expanded"
)

# ---------- SETUP ---------- #
st.set_page_config(page_title="SmartBiz", layout="wide", initial_sidebar_state="collapsed")

# Warna background halaman
blue_sky = "#E2F9FF"
st.markdown(f"<style>body {{ background-color: {blue_sky}; }}</style>", unsafe_allow_html=True)

# Style untuk form input
st.markdown("""
    <style>
    /* Umum untuk semua input */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div input {
        background-color: #F8FEFF;  /* ganti abu jadi putih kebiruan */
        color: black;
        border: 1px solid #9AE1FF;
        border-radius: 8px;
    }      
             
    /* Khusus tombol + dan - pada NumberInput */
    .stNumberInput button {
        background-color: #F8FEFF;
        color: black;
        border: 1px solid #9AE1FF;
    }

    /* Hover & fokus */
    .stNumberInput > div > div input:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus {
        border: 2px solid #62c4e6;
        outline: none;
    }

    /* Label */
    label {
        color: #9AE1FF;
        font-weight: bold;
    }
            
    /* Ubah warna tag di multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #d0e7ff !important;  /* pastel biru */
        color: #003366 !important;            /* teks biru tua */
        border: none !important;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        color: #003366 !important;
    }  
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER UI STYLE ---------- #
st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(to bottom, #e0f0ff, #ffffff);
            padding: 30px 30px 20px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .header-content {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .header-content img {
            width: 60px;
            height: 60px;
        }

        .header-title {
            font-size: 56px;
            font-weight: 700;
            color: #1a2e44;
            margin: 0;
        }

        .header-subtitle {
            font-size: 16px;
            color: #5e6a75;
            margin: 4px 0 0 0;
        }
    </style>

    <div class="header-container">
        <div class="header-content">
            <img src="https://cdn-icons-png.flaticon.com/512/6062/6062646.png" alt="Business Icon">
            <div>
                <p class="header-title">Dashboard Analisis Bisnis - SmartBiz</p>
                <p class="header-subtitle">Berikut ini analisis bisnis kamu</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ---------- #
if "generating_pdf" not in st.session_state:
    st.session_state.generating_pdf = False

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

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
        st.markdown("""
        <h1 style='margin-bottom:0;'>SmartBiz</h1>
        <p style='margin-top:0; font-size:18px; color:gray;'>Solusi Analytics Sederhana untuk Bisnis Cerdas 💡</p>
        """, unsafe_allow_html=True)

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
            4. Klik tombol **Mulai Analisis!** untuk melihat analisis dashboard.
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

        submit = st.form_submit_button("🚀 Mulai Analisis!")
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
    st.markdown("""<footer style='text-align: center; padding: 10px;'><p>© 2025 SmartBiz by Zai. All rights reserved.</p></footer>""", unsafe_allow_html=True)

# ---------- HALAMAN: DASHBOARD ---------- #
def plot_to_base64(fig):
    img_bytes = fig.to_image(format="png", width=800, height=400)
    return base64.b64encode(img_bytes).decode("utf-8")

def img_tag(fig):
    return f'<img src="data:image/png;base64,{plot_to_base64(fig)}" style="width:100%; margin-bottom:20px;" />'

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
    color_sequence = px.colors.qualitative.Pastel

    col1, col2 = st.columns(2)
    # Omset per Produk
    with col1:
        pie1 = filtered_df.groupby("Nama Produk")["Total"].sum().reset_index()
        fig1 = px.pie(
            pie1,
            names="Nama Produk",
            values="Total",
            title="Omset per Produk",
            color_discrete_sequence=color_sequence
        )
        st.plotly_chart(fig1, use_container_width=True)
    # Order per Produk
    with col2:
        pie2 = filtered_df.groupby("Nama Produk")["Jumlah"].sum().reset_index()
        fig2 = px.pie(
            pie2,
            names="Nama Produk",
            values="Jumlah",
            title="Order per Produk",
            color_discrete_sequence=color_sequence
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- Horizontal Bar Charts
    custom_blue = [
        [0.0, "#a9d1f6"],  
        [0.5, "#75b2f9"],  
        [1.0, "#3681c4"]   
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
    top_produk_jumlah_list = pie2.sort_values("Jumlah", ascending=False).head(3)["Nama Produk"].tolist() if not pie2.empty else []
    top_produk_jumlah = ', '.join(top_produk_jumlah_list) if top_produk_jumlah_list else "Data tidak tersedia"
    total_sales = filtered_df["Total"].sum()
    top_produk_jumlah_list = pie2.sort_values("Jumlah", ascending=False).head(3)["Nama Produk"].tolist() if not pie2.empty else []
    top_produk_jumlah = ', '.join(top_produk_jumlah_list) if top_produk_jumlah_list else "Data tidak tersedia"
    total_transaksi = filtered_df.shape[0]
    aov = filtered_df["Total"].mean() if not filtered_df.empty else 0
    jumlah_customer = filtered_df["Nama Customer"].nunique()

    top3_produk = pie1.sort_values("Total", ascending=False).head(3)["Nama Produk"].tolist()
    top_kategori = rank_cat.sort_values("Jumlah", ascending=False).head(1)["Kategori"].values[0] if not rank_cat.empty else "-"
    transaksi_harian = df_day_avg["Jumlah"].mean() if not df_day_avg.empty else 0
    hari_terbanyak = df_day_avg.loc[df_day_avg["Jumlah"].idxmax(), "Hari"] if not df_day_avg.empty else "-"
    hari_tersibuk_value = df_day_avg["Jumlah"].max() if not df_day_avg.empty else 0

    # --- Pareto Produk
    pareto_produk = filtered_df.groupby("Nama Produk")["Total"].sum().sort_values(ascending=False)
    pareto_produk_cumsum_pct = pareto_produk.cumsum() / pareto_produk.sum()
    # Ambil yang kontribusi kumulatif ≤ 80%
    produk_top_pareto = pareto_produk_cumsum_pct[pareto_produk_cumsum_pct <= 0.8].index.tolist()
    pareto_produk_detail = pareto_produk.loc[produk_top_pareto]
    # Buat DataFrame tabel
    produk_pareto_tabel = pareto_produk_detail.reset_index()
    produk_pareto_tabel.columns = ["Nama Produk", "Total"]
    produk_pareto_tabel["Persen"] = (produk_pareto_tabel["Total"] / pareto_produk.sum()) * 100
    produk_pareto_tabel = produk_pareto_tabel.sort_values("Total", ascending=False)

    # --- Pareto Customer
    pareto_customer = filtered_df.groupby("Nama Customer")["Total"].sum().sort_values(ascending=False)
    pareto_customer_cumsum_pct = pareto_customer.cumsum() / pareto_customer.sum()
    # Ambil yang kontribusi kumulatif ≤ 80%
    customer_top_pareto = pareto_customer_cumsum_pct[pareto_customer_cumsum_pct <= 0.8].index.tolist()
    pareto_customer_detail = pareto_customer.loc[customer_top_pareto]
    # Buat DataFrame tabel
    customer_pareto_tabel = pareto_customer_detail.reset_index()
    customer_pareto_tabel.columns = ["Nama Customer", "Total"]
    customer_pareto_tabel["Persen"] = (customer_pareto_tabel["Total"] / pareto_customer.sum()) * 100
    customer_pareto_tabel = customer_pareto_tabel.sort_values("Total", ascending=False)

    # --- DataFrame Produk
    produk_pareto_df = pareto_produk_detail.reset_index()
    produk_pareto_df.columns = ["Nama Produk", "Omset"]
    produk_pareto_df["%"] = (produk_pareto_df["Omset"] / pareto_produk.sum()) * 100
    produk_pareto_df["Omset"] = produk_pareto_df["Omset"].round(0).astype(int)
    produk_pareto_df["%"] = produk_pareto_df["%"].round(1)

    # --- DataFrame Customer
    customer_pareto_df = pareto_customer_detail.reset_index()
    customer_pareto_df.columns = ["Nama Customer", "Omset"]
    customer_pareto_df["%"] = (customer_pareto_df["Omset"] / pareto_customer.sum()) * 100
    customer_pareto_df["Omset"] = customer_pareto_df["Omset"].round(0).astype(int)
    customer_pareto_df["%"] = customer_pareto_df["%"].round(1)

    # --- INsight Pareto
    st.markdown("### 📈 Analisis Pareto")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Detail Produk (Kontributor 80% Omset)")
        st.dataframe(produk_pareto_df, height=300, use_container_width=True)
    with col2:
        st.markdown("### 👑 Detail Customer (Kontributor 80% Omset)")
        st.dataframe(customer_pareto_df, height=300, use_container_width=True)


    # Insight ditampilkan
    st.markdown("### 💡 Insight Summary")
    st.info(f"""
    💰 **Omset & AOV**: Total omset sebesar Rp {total_sales:,.0f}, dengan rata-rata nilai transaksi (AOV) Rp {aov:,.0f} — menjadi tolok ukur performa bisnis.

    🛒 **Transaksi & Customer**: Terdapat {total_transaksi} transaksi dari {jumlah_customer} pelanggan unik — bisa ditingkatkan dengan program loyalitas atau retensi.

    📆 **Bulan Tertinggi**: Aktivitas penjualan tertinggi terjadi di bulan **{bulan_tertinggi}** — manfaatkan momen ini untuk promosi musiman.

    🕐 **Hari Tersibuk**: Penjualan terbanyak terjadi setiap hari **{hari_terbanyak}** (rata-rata {hari_tersibuk_value:.1f} order/hari) — cocok untuk promo terbatas seperti flash sale atau happy hour.

    📉 **Hari Sepi**: Hari sepi bisa dianalisis lebih lanjut (misalnya: jadwal buka, cuaca, promosi kurang aktif).

    📈 **Rata-rata Order per Hari**: {transaksi_harian:.1f} order/hari — bisa dijadikan tolok ukur ritme harian.

    📦 **Kategori Terpopuler**: Produk terbanyak terjual berasal dari kategori **{top_kategori}** — cocok jadi andalan lini utama.

    🔝 **Produk Terlaris**: Produk dengan omset tertinggi adalah **{produk_terlaris}**.

    🏆 **Top 3 Produk Omset**: {', '.join(top3_produk)} — layak diprioritaskan dalam stok, promosi, dan bundling.

    🏅 **Top 3 Produk Jumlah Order**: {top_produk_jumlah} — fokus pada produk ini untuk meningkatkan volume penjualan.

    📊 **Pareto Produk**: Hanya {len(produk_top_pareto)} produk (sekitar 20%) menyumbang >80% dari total omset — fokus promosi & stok pada produk ini untuk efisiensi.

    👑 **Pareto Customer**: {len(customer_top_pareto)} pelanggan menyumbang >80% dari penjualan — ideal ditarget dengan program loyalitas atau benefit eksklusif.
    """)

    # --- Download Report
    def generate_summary_report(info, filtered_df, start_date, end_date, pie1, pie2, loyal, df_day_avg, monthly_order, rank_cat):
        nama = info['nama']
        jenis = info['jenis']
        usia = datetime.now().year - int(info['tahun'])

        total_transaksi = filtered_df.shape[0]
        total_omset = filtered_df['Total'].sum()
        avg_order = filtered_df['Total'].mean() if not filtered_df.empty else 0
        total_customer = filtered_df['Nama Customer'].nunique()

        produk_terlaris = pie1.loc[pie1['Total'].idxmax(), 'Nama Produk'] if not pie1.empty else "-"
        bulan_tertinggi = monthly_order.loc[monthly_order['Jumlah'].idxmax(), 'Bulan'] if not monthly_order.empty else "-"
        hari_terbanyak = df_day_avg.loc[df_day_avg["Jumlah"].idxmax(), "Hari"] if not df_day_avg.empty else "-"
        hari_tersibuk_value = df_day_avg["Jumlah"].max() if not df_day_avg.empty else 0
        hari_tersepi = df_day_avg.loc[df_day_avg["Jumlah"].idxmin(), "Hari"] if not df_day_avg.empty else "-"

        html_report = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 40px;
                    color: #333;
                    background-color: #f9f9fb;
                    line-height: 1.6;
                    font-size: 15px;
                }}

                h1 {{
                    color: #68A1E1;
                    font-size: 26px;
                    margin-bottom: 10px;
                }}

                h2 {{
                    color: #333;
                    font-size: 20px;
                    margin-top: 30px;
                    margin-bottom: 10px;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 4px;
                }}

                ul {{
                    padding-left: 25px;
                    margin-top: 5px;
                }}

                li {{
                    margin-bottom: 8px;
                }}

                b {{
                    color: #073E34;
                }}

                .section {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 25px;
                    box-shadow: 0px 1px 3px rgba(0,0,0,0.05);
                }}

                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 10px;
                }}

                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    font-size: 14px;
                }}

                th {{
                    background-color: #f0f0f0;
                    color: #333;
                }}

                .scrollable-table {{
                    overflow-x: auto; 
                }}

                .table-container {{
                    display: flex;
                    gap: 40px;
                }}

                .table-box {{
                    flex: 1;
                }}
            </style>
        </head>
        <body>

            <div class="section">
                <h1>📊 SmartBiz Business Summary Report</h1>
                <p style="margin-top:-5px;">Laporan ringkas performa usaha berbasis data transaksi</p>
            </div>

            <div class="section">
                <h2>📋 Informasi Usaha</h2>
                <ul>
                    <li>🏢 <b>Nama Usaha:</b> {nama}</li>
                    <li>🔧 <b>Jenis Usaha:</b> {jenis}</li>
                    <li>📅 <b>Tahun Berdiri:</b> {info['tahun']}</li>
                    <li>⏳ <b>Usia Usaha:</b> {usia} tahun</li>
                </ul>
            </div>

            <div class="section">
                <h2>📌 Ringkasan Penjualan</h2>
                <p>📆 Periode: <b>{start_date.date()}</b> s.d. <b>{end_date.date()}</b></p>
                <ul>
                    <li>🧾 <b>Total Transaksi:</b> {total_transaksi}</li>
                    <li>💰 <b>Total Omset:</b> Rp {total_omset:,.0f}</li>
                    <li>📈 <b>Rata-rata Transaksi (AOV):</b> Rp {avg_order:,.0f}</li>
                    <li>🧍 <b>Jumlah Customer Unik:</b> {total_customer}</li>
                    <li>🥇 <b>Produk Terlaris:</b> {produk_terlaris}</li>
                </ul>
            </div>

            <div class="section">
                <h2>📅 Pola Order</h2>
                <ul>
                    <li>📊 <b>Bulan Paling Ramai:</b> {bulan_tertinggi}</li>
                    <li>🔥 <b>Hari Tersibuk:</b> {hari_terbanyak} (avg {hari_tersibuk_value:.1f} order)</li>
                    <li>😴 <b>Hari Tersepi:</b> {hari_tersepi}</li>
                </ul>
            </div>

            <div class="section">
                <h2>🧠 Insight & Rekomendasi</h2>
                <ul>
                    <li>🚀 Fokus promosi ke produk <b>{produk_terlaris}</b></li>
                    <li>🏅 Fokus volume ke produk: <b>{top_produk_jumlah}</b></li>
                    <li>📦 Manfaatkan hari <b>{hari_terbanyak}</b> untuk promo bundling atau flash sale</li>
                    <li>🔍 Evaluasi performa hari <b>{hari_tersepi}</b></li>
                </ul>
            </div>

            <div class="section">
            <h2>📊 Analisis Pareto (80/20)</h2>
            <p>Berikut adalah produk dan customer yang menyumbang lebih dari 80% total omset:</p>

            <h3>📦 Detail Produk (Kontributor 80% Omset)</h3>
            <div class="scrollable-table">
                <table>
                    <tr><th>Nama Produk</th><th>Omset</th><th>%</th></tr>
                    {''.join([f"<tr><td>{row['Nama Produk']}</td><td>Rp {row['Total']:,.0f}</td><td>{row['Persen']:.1f}%</td></tr>" for _, row in produk_pareto_tabel.iterrows()])}
                </table>
            </div>

            <h3>👥 Detail Customer (Kontributor 80% Omset)</h3>
            <div class="scrollable-table">
                <table>
                    <tr><th>Nama Customer</th><th>Omset</th><th>%</th></tr>
                    {''.join([f"<tr><td>{row['Nama Customer']}</td><td>Rp {row['Total']:,.0f}</td><td>{row['Persen']:.1f}%</td></tr>" for _, row in customer_pareto_tabel.iterrows()])}
                </table>
            </div>
        </div>
        </body>
        </html>
        """
        return html_report
    
    # === Generate PDF
    if st.button("🛠️ Generate HTML Summary Report"):
        summary_html = generate_summary_report(
            info, filtered_df, start_date, end_date,
            pie1, pie2, loyal, df_day_avg, monthly_order, rank_cat
        )
        html_bytes = summary_html.encode("utf-8")

        # Tombol download HTML
        st.download_button(
            label="📥 Download Summary Report (HTML)",
            data=html_bytes,
            file_name="SmartBiz_Summary_Report.html",
            mime="text/html"
        )

        # Preview langsung di halaman Streamlit
        st.markdown("### 🖥️ Preview Laporan")
        st.components.v1.html(summary_html, height=600, scrolling=True)

        st.info("✅ File HTML berhasil dibuat. Kamu bisa buka hasilnya di browser lalu tekan **Ctrl+P → Save as PDF** untuk menyimpannya.")

    # ⬅️ TOMBOL KEMBALI (Selalu tampil)
    st.markdown("---")
    if st.button("⬅️ Kembali ke Home"):
        st.session_state.page = "home"
        st.rerun()

# ---------- ROUTING ---------- #
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "dashboard":
    dashboard_page()   