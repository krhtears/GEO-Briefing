import streamlit as st
import questions_manager
import personas_manager
import importlib

# Force reload to ensure latest data
importlib.reload(questions_manager)
importlib.reload(personas_manager)

st.set_page_config(page_title="설정 (Configuration)", page_icon="⚙️")

st.title("⚙️ 설정 (Configuration)")
st.info("이메일 수신인과 페르소나를 관리하는 페이지입니다.")

tab_recipients, tab_personas = st.tabs(["📧 수신인 관리", "🎭 페르소나 관리"])

# --- Tab 1: Recipients ---
with tab_recipients:
    st.header("📧 이메일 수신인 관리")
    
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
                # Handle legacy string format just in case, though app.py handles migration usually
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

# --- Tab 2: Personas ---
with tab_personas:
    st.header("🎭 사용자 페르소나 (질문자 특성) 관리")
    st.caption("질문하는 사람(User)의 특성이나 상황을 설정합니다. AI는 이 정보를 바탕으로 맞춤형 답변을 제공합니다. 최대 5개까지 저장 가능합니다.")
    
    # Load Personas
    personas = personas_manager.load_personas()
    
    # Add form
    with st.expander("➕ 새 페르소나 추가하기", expanded=False):
        if len(personas) >= 5:
            st.warning("⚠️ 페르소나는 최대 5개까지만 저장할 수 있습니다. 기존 페르소나를 삭제 후 추가해주세요.")
        else:
            with st.form("add_persona_form", clear_on_submit=True):
                p_name = st.text_input("페르소나 이름 (예: 초등 학부모, 학원 강사)")
                p_prompt = st.text_area("특성 설명 (AI가 참고할 사용자 정보)", height=150, 
                                      placeholder="저는 초등학교 3학년 자녀를 둔 학부모입니다. 교육 용어를 잘 모르니 쉽게 설명해주세요.")
                p_submitted = st.form_submit_button("저장하기")
                
                if p_submitted:
                    if p_name and p_prompt:
                        if personas_manager.add_persona(p_name, p_prompt):
                            st.success(f"'{p_name}' 페르소나 저장 완료!")
                            st.rerun()
                        else:
                            st.error("저장 실패 (최대 개수 초과 등)")
                    else:
                        st.warning("이름과 프롬프트를 모두 입력해주세요.")

    # List & Delete
    st.divider()
    if personas:
        for i, p in enumerate(personas):
            with st.container(border=True):
                col_p_head, col_p_del = st.columns([0.85, 0.15])
                col_p_head.subheader(f"🎭 {p['name']}")
                if col_p_del.button("삭제", key=f"del_persona_{i}"):
                    personas_manager.delete_persona(i)
                    st.rerun()
                
                st.code(p['prompt'], language=None)
    else:
        st.info("등록된 페르소나가 없습니다.")
