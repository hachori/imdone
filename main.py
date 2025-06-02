import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# 구글 인증 설정
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds_dict = json.loads(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# 구글 시트 연결
sheet = client.open_by_key("1d0z3fyutTRpfRTtYy4yvcjjTtm7lQP5zCIZs0AsUdkc").sheet1

# 페이지 설정
st.set_page_config(page_title="우유 다 먹었어요", page_icon="🥛", layout="centered")

# 앱 제목
st.title("🥛 우유 다 먹었어요!")
st.markdown("**우유를 다 마셨으면, 이름을 입력해주세요!**")

# 입력 폼
with st.form("milk_form"):
    name = st.text_input("이름", max_chars=10, placeholder="이름을 입력하세요")
    submitted = st.form_submit_button("✅ 우유 다 마셨어요!")

    if submitted:
        if name.strip() == "":
            st.warning("이름을 입력해 주세요.")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([name.strip(), now])
            st.success(f"🥛 {name} 님, 잘했어요! 우유 다 마신 걸 기록했어요.")

st.markdown("---")
st.subheader("📋 우유 다 마신 친구들")

# 대시보드 표시
data = sheet.get_all_records()
if data:
    df = pd.DataFrame(data)
    df.index += 1
    df.columns = ['이름', '등록시간']
    st.dataframe(df, use_container_width=True)
else:
    st.info("아직 등록된 친구가 없어요.")
