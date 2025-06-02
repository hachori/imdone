import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# --- 구글 인증 ---
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# JSON 키 파일명
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# --- Google Sheet 연결 (URL의 ID 사용) ---
spreadsheet_id = '1d0z3fyutTRpfRTtYy4yvcjjTtm7lQP5zCIZs0AsUdkc'
sheet = client.open_by_key(spreadsheet_id).sheet1  # 첫 번째 시트 사용

# --- Streamlit UI ---
st.title("👋 이름 등록 & 대시보드")

with st.form("name_form"):
    name = st.text_input("당신의 이름을 입력하세요:")
    submitted = st.form_submit_button("등록")

    if submitted and name:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([name, now])
        st.success(f"{name} 님, 등록되었습니다!")

# --- 대시보드 표시 ---
st.subheader("📋 등록자 목록")

data = sheet.get_all_records()
if data:
    df = pd.DataFrame(data)
    df.index += 1
    st.dataframe(df)
else:
    st.write("아직 등록된 이름이 없습니다.")
