import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# --------------------
# CONFIG
# --------------------
SHEET_ID = "17yWg2YpqnPBCPTz4TrYeRjhJlm28jvwSL1WJ4Nu7SJ8"
GID = 1367381343

st.set_page_config(
    page_title="Operasyon Dashboard",
    layout="wide"
)

st.title("📊 Operasyonel Performans Dashboard")

# --------------------
# GOOGLE SHEETS BAĞLANTI
# --------------------
@st.cache_data(ttl=600)
def load_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    ws = client.open_by_key(SHEET_ID).get_worksheet_by_id(GID)
    df = pd.DataFrame(ws.get_all_records())
    return df

df = load_data()

# --------------------
# TARİH
# --------------------
if "Tarih" in df.columns:
    df["Tarih"] = pd.to_datetime(df["Tarih"])

# --------------------
# SIDEBAR FİLTRE
# --------------------
st.sidebar.header("🔍 Filtreler")

rapor_tipi = st.sidebar.selectbox(
    "Rapor Tipi",
    ["Tümü", "Günlük", "Haftalık"]
)

if rapor_tipi == "Günlük" and "Tarih" in df.columns:
    df = df[df["Tarih"].dt.date == datetime.today().date()]

elif rapor_tipi == "Haftalık" and "Tarih" in df.columns:
    df = df[df["Tarih"] >= datetime.today() - timedelta(days=7)]

# --------------------
# HESAPLAMALAR
# --------------------
if {"Planlanan_KM", "Gerceklesen_KM"}.issubset(df.columns):
    df["KM_Fark"] = df["Gerceklesen_KM"] - df["Planlanan_KM"]

# --------------------
# KPI
# --------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Toplam Kayıt", len(df))

if "KM_Fark" in df.columns:
    col2.metric("Ort. KM Fark", round(df["KM_Fark"].mean(), 2))
    col3.metric("Max KM Sapma", round(df["KM_Fark"].max(), 2))

if "Geofence_Durum" in df.columns:
    geo_out = (df["Geofence_Durum"] == "Dışında").mean() * 100
    col4.metric("Geofence Dışı %", round(geo_out, 2))

# --------------------
# GRAFİKLER
# --------------------
st.divider()

colA, colB = st.columns(2)

if "KM_Fark" in df.columns:
    fig_km = px.histogram(
        df,
        x="KM_Fark",
        nbins=30,
        title="KM Fark Dağılımı"
    )
    colA.plotly_chart(fig_km, use_container_width=True)

if "Geofence_Durum" in df.columns:
    fig_geo = px.pie(
        df,
        names="Geofence_Durum",
        title="Geofence Durumu"
    )
    colB.plotly_chart(fig_geo, use_container_width=True)

# --------------------
# ADRES DOĞRULUK
# --------------------
if "Adres_Dogru" in df.columns:
    adres_kpi = (
        df["Adres_Dogru"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .reset_index()
        .rename(columns={"index": "Durum", "Adres_Dogru": "Yüzde"})
    )

    fig_adres = px.bar(
        adres_kpi,
        x="Durum",
        y="Yüzde",
        title="Adres Doğruluk Oranı (%)",
        text="Yüzde"
    )
    st.plotly_chart(fig_adres, use_container_width=True)

# --------------------
# TABLO
# --------------------
st.divider()
st.subheader("📋 Detay Veri")
st.dataframe(df, use_container_width=True)
