import streamlit as st
import pandas as pd
from io import StringIO

# Title of the app
st.title("File Upload Example")

# Instructions
st.markdown("""
    Please upload a file. We currently support CSV and TXT files.
""")

# File uploader widget
uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt"])

# Check if a file is uploaded
if uploaded_file is not None:
    # If the uploaded file is a CSV file
    if uploaded_file.type == "text/csv":
        # Read the CSV file into a pandas dataframe
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV file:")
        st.dataframe(df)  # Display the dataframe

    # If the uploaded file is a TXT file
    elif uploaded_file.type == "text/plain":
        # Read the TXT file content
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        text = stringio.read()
        st.text_area("Uploaded Text File", text, height=300)

    else:
        st.error("Unsupported file type")
else:
    st.info("Please upload a file to get started")
