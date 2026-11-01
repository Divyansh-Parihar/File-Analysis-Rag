import streamlit as st
import requests
from logger import get_logger

logger = get_logger(__name__)
logger.debug
('Streamlit app started')

URL = "http://localhost:5000"

st.header("File Analysis")
upload_file = st.file_uploader("Upload Your File")

if st.button("Summarize") and upload_file:
    logger.info(f"Summarize button clicked | file='{upload_file.name}' | size={upload_file.size} bytes")

    with st.spinner("Analyzing... this may take a moment"):
        logger.debug(f"Sending POST to {URL}/summarize")
        response = requests.post(f"{URL}/summarize", files={'file': (upload_file.name, upload_file.getvalue())})

    logger.info(f"Response received | status_code={response.status_code}")

    if response.status_code == 200:
        result = response.json()
        logger.info(f"Success | topic= '{result['topic']}'")

        st.subheader(f"Title: {result['topic']}")
        st.write(f"Summary: {result['summary']}")
        st.write("Topics Discussed: ")
        for topic in result['key_topics']:
            st.write(f'- {topic}')
    else:
        error_msg = response.json().get('error', "Something went wrong.")
        logger.error(f"Request failed | status={response.status_code} | error='{error_msg}'")
        st.error(error_msg)
        

