import streamlit as st
import stats_manager

# --- Clean Navigation ---
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("홈 (Main)", use_container_width=True):
        st.switch_page("app.py")
    if st.button("이메일 수신인 설정", use_container_width=True):
        st.switch_page("pages/01_Email_Recipients.py")
    if st.button("질문자 페르소나 설정", use_container_width=True):
        st.switch_page("pages/02_Personas.py")
    if st.button("경쟁사 키워드 관리", use_container_width=True, type="primary"):
        pass # Already on this page

    if st.button("질문 설정 (Questions)", use_container_width=True):
        st.switch_page("pages/04_Question_Settings.py")
    
    st.divider()

st.title("🏢 경쟁사 및 키워드 관리")
st.caption("우리 회사와 경쟁하는 브랜드, 그리고 해당 브랜드를 감지할 키워드를 등록합니다. 등록된 키워드가 브리핑에 포함되면 통계에 집계됩니다.")
st.caption("설정 완료 후 '홈 (main)'으로 돌아가주세요.")

# Load Competitors
competitors = stats_manager.load_competitors()

# Add New Competitor Form
with st.expander("🆕 새로운 경쟁사 추가하기", expanded=False):
    with st.form("add_competitor_form", clear_on_submit=True):
        new_name = st.text_input("경쟁사 브랜드명 (예: 메가스터디교육)")
        new_keywords = st.text_input("감지 키워드 (쉼표로 구분, 예: 엠베스트, 엘리하이)")
        
        submitted = st.form_submit_button("추가")
        if submitted:
            if new_name and new_keywords:
                # Parse keywords
                keywords_list = [k.strip() for k in new_keywords.split(",") if k.strip()]
                
                # Check duplicate name
                if any(c['name'] == new_name for c in competitors):
                    st.error("이미 존재하는 브랜드명입니다.")
                else:
                    competitors.append({
                        "name": new_name,
                        "keywords": keywords_list
                    })
                    stats_manager.save_competitors(competitors)
                    st.success(f"{new_name} 추가 완료!")
                    st.rerun()
            else:
                st.warning("브랜드명과 키워드를 모두 입력해주세요.")

st.divider()

# List Competitors
st.markdown("### 📋 등록된 경쟁사 목록")

if not competitors:
    st.info("등록된 경쟁사가 없습니다.")
else:
    for i, comp in enumerate(competitors):
        with st.container(border=True):
            # Check if this item is being edited
            is_editing = (st.session_state.get("edit_target_index") == i)
            
            if is_editing:
                # --- Edit Mode ---
                with st.form(key=f"edit_form_{i}"):
                    edited_name = st.text_input("브랜드명", value=comp['name'])
                    edited_keywords = st.text_area("키워드 (쉼표로 구분)", value=", ".join(comp['keywords']))
                    
                    col_save, col_cancel = st.columns(2)
                    if col_save.form_submit_button("저장 (Save)", type="primary", use_container_width=True):
                        # Update data
                        competitors[i]['name'] = edited_name
                        competitors[i]['keywords'] = [k.strip() for k in edited_keywords.split(",") if k.strip()]
                        stats_manager.save_competitors(competitors)
                        
                        # Reset state
                        st.session_state.edit_target_index = None
                        st.success("수정되었습니다.")
                        st.rerun()
                        
                    if col_cancel.form_submit_button("취소 (Cancel)", type="secondary", use_container_width=True):
                        st.session_state.edit_target_index = None
                        st.rerun()
            
            else:
                # --- View Mode ---
                col1, col2 = st.columns([0.8, 0.2])
                
                with col1:
                    st.subheader(f"🏷️ {comp['name']}")
                    st.write(f"**키워드:** {', '.join(comp['keywords'])}")
                
                with col2:
                    if st.button("수정 (Edit)", key=f"edit_btn_{i}", use_container_width=True):
                        st.session_state.edit_target_index = i
                        st.rerun()
                        
                    if st.button("삭제 (Delete)", key=f"del_btn_{i}", type="secondary", use_container_width=True):
                        competitors.pop(i)
                        stats_manager.save_competitors(competitors)
                        # Identify logic if we deleted the one being edited (edge case), reset state
                        if st.session_state.get("edit_target_index") == i:
                            st.session_state.edit_target_index = None
                        st.success("삭제되었습니다.")
                        st.rerun()
