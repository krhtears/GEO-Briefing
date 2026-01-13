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
    st.markdown("#### ⚙️ 설정 (Settings)")
    if st.button("홈 (Main)", use_container_width=True):
        st.switch_page("app.py")
        
    if st.button("질문자 페르소나 설정", use_container_width=True, type="primary"):
        st.switch_page("pages/02_Personas.py")

    if st.button("질문 설정", use_container_width=True):
        st.switch_page("pages/04_Question_Settings.py")
        
    if st.button("이메일 수신인 설정", use_container_width=True):
        st.switch_page("pages/01_Email_Recipients.py")

    if st.button("경쟁사 키워드 관리", use_container_width=True):
        st.switch_page("pages/03_Competitor_Settings.py")
        
    st.divider()

st.title("🎭 사용자 페르소나 (질문자 특성) 관리")
st.caption("질문하는 사람(User)의 특성이나 상황을 설정합니다. AI는 이 정보를 바탕으로 맞춤형 답변을 제공합니다. 최대 5개까지 저장 가능합니다.")
st.caption("페르소나 등록, 체크 완료 후 '홈 (main)'으로 돌아가주세요.")

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
            # Check if this item is being edited
            is_editing = (st.session_state.get("edit_persona_index") == i)
            
            if is_editing:
                # --- Edit Mode ---
                with st.form(key=f"edit_persona_form_{i}"):
                    edited_name = st.text_input("페르소나 이름", value=p['name'])
                    edited_prompt = st.text_area("특성 설명", value=p['prompt'], height=150)
                    
                    col_save, col_cancel = st.columns(2)
                    if col_save.form_submit_button("저장 (Save)", type="primary", use_container_width=True):
                        # Update data
                        personas[i]['name'] = edited_name
                        personas[i]['prompt'] = edited_prompt
                        personas_manager.save_personas(personas)
                        
                        # Reset state
                        st.session_state.edit_persona_index = None
                        st.success("수정되었습니다.")
                        st.rerun()
                        
                    if col_cancel.form_submit_button("취소 (Cancel)", type="secondary", use_container_width=True):
                        st.session_state.edit_persona_index = None
                        st.rerun()
            else:
                # --- View Mode ---
                col_p_head, col_p_action = st.columns([0.8, 0.2])
                with col_p_head:
                    st.subheader(f"🎭 {p['name']}")
                
                with col_p_action:
                     if st.button("수정 (Edit)", key=f"edit_p_{i}", use_container_width=True):
                        st.session_state.edit_persona_index = i
                        st.rerun()
                     
                     if st.button("삭제 (Delete)", key=f"del_persona_{i}", type="secondary", use_container_width=True):
                        personas_manager.delete_persona(i)
                        # Handle edge case where deleted item was being edited
                        if st.session_state.get("edit_persona_index") == i:
                             st.session_state.edit_persona_index = None
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
