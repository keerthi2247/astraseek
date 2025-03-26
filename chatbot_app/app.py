from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import google.generativeai as genai
from PyPDF2 import PdfReader  # For PDF text extraction

# Configure Gemini Pro model
genai.configure(api_key=os.getenv("AIzaSyCzZn0h87yUo6clBFSYAWwrhsyxxLJGxfY"))

# Initialize Gemini Pro model
model = genai.GenerativeModel("gemini-1.5-pro")

# Initialize Streamlit app
st.set_page_config(page_title="AstraSeek - Limitless Learning", layout="wide")
st.header("AstraSeek")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to get Gemini response
def get_gemini_response(question, chat_history):
    # Format the chat history for the model
    formatted_history = []
    for role, text in chat_history:
        if role == "You":
            formatted_history.append({"role": "user", "parts": [text]})
        elif role == "Bot":
            formatted_history.append({"role": "model", "parts": [text]})
    
    # Start a new chat session with the formatted history
    chat = model.start_chat(history=formatted_history)
    response = chat.send_message(question, stream=True)
    
    # Collect all chunks into a single response
    full_response = ""
    for chunk in response:
        full_response += chunk.text
    
    # Ensure the response is fully resolved
    response.resolve()  # Resolve the response to avoid IncompleteIterationError
    
    # Return the full response and updated chat history
    return full_response, chat.history

# Sidebar for Chat History
with st.sidebar:
    st.header("Chat History")
    if st.button("Clear History"):
        st.session_state['chat_history'] = []
    
    # Display user questions and bot responses in the sidebar
    for idx, (role, text) in enumerate(st.session_state['chat_history']):
        if role == "You":
            with st.expander(f"Q: {text}"):
                for r, t in st.session_state['chat_history'][idx:idx+2]:  # Question + Answer
                    st.write(f"**{r}:** {t}")

# Main chat interface
with st.form(key="chat_form"):
    input = st.text_input("Every question leads to knowledge. What's yours? 🧭", key="input")
    submit = st.form_submit_button("Search🔍")

# PDF Upload and Question Generation
st.header("Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from the uploaded PDF
    pdf_text = extract_text_from_pdf(uploaded_file)
    
    # Display the extracted text (optional)
    with st.expander("View Extracted Text"):
        st.write(pdf_text)
    
    # Generate important questions from the PDF text
    if st.button("Generate Important Questions from PDF"):
        prompt = f"Generate 5 important questions based on the following text:\n\n{pdf_text}"
        response, _ = get_gemini_response(prompt, st.session_state['chat_history'])
        
        # Display the generated questions
        st.subheader("Important Questions from the PDF")
        st.write(response)
        
        # Add the generated questions to the chat history
        st.session_state['chat_history'].append(("Bot", response))

if submit and input:
    # Get the response and updated chat history
    full_response, updated_history = get_gemini_response(input, st.session_state['chat_history'])
    
    # Display the complete response without breakage
    st.subheader("The Response is")
    st.write(full_response)  # Display the full response at once
    
    # Add the user's question and bot's response to the chat history
    st.session_state['chat_history'].append(("You", input))
    st.session_state['chat_history'].append(("Bot", full_response))
