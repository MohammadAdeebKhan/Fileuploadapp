import streamlit as st
import requests

# The URL of the Django API for uploading files
API_URL = "https://expenseapp.creowiz.com/api/save_docs/"  # Replace with your actual API endpoint

def upload_file_to_api(uploaded_file):
    """Send the uploaded file to the Django API and return the file URL."""
    # Prepare the file as a dictionary to send in a multipart/form-data POST request
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

    # Send POST request to the Django API with the uploaded file
    response = requests.post(API_URL, files=files)

    if response.status_code == 201:
        # Successfully uploaded, return the file URL from the response
        return response.json().get("file", None)
    else:
        st.error(f"Failed to upload file. Error: {response.text}")
        return None

def display_uploaded_files(file_urls):
    """Display a list of uploaded file URLs in Streamlit."""
    if file_urls:
        st.write("### Uploaded Files:")
        for url in file_urls:
            st.markdown(f"[Click here to access the file]({url})")
    else:
        st.write("No files uploaded yet.")

# Streamlit app UI
st.title("File Upload with Django and Streamlit")

# File uploader widget
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "flac", "ogg"])

if uploaded_file:
    # Call the API to upload the file
    file_url = upload_file_to_api(uploaded_file)

    if file_url:
        # Show success message and the file URL
        st.success(f"File uploaded successfully! You can access the file at: {file_url}")

        # Store the file URL in Streamlit session state to keep track of uploaded files
        if "file_urls" not in st.session_state:
            st.session_state.file_urls = []

        # Add the newly uploaded file URL to the session state
        st.session_state.file_urls.append(file_url)

# Display all uploaded file URLs
display_uploaded_files(st.session_state.get("file_urls", []))
