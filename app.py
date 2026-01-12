import streamlit as st
import importlib
import email_sender
import questions_manager
import api_clients
import history_manager
import stats_manager
import personas_manager

# Force reload modules to pick up changes
importlib.reload(questions_manager)
importlib.reload(api_clients)
importlib.reload(email_sender)
importlib.reload(history_manager)
importlib.reload(stats_manager)
importlib.reload(personas_manager)

# Set page config
st.set_page_config(page_title="유초중사업본부 GEO Analytics", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    /* Desktop Sidebar Width */
    @media (min-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 500px;
            max-width: 800px;
        }
    }
    /* Hide the native Streamlit navigation widget */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    # /* Responsive Tables */
    table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("유초중사업본부 GEO Analytics")

# Sidebar Logic
with st.sidebar:
    # Custom Navigation
    if st.button("홈 (Main)", use_container_width=True, type="primary"):
        st.switch_page("app.py")
        
    if st.button("이메일 수신인 설정", use_container_width=True):
        st.switch_page("pages/01_Email_Recipients.py")
        
    if st.button("질문자 페르소나 설정", use_container_width=True):
        st.switch_page("pages/02_Personas.py")
        
    st.divider()

if st.session_state.get("viewing_history", False):
    st.sidebar.header("📜 지난 브리핑 질문")
    st.sidebar.info("뷰어 모드입니다. 편집하려면 아래 버튼을 눌러주세요.")
    
    if st.sidebar.button("🔙 브리핑 입력 모드 돌아가기"):
        # Restore latest questions if available
        history_items = history_manager.load_history()
        if history_items:
            latest_questions = [item['question'] for item in history_items[0]['data']]
            questions_manager.set_questions(latest_questions)
            
        st.session_state.viewing_history = False
        st.rerun()
        
    # Extract questions from the current result set
    if "briefing_results" in st.session_state and st.session_state.briefing_results:
        # Assuming current_questions matches the order in results
        # Or safely extracting from the first result item if we stored it?
        # Actually briefing_results is a list of dicts: [{'question': '...', ...}]
        current_questions = [item['question'] for item in st.session_state.briefing_results]
        
        for i, q in enumerate(current_questions):
             st.sidebar.write(f"**{i+1}.** {q}")
        
        # When viewing history, we use these questions for context, but we don't run them.
        questions = current_questions
    else:
        st.sidebar.warning("No history loaded.")
        questions = []

else:
    # Live Mode - Edit Questions
    st.sidebar.header("질문 편집하기")
    
    # Add new question
    with st.sidebar.form(key="question_form", clear_on_submit=True):
        new_question = st.text_input("새로운 질문을 입력해주세요.")
        submit_question = st.form_submit_button("질문 추가하기")

        if submit_question:
            if new_question:
                if questions_manager.add_question(new_question):
                    st.sidebar.success("질문 추가 완료!")
                    st.rerun()
                else:
                    st.sidebar.warning("질문이 이미 존재합니다.")
            else:
                st.sidebar.warning("질문을 입력해주세요.")

    # List and Delete questions
    # List and Delete questions
    st.sidebar.markdown("### <span style='color: #666666;'>등록된 질문</span>", unsafe_allow_html=True)
    questions = questions_manager.load_questions()

    for i, q in enumerate(questions):
        col1, col2 = st.sidebar.columns([0.85, 0.15])
        col1.markdown(f"<span style='color: #666666;'>**{i+1}.** {q}</span>", unsafe_allow_html=True)
        if col2.button("🗑️", key=f"del_q_{i}"):
            questions_manager.delete_question(i)
            st.rerun()

st.sidebar.divider()

# --- Persona Status ---
st.sidebar.header("질문자 페르소나")

# Load active personas
all_personas = personas_manager.load_personas() # [{'name':..., 'active':...}]
active_personas_list = [p for p in all_personas if p.get('active', False)]

if active_personas_list:
    st.sidebar.success(f"총 {len(active_personas_list)}개의 질문자 페르소나가 적용됩니다.")
    for p in active_personas_list:
        st.sidebar.text(f"✅ {p['name']}")
    
    # Get prompts for API
    selected_persona_prompts = [p['prompt'] for p in active_personas_list]

else:
    st.sidebar.info("적용된 페르소나가 없습니다.\n'질문자 페르소나 설정' 메뉴에서 선택해주세요.")
    selected_persona_prompts = []


# Main Area
st.markdown("##### (1) 질문, (2) 질문자 페르소나, (3) 메일 수신인을 확인하고 'briefing 시작하기' 버튼을 눌러주세요.")

# --- History Section ---
st.markdown("### Recent Briefings (최근 7개)")
history_items = history_manager.load_history()

# Create a container for history buttons to layout horizontally or wrapped
if history_items:
    cols = st.columns(len(history_items))
    for i, item in enumerate(history_items):
        # Button label: Timestamp
        if cols[i].button(f"{item['timestamp']}\n(View)", key=f"hist_{i}"):
             st.session_state.briefing_results = item['data']
             st.session_state.show_confirm_dialog = False # Don't show confirm for history view
             st.session_state.viewing_history = True # Enable History View Mode
             st.rerun()
    st.divider()

# Initialize session state for results if not exists
if "briefing_results" not in st.session_state:
    st.session_state.briefing_results = []

col_btn_run, col_btn_email = st.columns([0.2, 0.8])

with col_btn_run:
    run_clicked = st.button("Briefing 시작하기", type="primary")
    if run_clicked:
        st.session_state.viewing_history = False # Reset to Live Mode on Run

