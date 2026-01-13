import streamlit as st
import questions_manager
import importlib

# Force reload to ensure latest data
importlib.reload(questions_manager)

st.set_page_config(page_title="이메일 수신인 관리", page_icon="📧")

# Hide native navigation
# Hide native navigation & Set Sidebar Width
st.markdown("""
<style>
/* Desktop Sidebar Width */
@media (min-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 500px;
        max-width: 800px;
    }
}
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    if st.button("홈 (Main)", use_container_width=True):
        st.session_state.viewing_history = False
        st.session_state.selected_hist_index = None
        st.switch_page("app.py")
        
    st.divider()
    
    st.markdown("#### ⚙️ 설정 (Settings)")
        
    if st.button("질문자 페르소나 설정", use_container_width=True):
        st.switch_page("pages/02_Personas.py")

    if st.button("질문 설정", use_container_width=True):
        st.switch_page("pages/04_Question_Settings.py")
        
    if st.button("이메일 수신인 설정", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Email_Recipients.py")

    if st.button("경쟁사 키워드 관리", use_container_width=True):
        st.switch_page("pages/03_Competitor_Settings.py")
        
    st.divider()

st.title("📧 이메일 수신인 관리")
st.caption("수신인 등록 완료 후 '홈 (main)'으로 돌아가주세요.")

# Add form
with st.form("add_recipient_form", clear_on_submit=True):
    col1, col2 = st.columns([0.4, 0.6])
    new_name = col1.text_input("이름")
    new_email = col2.text_input("이메일")
    submitted = st.form_submit_button("수신인 추가")
    
    if submitted:
        if new_name and new_email:
            if questions_manager.add_recipient(new_name, new_email):
                st.success(f"{new_name} ({new_email}) 추가 완료!")
                st.rerun()
            else:
                st.error("이미 존재하는 이메일입니다.")
        else:
            st.warning("이름과 이메일을 모두 입력해주세요.")

# List & Delete
st.divider()
recipients = questions_manager.load_recipients()
if recipients:
    st.write(f"총 {len(recipients)}명의 수신인이 등록되어 있습니다.")
    for i, r in enumerate(recipients):
        col_info, col_del = st.columns([0.85, 0.15])
        with col_info:
            if isinstance(r, dict):
                st.text(f"{r['name']} ({r['email']})")
            else:
                st.text(f"{r}")
        
        with col_del:
            if st.button("삭제", key=f"del_rec_{i}"):
                questions_manager.delete_recipient(i)
                st.rerun()
else:
    st.info("등록된 수신인이 없습니다.")
