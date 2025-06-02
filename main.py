import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import plotly.express as px # Plotly Express 임포트

# --- 구글 인증 및 시트 연결 (기존 코드와 동일) ---
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds_dict = json.loads(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

try:
    google_sheet_id = st.secrets["google_sheet_id"]
    sheet = client.open_by_key(google_sheet_id).sheet1
except KeyError:
    st.error("secrets.toml 파일에 'google_sheet_id'가 설정되어 있지 않습니다. 설정해주세요.")
    st.stop()
except Exception as e:
    st.error(f"Google Sheet 연결 중 오류 발생: {e}")
    st.exception(e)
    st.stop()
# --- 구글 인증 및 시트 연결 끝 ---

# --- 데이터 로드 및 캐싱 함수 ---
@st.cache_data(ttl=60) # 60초(1분)마다 캐시 갱신
def load_data_from_sheet():
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            df.columns = ['이름', '등록시간']
            # '등록시간' 컬럼을 datetime 객체로 변환
            df['등록시간'] = pd.to_datetime(df['등록시간'])
            return df
        return pd.DataFrame(columns=['이름', '등록시간']) # 데이터 없으면 빈 DataFrame 반환
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류 발생: {e}")
        st.exception(e)
        return pd.DataFrame(columns=['이름', '등록시간'])

# --- 데이터 삭제 함수 ---
def delete_data_from_sheet(row_index):
    try:
        # gspread는 1-based index를 사용합니다.
        # df.index는 0-based이므로 1을 더해야 합니다.
        sheet.delete_rows(row_index + 1)
        st.success(f"{row_index + 1}번째 행의 데이터가 삭제되었습니다.") # 사용자에게 1-based 인덱스 표시
        st.cache_data.clear() # 캐시 무효화
        st.rerun() # 페이지 새로고침
    except Exception as e:
        st.error(f"데이터 삭제 중 오류 발생: {e}")
        st.exception(e)

# --- 전체 기록 초기화 함수 ---
def clear_all_data_from_sheet():
    try:
        # 시트의 모든 내용을 지웁니다. (첫 행은 헤더로 유지)
        # get_all_values()를 사용하여 현재 시트의 크기를 파악하고,
        # 첫 행을 제외한 나머지 행을 지웁니다.
        all_values = sheet.get_all_values()
        if len(all_values) > 1: # 헤더 행(1행)만 있고 데이터가 없는 경우가 아니면
            sheet.delete_rows(2, len(all_values)) # 2행부터 마지막 행까지 삭제
            st.success("모든 기록이 성공적으로 초기화되었습니다.")
            st.cache_data.clear() # 캐시 무효화
            st.rerun() # 페이지 새로고침
        else:
            st.info("시트에 삭제할 기록이 없습니다.")
    except Exception as e:
        st.error(f"전체 기록 초기화 중 오류 발생: {e}")
        st.exception(e)

# --- 페이지 설정 ---
st.set_page_config(page_title="우유 다 먹었어요 & 관리자", page_icon="🥛", layout="wide")

# --- 앱 메인 페이지와 관리자 페이지 전환 ---
# 쿼리 파라미터를 사용하여 페이지를 전환합니다.
query_params = st.query_params

if "page" in query_params and query_params["page"] == "admin":
    # 관리자 페이지
    st.sidebar.title("관리자 로그인")
    admin_entered_password = st.sidebar.text_input("비밀번호를 입력하세요", type="password")
    admin_login_button = st.sidebar.button("로그인")

    if st.session_state.get("logged_in_as_admin", False):
        st.sidebar.success("관리자 로그인 성공!")
        is_admin_logged_in = True
    elif admin_login_button:
        if admin_entered_password == st.secrets["admin_password"]:
            st.session_state["logged_in_as_admin"] = True
            st.sidebar.success("관리자 로그인 성공!")
            is_admin_logged_in = True
            st.rerun() # 로그인 상태 반영을 위해 새로고침
        else:
            st.sidebar.error("비밀번호가 틀렸습니다.")
            is_admin_logged_in = False
    else:
        is_admin_logged_in = False

    if is_admin_logged_in:
        st.title("👨‍🏫 선생님 관리자 페이지")
        st.markdown("---")

        st.subheader("모든 우유 마시기 기록")

        df_all_data = load_data_from_sheet()

        if not df_all_data.empty:
            # 인덱스를 열로 표시할 때, 1-based 인덱스를 보여주기 위해 +1
            st.dataframe(df_all_data.reset_index().rename(columns={'index': '인덱스'}), use_container_width=True)
            st.markdown("---")

            st.subheader("기록 삭제")
            st.warning("경고: 삭제된 데이터는 복구할 수 없습니다!")

            col1, col2 = st.columns(2) # 삭제 버튼들을 위한 컬럼 분리

            with col1:
                row_to_delete = st.number_input(
                    "삭제할 행의 '인덱스'를 입력하세요 (표의 첫 번째 열)",
                    min_value=0, # DataFrame 인덱스는 0부터 시작
                    max_value=len(df_all_data) - 1 if len(df_all_data) > 0 else 0,
                    value=0,
                    step=1,
                    key="single_delete_input" # 고유 키 추가
                )
                delete_button = st.button("선택한 기록 삭제", key="single_delete_button")

                if delete_button:
                    # gspread의 delete_rows는 1-based 인덱스를 사용하므로 +1
                    delete_data_from_sheet(row_to_delete)
            
            with col2:
                st.subheader("전체 기록 초기화")
                st.warning("경고: 이 버튼을 누르면 모든 기록이 영구적으로 삭제됩니다!")
                confirm_clear = st.checkbox("정말로 모든 기록을 삭제하시겠습니까?", key="confirm_clear_checkbox")
                clear_all_button = st.button("전체 기록 초기화", disabled=not confirm_clear, key="clear_all_button")

                if clear_all_button and confirm_clear:
                    clear_all_data_from_sheet()
        else:
            st.info("아직 등록된 기록이 없습니다.")

        st.markdown("---")
        if st.sidebar.button("관리자 로그아웃"):
            if "logged_in_as_admin" in st.session_state:
                del st.session_state["logged_in_as_admin"]
            st.rerun() # 로그아웃 후 새로고침

    else:
        st.warning("선생님 관리자 페이지는 비밀번호를 입력해야 접근할 수 있습니다.")
        st.info("메인 페이지로 돌아가려면 '메인 페이지' 버튼을 클릭하세요.")
        if st.button("메인 페이지"):
            st.query_params["page"] = "main"
            st.rerun()


else:
    # 학생용 메인 페이지 (기존 코드 대부분)
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
                try:
                    sheet.append_row([name.strip(), now])
                    st.success(f"🥛 {name} 님, 잘했어요! 우유 다 마신 걸 기록했어요.")
                    st.cache_data.clear() # 새 데이터 추가 시 캐시 무효화
                except Exception as e:
                    st.error(f"데이터 기록 중 오류 발생: {e}")
                    st.exception(e)

    st.markdown("---")
    st.subheader("📋 우유 다 마신 친구들")

    # 대시보드 표시
    df_dashboard = load_data_from_sheet() # 캐싱된 함수 사용
    if not df_dashboard.empty:
        # 대시보드용으로 인덱스 조정 (사용자에게 1-based 인덱스처럼 보이게)
        st.dataframe(df_dashboard.reset_index().rename(columns={'index': '인덱스'}), use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 우유 마시기 현황 시각화")

        # 1. 학생별 우유 마시기 횟수
        st.markdown("#### 🧑‍🎓 학생별 우유 마시기 횟수")
        student_counts = df_dashboard['이름'].value_counts().reset_index()
        student_counts.columns = ['이름', '횟수']
        fig_student_counts = px.bar(
            student_counts,
            x='이름',
            y='횟수',
            title='학생별 우유 마시기 횟수',
            labels={'이름': '학생 이름', '횟수': '우유 마신 횟수'},
            color='횟수', # 횟수에 따라 색상 변화
            color_continuous_scale=px.colors.sequential.Viridis # 색상 스케일
        )
        fig_student_counts.update_layout(xaxis_title="학생 이름", yaxis_title="우유 마신 횟수")
        st.plotly_chart(fig_student_counts, use_container_width=True)

        # 2. 시간대별 우유 마시기 현황
        st.markdown("#### ⏰ 시간대별 우유 마시기 현황")
        # '등록시간'에서 시간(hour)만 추출
        df_dashboard['시간'] = df_dashboard['등록시간'].dt.hour
        hourly_counts = df_dashboard['시간'].value_counts().sort_index().reset_index()
        hourly_counts.columns = ['시간', '횟수']
        fig_hourly_counts = px.bar(
            hourly_counts,
            x='시간',
            y='횟수',
            title='시간대별 우유 마시기 현황',
            labels={'시간': '시간 (시)', '횟수': '우유 마신 횟수'},
            color='횟수',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig_hourly_counts.update_layout(xaxis_title="시간 (0-23시)", yaxis_title="우유 마신 횟수", xaxis_tickangle=-45)
        st.plotly_chart(fig_hourly_counts, use_container_width=True)

    else:
        st.info("아직 등록된 친구가 없어요.")

    st.markdown("---")
    st.info("선생님은 사이드바의 '관리자 페이지' 버튼을 클릭하세요.")

# --- 사이드바 네비게이션 ---
st.sidebar.header("페이지 이동")
if "page" in query_params and query_params["page"] == "admin":
    if st.sidebar.button("메인 페이지"):
        st.query_params["page"] = "main"
        st.rerun()
else:
    if st.sidebar.button("관리자 페이지"):
        st.query_params["page"] = "admin"
        st.rerun()
