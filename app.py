import streamlit as st
import importlib
import email_sender
import questions_manager
import api_clients
import history_manager

# Force reload modules to pick up changes
importlib.reload(questions_manager)
importlib.reload(api_clients)
importlib.reload(email_sender)
importlib.reload(history_manager)

# Set page config
st.set_page_config(page_title="유초중사업본부 GEO Briefing", page_icon="🌤️", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 500px; /* Increase sidebar width */
        max-width: 800px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("유초중사업본부 GEO Briefing")

# Sidebar - Question Management
st.sidebar.header("📝 질문 편집하기")

# Add new question
new_question = st.sidebar.text_input("새로운 질문을 입력해주세요.")
if st.sidebar.button("질문 추가하기"):
    if new_question:
        if questions_manager.add_question(new_question):
            st.sidebar.success("질문 추가 완료!")
            st.rerun()
        else:
            st.sidebar.warning("질문이 이미 존재합니다.")
    else:
        st.sidebar.warning("질문을 입력해주세요.")

# List and Delete questions
st.sidebar.subheader("등록된 질문")
questions = questions_manager.load_questions()

for i, q in enumerate(questions):
    col1, col2 = st.sidebar.columns([0.85, 0.15])
    col1.write(f"**{i+1}.** {q}")
    if col2.button("🗑️", key=f"del_q_{i}"):
        questions_manager.delete_question(i)
        st.rerun()

st.sidebar.divider()

# Sidebar - Recipient Management
st.sidebar.header("📧 수신인 편집하기")

# Add new recipient
col_new_name, col_new_email = st.sidebar.columns([0.4, 0.6])
new_name = col_new_name.text_input("이름")
new_email = col_new_email.text_input("이메일")

if st.sidebar.button("수신인 추가하기"):
    if new_name and new_email:
        if "@" not in new_email:
             st.sidebar.warning("이메일 형식이 올바르지 않습니다.")
        elif questions_manager.add_recipient(new_name, new_email):
            st.sidebar.success("수신인 추가 완료!")
            st.rerun()
        else:
            st.sidebar.warning("수신인이 이미 존재합니다.")
    else:
        st.sidebar.warning("이름과 이메일을 모두 입력해주세요.")

# List and Delete recipients
st.sidebar.subheader("메일 수신인 리스트")
recipients = questions_manager.load_recipients()

for i, r in enumerate(recipients):
    col1, col2 = st.sidebar.columns([0.85, 0.15])
    col1.text(f"- {r['name']} ({r['email']})")
    if col2.button("🗑️", key=f"del_r_{i}"):
        questions_manager.delete_recipient(i)
        st.rerun()


# Main Area
st.subheader("질문과 메일 수신인을 확인하고 briefing 시작하기를 눌러주세요.")

# --- History Section ---
st.markdown("### 🕒 Recent Briefings")
history_items = history_manager.load_history()

# Create a container for history buttons to layout horizontally or wrapped
if history_items:
    cols = st.columns(len(history_items))
    for i, item in enumerate(history_items):
        # Button label: Timestamp
        if cols[i].button(f"{item['timestamp']}\n(View)", key=f"hist_{i}"):
             st.session_state.briefing_results = item['data']
             st.session_state.show_confirm_dialog = False # Don't show confirm for history view
             st.rerun()
    st.divider()

# Initialize session state for results if not exists
if "briefing_results" not in st.session_state:
    st.session_state.briefing_results = []

col_btn_run, col_btn_email = st.columns([0.2, 0.8])

with col_btn_run:
    run_clicked = st.button("🚀 Briefing 시작하기", type="primary")

with col_btn_email:
    email_clicked = st.button("📧 결과 이메일로 보내기")

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
                    gemini_response = api_clients.ask_gemini(question)
                    gpt_response = api_clients.ask_gpt(question)
                
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
            st.warning("📢 **해당 결과를 메일 수신인에게 지금 발송하시겠습니까?**")
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
    
    if not st.session_state.briefing_results:
        st.warning("⚠️ Please generate the briefing first!")
    elif not recipients:
        st.warning("⚠️ No recipients configured.")
    else:
        with st.spinner("Sending email..."):
            import importlib
            importlib.reload(email_sender)
            email_status = email_sender.send_briefing_email(recipients, st.session_state.briefing_results)
            
            if email_status is True:
                st.success(f"Email sent to {len(recipients)} recipients!")
            else:
                st.error(f"Failed to send email: {email_status}")