with col_btn_email:
    email_clicked = st.button("결과 이메일로 보내기")

if run_clicked:
    if not questions:
        st.warning("No questions configured. Please add some in the sidebar.")
    else:
        # Check for API Keys
        import api_keys
        if "PASTE" in api_keys.GEMINI_API_KEY or "PASTE" in api_keys.OPENAI_API_KEY:
             st.error("⚠️ Please update `api_keys.py` within actual API keys.")
        else:
            progress_bar = st.progress(0)
            results_data = []
            
            # Clear previous results
            st.session_state.briefing_results = []
            
            for index, question in enumerate(questions):
                # We can't use st.markdown direct output here nicely if we want to redraw from state later,
                # but for the "live" feel we can write to a placeholder or just let it render, 
                # then re-render from state on next pass? 
                # Actually, simpler to just render as we go, and ONLY store data for Email.
                # BUT, if user clicks Email, page reruns, run_clicked is False.
                # So we MUST render solely from session_state data if we want persistence.
                pass
            
            # Streaming generation logic with session state storage
            stats_placeholder = st.empty()
            
            for index, question in enumerate(questions):
                # Placeholder for streaming UI could be complex to mix with final state rendering.
                # Let's do: Generate ALL data first (with spinner), then store, then render.
                # OR: Render incrementally and append to state.
                
                with st.spinner(f"Analyzing Q{index+1}/{len(questions)}: {question}"):
                    # Pass the active prompts loaded from sidebar logic above
                    gemini_response = api_clients.ask_gemini(question, persona_prompts=selected_persona_prompts)
                    gpt_response = api_clients.ask_gpt(question, persona_prompts=selected_persona_prompts)
                
                results_data.append({
                    "question": question,
                    "gemini": gemini_response,
                    "gpt": gpt_response
                })
                progress_bar.progress((index + 1) / len(questions))
            
            st.session_state.briefing_results = results_data
            
            # Save to history
            history_manager.save_to_history(results_data)
            
            st.session_state.show_confirm_dialog = True  # Trigger confirmation
            st.rerun() 

# Render Results from Session State
if st.session_state.briefing_results:
    # Confirmation Dialog Area
    if st.session_state.get("show_confirm_dialog", False):
        with st.container(border=True):
            st.warning("**해당 결과를 메일 수신인에게 지금 발송하시겠습니까?**")
            col_conf_yes, col_conf_no = st.columns(2)
            
            with col_conf_yes:
                if st.button("예 (Yes)", key="confirm_yes", use_container_width=True):
                     st.session_state.trigger_email_send = True
                     st.session_state.show_confirm_dialog = False # Close dialog
                     st.rerun()
            
            with col_conf_no:
                if st.button("아니오 (No)", key="confirm_no", use_container_width=True):
                     st.session_state.show_confirm_dialog = False
                     st.rerun()

    # Calculate Stats
    stats = stats_manager.calculate_stats(st.session_state.briefing_results)
    
    # Display Stats Table (custom HTML to match look)
    st.markdown("### 📊 브랜드, 관련 키워드 언급 횟수")
    
    # Create rows for HTML table
    header_html = "".join([f"<th style='background-color: #E2EFDA; border: 1px solid black; padding: 5px; text-align: center;'>{brand}</th>" for brand in stats.keys()])
    count_html = "".join([f"<td style='border: 1px solid black; padding: 5px; text-align: center;'>{count}</td>" for count in stats.values()])
    
    st.markdown(f"""
    <table style='width: 100%; border-collapse: collapse; border: 1px solid black;'>
        <tr>
            <th style='background-color: #E2EFDA; border: 1px solid black; padding: 5px; text-align: center; width: 100px;'>구분</th>
            {header_html}
        </tr>
        <tr>
            <td style='border: 1px solid black; padding: 5px; text-align: center; font-weight: bold;'>언급횟수</td>
            {count_html}
        </tr>
    </table>
    <br>
    """, unsafe_allow_html=True)

    for item in st.session_state.briefing_results:
        st.markdown(f"### ❓ {item['question']}")
        col_gemini, col_gpt = st.columns(2)
        with col_gemini:
             st.markdown("#### ✨ Gemini")
             st.markdown(item['gemini'])
        with col_gpt:
             st.markdown("#### 🤖 GPT")
             st.markdown(item['gpt'])
        st.divider()
    
    if not st.session_state.get("show_confirm_dialog", False):
        st.success("✅ Briefing Ready")

# Email Logic (Handles button click or auto-confirm)
if email_clicked or st.session_state.get("trigger_email_send", False):
    # Reset trigger
    st.session_state.trigger_email_send = False
    
    # Load recipients for email sending (User manages them in Configuration page now)
    recipients = questions_manager.load_recipients()
    
    if not st.session_state.briefing_results:
        st.warning("⚠️ Please generate the briefing first!")
    elif not recipients:
        st.warning("⚠️ No recipients configured. Please add them in the Setting page.")
    else:
        with st.spinner("Sending email..."):
            import importlib
            importlib.reload(email_sender)
            
            # Re-calculate stats for email to be safe (or pass from session state)
            stats = stats_manager.calculate_stats(st.session_state.briefing_results)
            
            email_status = email_sender.send_briefing_email(recipients, st.session_state.briefing_results, stats)
            
            if email_status is True:
                st.success("이 메일이 발송되었습니다")
            else:
                st.error(f"Failed to send email: {email_status}")
