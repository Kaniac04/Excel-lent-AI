import streamlit as st
import requests
import os
from dotenv import load_dotenv
from services.logger_service import get_logger

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
logger = get_logger("streamlit_ui")

st.set_page_config(page_title="Excel-lent AI Interview", layout="centered")
st.title("Excel-lent AI Interview Platform")

# session defaults
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history" not in st.session_state:
    st.session_state.history = []

if "is_waiting" not in st.session_state:
    st.session_state.is_waiting = False
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

def start_interview(name):
    logger.info(f"Attempting to start interview for: {name}")
    try:
        response = requests.post(f"{API_URL}/interview", json={"name": name}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            # use canonical role values for Streamlit chat
            st.session_state.history = [{"role": "assistant", "content": data.get("message", "")}]
            logger.info(f"Interview started. Session ID: {data['session_id']}")
        else:
            logger.error(f"Failed to start interview. Status: {response.status_code}, Response: {response.text}")
            st.error("Failed to start interview. Please try again.")
    except Exception as e:
        logger.exception("Exception during start_interview")
        st.error("Error connecting to API.")


# API processing at the top level, not in the form
if st.session_state.pending_user_input is not None and not st.session_state.is_waiting:
    user_input = st.session_state.pending_user_input
    st.session_state.is_waiting = True
    try:
        logger.info(f"Sending user response for session {st.session_state.session_id}: {user_input}")
        payload = {
            "session_id": st.session_state.session_id,
            "user_input": user_input
        }
        response = requests.post(f"{API_URL}/response", json=payload, stream=True, timeout=600)
        if response.status_code == 200:
            ai_message = ""
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk:
                    ai_message += chunk + "\n"
            st.session_state.history.append({"role": "user", "content": user_input})
            st.session_state.history.append({"role": "assistant", "content": ai_message.strip()})
            logger.info("AI response received and added to history.")
        else:
            logger.error(f"Failed to get response from AI. Status: {response.status_code}, Response: {response.text}")
            st.error("Failed to get response from AI.")
    except Exception as e:
        logger.exception("Exception during send_response")
        st.error("Error connecting to API.")
    finally:
        st.session_state.is_waiting = False
        st.session_state.pending_user_input = None
        st.session_state.clear_input = True
        st.rerun()

if st.session_state.session_id is None:
    with st.form("start_form"):
        name = st.text_input("Enter your name to begin the interview:", key="start_name")
        submitted = st.form_submit_button("Start Interview")
        if submitted and name.strip():
            logger.info("Start Interview button clicked.")
            start_interview(name.strip())
            st.rerun()
else:
    st.subheader("Interview Chat")
    # Display chat history as chat messages
    for msg in st.session_state.history:
        logger.debug(f"Chat message: {msg}")
        role = msg.get("role", "assistant")
        if role not in ("assistant", "user", "system"):
            role = "assistant"
        with st.chat_message(role):
            st.markdown(msg.get("content", ""))

    # Clear input before rendering the form if just submitted
    if "clear_input" in st.session_state and st.session_state.clear_input:
        st.session_state["response_input"] = ""
        st.session_state.clear_input = False

    with st.form("response_form"):
        user_input = st.text_area(
            "Your response:", key="response_input", disabled=st.session_state.is_waiting, height=100
        )
        # Only disable the button during API processing
        submitted = st.form_submit_button("Send", disabled=st.session_state.is_waiting)
        if submitted and user_input and user_input.strip():
            logger.info("Send button clicked in response form.")
            st.session_state.pending_user_input = user_input.strip()
            st.rerun()

    if st.button("Restart Interview"):
        logger.info("Restart Interview button clicked.")
        st.session_state.session_id = None
        st.session_state.history = []
        st.session_state.is_waiting = False
        st.rerun()
