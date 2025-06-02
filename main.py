import streamlit as st
import pandas as pd
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(
    page_title="우리들의 할일 완료 대시보드",
    page_icon="✨",
    layout="wide"
)

# Google Sheets 연결 (secrets.toml에 설정된 정보 사용)
# spreadsheet 값은 secrets.toml에 설정된 스프레드시트 이름 또는 URL과 일치해야 합니다.
conn = st.connection("gsheets", type="spreadsheet") # "gsheets"는 secrets.toml의 [connections.gsheets]와 연결됩니다.

# --- 함수: Google Sheet에서 데이터 읽기 ---
@st.cache_data(ttl="10m") # 10분마다 캐시 갱신 (선택 사항)
def get_completed_tasks_from_gsheets():
    try:
        # worksheet_name은 시트의 실제 이름이어야 합니다 (예: "Sheet1")
        # 데이터프레임으로 가져옵니다.
        df = conn.read(worksheet="완료현황", usecols=list(range(2)), ttl=5) # 0, 1번째 열만 가져옴
        return df.to_dict('records') # 딕셔너리 리스트 형태로 반환
    except Exception as e:
        st.error(f"Google Sheet에서 데이터를 읽어오는 중 오류 발생: {e}")
        return []

# --- 함수: Google Sheet에 데이터 추가 ---
def add_task_to_gsheets(name, completion_time):
    new_data = pd.DataFrame([{"이름": name, "완료 시간": completion_time.strftime('%Y-%m-%d %H:%M:%S')}])
    try:
        conn.write(worksheet="완료현황", data=new_data, ttl=0) # ttl=0으로 설정하여 즉시 업데이트
        st.success("Google Sheet에 성공적으로 기록되었습니다!")
    except Exception as e:
        st.error(f"Google Sheet에 데이터를 쓰는 중 오류 발생: {e}")

# --- 세션 상태 초기화 (데이터 저장용) ---
# 이제 session_state는 Google Sheets 데이터를 캐시하는 용도로 사용될 수 있습니다.
# 실제 데이터는 Google Sheets에 있습니다.
if 'completed_tasks_data' not in st.session_state:
    st.session_state.completed_tasks_data = get_completed_tasks_from_gsheets()

# --- 할일 목록 정의 ---
tasks = [
    "오늘의 학습지 풀기",
    "책 10분 읽기",
    "방 정리하기",
    "줄넘기 50번 하기",
    "부모님께 사랑한다고 말하기"
]

# --- 사이드바 (대시보드) ---
with st.sidebar:
    st.header("✨ 완료 현황 대시보드 ✨")
    # Google Sheet에서 최신 데이터 가져오기
    current_completed_data = get_completed_tasks_from_gsheets()
    if current_completed_data:
        df_completed = pd.DataFrame(current_completed_data)
        st.dataframe(df_completed, use_container_width=True, hide_index=True)
    else:
        st.info("아직 완료된 할일이 없어요!")

# --- 메인 페이지 ---
st.title("🚀 우리들의 할일 완료! 🚀")
st.markdown("---")

st.subheader("오늘 할일을 모두 완료했나요?")

# 할일 목록 체크박스
task_completion_status = {}
for i, task in enumerate(tasks):
    task_completion_status[task] = st.checkbox(f"✅ {task}", key=f"task_{i}")

# 모든 할일이 완료되었는지 확인
all_tasks_completed = all(task_completion_status.values())

st.markdown("---")

if all_tasks_completed:
    st.balloons()
    st.success("🎉 모든 할일을 완료했어요! 정말 대단해요! 🎉")

    with st.form("completion_form"):
        st.subheader("😊 이름을 알려주세요 😊")
        student_name = st.text_input("이름을 입력해주세요", max_chars=20)
        submitted = st.form_submit_button("완료했어요!")

        if submitted:
            if student_name:
                completion_time = datetime.now()
                # Google Sheet에 데이터 추가
                add_task_to_gsheets(student_name, completion_time)
                # 세션 상태도 업데이트 (즉시 반영을 위함)
                st.session_state.completed_tasks_data.append({
                    "이름": student_name,
                    "완료 시간": completion_time.strftime('%Y-%m-%d %H:%M:%S')
                })
                st.rerun() # 페이지 새로고침하여 대시보드 업데이트
            else:
                st.warning("이름을 입력해주세요!")
else:
    st.info("아직 남은 할일이 있어요! 모두 완료하면 이름을 입력할 수 있어요.")

st.markdown("---")
st.caption("Made with ❤️ by Your Teacher")
