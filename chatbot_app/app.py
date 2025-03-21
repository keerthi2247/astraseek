from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import google.generativeai as genai

# Configure Gemini Pro model
genai.configure(api_key=os.getenv("AIzaSyCzZn0h87yUo6clBFSYAWwrhsyxxLJGxfY"))

# Initialize Gemini Pro model
model = genai.GenerativeModel("gemini-1.5-pro")
chat = model.start_chat(history=[])

# Function to get Gemini response
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Initialize Streamlit app
st.set_page_config(page_title="AstraSeek - Limitless learning", layout="wide")
st.header("AstraSeek")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Sidebar for Chat History
with st.sidebar:
    st.header("Chat History")
    if st.button("Clear History"):
        st.session_state['chat_history'] = []
    
    # Display user questions in the sidebar
    for idx, (role, text) in enumerate(st.session_state['chat_history']):
        if role == "You":
            with st.expander(f"Q: {text}"):
                for r, t in st.session_state['chat_history'][idx:idx+2]:  # Question + Answer
                    st.write(f"**{r}:** {t}")

# Main chat interface
with st.form(key="chat_form"):
    input = st.text_input("Every question leads to knowledge. What's yours? 🧭", key="input")
    submit = st.form_submit_button("Search🔍")

if submit and input:
    response = get_gemini_response(input)
    st.session_state['chat_history'].append(("You", input))
    
    # Collect all chunks into a single response
    full_response = ""
    for chunk in response:
        full_response += chunk.text
    
    # Display the complete response without breakage
    st.subheader("The Response is")
    st.write(full_response)  # Display the full response at once
    
    # Add the full response to the chat history
    st.session_state['chat_history'].append(("Bot", full_response))
