import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# JSON을 Secrets에서 로드
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds_dict = json.loads(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# 구글 시트 연결
sheet = client.open_by_key("1d0z3fyutTRpfRTtYy4yvcjjTtm7lQP5zCIZs0AsUdkc").sheet1

# Streamlit UI
st.title("이름 등록")

with st.form("name_form"):
    name = st.text_input("이름을 입력하세요")
    submitted = st.form_submit_button("등록")

    if submitted and name:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([name, now])
        st.success(f"{name} 님이 등록되었습니다.")

# 대시보드 표시
st.subheader("등록자 목록")
data = sheet.get_all_records()
if data:
    df = pd.DataFrame(data)
    df.index += 1
    st.dataframe(df)
else:
    st.info("등록된 데이터가 없습니다.")
