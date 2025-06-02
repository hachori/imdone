import streamlit as st
import pandas as pd
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(
    page_title="우리들의 할일 완료 대시보드",
    page_icon="✨",
    layout="wide"
)

# --- 세션 상태 초기화 (데이터 저장용) ---
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []

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
    if st.session_state.completed_tasks:
        df_completed = pd.DataFrame(st.session_state.completed_tasks)
        df_completed['완료 시간'] = df_completed['완료 시간'].dt.strftime('%Y-%m-%d %H:%M:%S') # 시간 포맷 변경
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
                st.session_state.completed_tasks.append({
                    "이름": student_name,
                    "완료 시간": completion_time
                })
                st.success(f"{student_name}님, 할일 완료 기록이 저장되었습니다! 멋져요!")
                # 페이지 새로고침하여 대시보드 업데이트 (선택 사항)
                st.rerun() # 여기가 변경되었습니다.
            else:
                st.warning("이름을 입력해주세요!")
else:
    st.info("아직 남은 할일이 있어요! 모두 완료하면 이름을 입력할 수 있어요.")

st.markdown("---")
st.caption("Made with ❤️ by Your Teacher")
