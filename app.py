import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SHEET_ID = "17yWg2YpqnPBCPTz4TrYeRjhJlm28jvwSL1WJ4Nu7SJ8"
GID = 1367381343

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

gc = gspread.authorize(creds)

ws = gc.open_by_key(SHEET_ID).get_worksheet_by_id(GID)
df = pd.DataFrame(ws.get_all_records())

st.write(df.head())
