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
# secrets에서 Google Sheet ID 불러오기
try:
    google_sheet_id = st.secrets["google_sheet_id"]
    sheet = client.open_by_key(google_sheet_id).sheet1
except KeyError:
    st.error("secrets.toml 파일에 'google_sheet_id'가 설정되어 있지 않습니다. 설정해주세요.")
    st.stop() # 앱 실행 중지
except Exception as e:
    st.error(f"Google Sheet 연결 중 오류 발생: {e}")
    st.exception(e) # 자세한 트레이스백 출력
    st.stop() # 앱 실행 중지


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
            # 데이터 기록 중 오류 처리 추가
            try:
                sheet.append_row([name.strip(), now])
                st.success(f"🥛 {name} 님, 잘했어요! 우유 다 마신 걸 기록했어요.")
            except Exception as e:
                st.error(f"데이터 기록 중 오류 발생: {e}")
                st.exception(e) # 개발 모드에서 자세한 오류 확인

st.markdown("---")
st.subheader("📋 우유 다 마신 친구들")

# 대시보드 표시
# 데이터 불러오는 중 오류 처리 추가
try:
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        df.index += 1
        df.columns = ['이름', '등록시간'] # 시트의 첫 행이 헤더로 사용되지 않는 경우, 수동으로 컬럼명 설정 필요
        st.dataframe(df, use_container_width=True)
    else:
        st.info("아직 등록된 친구가 없어요.")
except Exception as e:
    st.error(f"대시보드 데이터를 불러오는 중 오류 발생: {e}")
    st.exception(e) # 개발 모드에서 자세한 오류 확인
