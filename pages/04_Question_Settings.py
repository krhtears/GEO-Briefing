
import streamlit as st
import questions_manager
import importlib

# Force reload module
importlib.reload(questions_manager)

st.set_page_config(page_title="질문 편집 설정", page_icon="📝")

# Hide native navigation
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("#### ⚙️ 설정 (Settings)")
    if st.button("홈 (Main)", use_container_width=True):
        st.switch_page("app.py")
        
    if st.button("질문자 페르소나 설정", use_container_width=True):
        st.switch_page("pages/02_Personas.py")

    if st.button("질문 설정", use_container_width=True, type="primary"):
        pass # Current page

    if st.button("이메일 수신인 설정", use_container_width=True):
        st.switch_page("pages/01_Email_Recipients.py")

    if st.button("경쟁사 키워드 관리", use_container_width=True):
        st.switch_page("pages/03_Competitor_Settings.py")
        
    st.divider()

st.title("📝 질문(Question) 편집 및 관리")
st.caption("AI 브리핑에 사용할 질문 리스트를 관리합니다. 질문은 위에서 아래 순서대로 실행됩니다.")
st.caption("설정 완료 후 '홈 (main)'으로 돌아가주세요.")

# Load Questions
questions = questions_manager.load_questions()

# Add New Question Form
with st.expander("➕ 새로운 질문 추가하기", expanded=False):
    with st.form("add_question_form", clear_on_submit=True):
        new_q_text = st.text_area("새로운 질문 내용", height=100)
        submitted = st.form_submit_button("질문 추가")
        
        if submitted:
            if new_q_text:
                if questions_manager.add_question(new_q_text):
                    st.success("질문 추가 완료!")
                    st.rerun()
                else:
                    st.warning("이미 존재하는 질문입니다.")
            else:
                st.warning("내용을 입력해주세요.")

st.divider()

if questions:
    st.markdown("### 📋 등록된 질문 목록")
    
    for i, q_text in enumerate(questions):
        with st.container(border=True):
            # Check if this item is being edited
            is_editing = (st.session_state.get("edit_question_index") == i)
            
            if is_editing:
                # --- Edit Mode ---
                with st.form(key=f"edit_q_form_{i}"):
                    # Note: Using text_area for multiline edits
                    edited_text = st.text_area(f"질문 {i+1} 수정", value=q_text, height=100)
                    
                    col_save, col_cancel = st.columns(2)
                    if col_save.form_submit_button("저장 (Save)", type="primary", use_container_width=True):
                        # Update data
                        questions[i] = edited_text
                        questions_manager.save_questions(questions)
                        
                        # Reset state
                        st.session_state.edit_question_index = None
                        st.success("수정되었습니다.")
                        st.rerun()
                        
                    if col_cancel.form_submit_button("취소 (Cancel)", type="secondary", use_container_width=True):
                        st.session_state.edit_question_index = None
                        st.rerun()
            else:
                # --- View Mode ---
                col_view, col_action = st.columns([0.85, 0.15])
                
                with col_view:
                    st.markdown(f"**{i+1}.** {q_text}")
                
                with col_action:
                    if st.button("수정", key=f"edit_q_{i}", use_container_width=True):
                        st.session_state.edit_question_index = i
                        st.rerun()
                        
                    if st.button("삭제", key=f"del_q_{i}", type="secondary", use_container_width=True):
                        questions_manager.delete_question(i)
                        
                        # Handle edge case where deleted item was being edited
                        if st.session_state.get("edit_question_index") == i:
                             st.session_state.edit_question_index = None
                        st.rerun()
else:
    st.info("등록된 질문이 없습니다.")
