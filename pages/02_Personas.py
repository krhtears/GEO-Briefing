import streamlit as st
import personas_manager
import importlib

# Force reload to ensure latest data
importlib.reload(personas_manager)

st.set_page_config(page_title="사용자 페르소나 설정", page_icon="🎭")

# Hide native navigation
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    if st.button("홈 (Main)", use_container_width=True):
        st.switch_page("app.py")
        
    if st.button("이메일 수신인 설정", use_container_width=True):
        st.switch_page("pages/01_Email_Recipients.py")
        
    if st.button("사용자 페르소나 설정", use_container_width=True, type="primary"):
        st.switch_page("pages/02_Personas.py")
        
    st.divider()

st.title("🎭 사용자 페르소나 (질문자 특성) 관리")
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
    st.markdown("### 📋 등록된 페르소나 목록")
    st.caption("체크박스를 선택하면 해당 페르소나가 브리핑 생성 시 반영됩니다.")
    
    for i, p in enumerate(personas):
        with st.container(border=True):
            col_p_head, col_p_del = st.columns([0.85, 0.15])
            col_p_head.subheader(f"🎭 {p['name']}")
            
            if col_p_del.button("삭제", key=f"del_persona_{i}"):
                personas_manager.delete_persona(i)
                st.rerun()
            
            # Content without horizontal scroll (Wrapped)
            st.info(p['prompt'], icon="📝")
            
            # Active Checkbox
            is_active = p.get('active', False)
            if st.checkbox("이 페르소나 적용하기", value=is_active, key=f"active_{i}"):
                if not is_active:
                    personas_manager.toggle_persona_active(i, True)
                    st.rerun()
            else:
                if is_active:
                    personas_manager.toggle_persona_active(i, False)
                    st.rerun()
else:
    st.info("등록된 페르소나가 없습니다.")
