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
            col1, col2 = st.columns([0.85, 0.15])
            
            with col1:
                st.subheader(f"🏷️ {comp['name']}")
                
                # Keywords display/edit
                current_keywords_str = ", ".join(comp['keywords'])
                new_keywords_str = st.text_area(f"키워드 (쉼표 구분) - {comp['name']}", value=current_keywords_str, key=f"kw_{i}")
                
                if new_keywords_str != current_keywords_str:
                    if st.button("키워드 수정 저장", key=f"save_{i}"):
                        updated_keywords = [k.strip() for k in new_keywords_str.split(",") if k.strip()]
                        competitors[i]['keywords'] = updated_keywords
                        stats_manager.save_competitors(competitors)
                        st.success("키워드가 수정되었습니다.")
                        st.rerun()
            
            with col2:
                st.write("") # Spacer
                st.write("") 
                if st.button("삭제", key=f"del_{i}", type="secondary"):
                    competitors.pop(i)
                    stats_manager.save_competitors(competitors)
                    st.success("삭제되었습니다.")
                    st.rerun()
