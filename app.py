import pymysql
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydub import AudioSegment
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import os




def process_audio(chunk):

        transcriptions = []
        

        load_dotenv()
        API_KEY = os.getenv("SECRET_KEY")
        client = Groq(api_key = API_KEY)

        temp_file = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        with open(temp_file, "wb") as f:
            data = chunk.getvalue()
            if data:
                f.write(data)
            else:
                print("No data to write to the file")




        


        #chunk = Chunking()
        chunks = chunk_audio(temp_file)
        transcriptions = []
        

        for chunk in chunks:

            with open(chunk , "rb") as f:
                audio_data = f.read()
                transcription = client.audio.transcriptions.create(
                                file=(chunk, audio_data),
                                model="whisper-large-v3",
                                prompt="specify content and spelling and the sponsor name",
                                response_format="json",
                                language="en",
                                temperature = 0.0
                            )
            
                
            transcribe_text = transcription.text 
            #return transcribe_text 
            transcriptions.append(transcribe_text)
                
            full_transcription = "\n".join(transcriptions)
            print(full_transcription)
            return full_transcription , temp_file

def chunk_audio(file_path, chunk_length_ms=10000):
        """Chunk an audio file into smaller parts based on chunk length."""

        #length = chunk_length_ms
        audio = AudioSegment.from_file(file_path)
        full_chunk = len(audio)
        chunks = []
        chunk_size = full_chunk // 4
        start_ms = 0

        
        while start_ms < full_chunk:
            
            #print(f'This is sart_ms {start_ms}')
            end_ms = start_ms + chunk_size
            
            #print(f"this is {end_ms}")
            chunk_audio = audio[start_ms:end_ms]
            
            
            chunk_file_path = f"chunk{start_ms}.mp3"
            
            if len(chunk_audio) > 1:
                chunk_audio.export(chunk_file_path, format="mp3")
                chunks.append(chunk_file_path)
            
            
            #chunks.append(chunk_file_path)

            
            start_ms += chunk_size
            
        
        return chunks

def agent(audio_file):
        
        full_transcription = ""
        
        load_dotenv()
        API_KEY = os.getenv("SECRET_KEY")
        # client = Groq(api_key = API_KEY)


        
        
        if not API_KEY:
            st.error("API_KEY not found in environment variables")
            return None
        
    

        llm = ChatGroq(api_key=API_KEY , model="llama3-8b-8192")

        
        #agents = TranscribeAgent()
        full_transcription ,temp_file = process_audio(audio_file)

        
        print(f"This is the full transcription {full_transcription}")
        messages = [
            SystemMessage(content="Give me the sponsor name from the given text please do analyze"),
            HumanMessage(content=full_transcription)
        ]

        response = llm.invoke(messages)
        sponsor_name = response.content



        messages = [
            SystemMessage(content="Give me the show name from the given text please do analyze"),
            HumanMessage(content=full_transcription)
        ]

        response = llm.invoke(messages)
        show_name = response.content

        messages = [
            SystemMessage(content=''' Give me the number of time the sponsor name is mentioned in the text following with sponsor 
            word don't give text just give number of time it mentioned '''),
            HumanMessage(content=full_transcription)
        ]

        response = llm.invoke(messages)
        number_of_time = response.content

        os.remove(temp_file)
        return {
            "transcription": full_transcription,
            "sponsor_name": sponsor_name,
            "show_name": show_name,
            "number_of_time": number_of_time
        }

#chunk = Chunking()



def save_to_database(sponsor_name, show_name, transcriptions):
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="Mysql@123",
            database="sponsors"
        )

        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS sponsordetails(
            sponsor VARCHAR(255) NOT NULL,
            show_name VARCHAR(255) NOT NULL,
            transcribed_text TEXT NOT NULL,
            datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)

        insert_query = """
        INSERT INTO sponsordetails (sponsor, show_name, transcribed_text)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(insert_query, (sponsor_name, show_name, transcriptions))
        connection.commit()

    except pymysql.Error as db_error:
        st.error(f"Database error: {str(db_error)}")

    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def view_database():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="Mysql@123",
            database="sponsors"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT sponsor, show_name, transcribed_text, datetime FROM sponsordetails")
        records = cursor.fetchall()
        return records

    except pymysql.Error as db_error:
        st.error(f"Database error: {str(db_error)}")
        return []

    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def main():
    

    
    st.title("Audio Processing Application")
    
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload Audio", "View Records"])

    if page == "Upload Audio":
        st.header("Upload Audio File")
        
        uploaded_file = st.file_uploader("Choose an audio file", type = ['mp3', 'wav', 'm4a'])
        
        if uploaded_file is not None:
            st.audio(uploaded_file)
            
            if st.button("Process Audio"):
                with st.spinner("Processing audio..."):
                    

                    result = agent(uploaded_file)
                    
                    
                    
                if result:
                    save_to_database(result['sponsor_name'] , result["show_name"] , result['transcription'])
                    st.success("Audio processed successfully!")
                    
                    st.subheader("Transcription")
                    st.write(result["transcription"])
                    
                    st.subheader("Sponsor Information")
                    st.write(result["sponsor_name"])
                    
                    st.subheader("Show Name")
                    st.write(result["show_name"])

                    st.subheader("number_of_time_sponsor_mentioned")
                    st.write(result["number_of_time"])

    else:  
        
        st.header("Database Records")
        records = view_database()
        
        if records:
            st.table([
                {
                    "Sponsor": record[0],
                    "Show Name": record[1],
                    "Transcribed Text": record[2],
                    "Date/Time": record[3]
                }
                for record in records
            ])
        else:
            st.info("No records found in the database.")


main()
#if __name__ == '__main__':
        #freeze_support()
        #main()


# import streamlit as st
# import requests

# # The URL of the Django API for uploading files
# API_URL = "https://expenseapp.creowiz.com/api/save_docs/"  # Replace with your actual API endpoint

# def upload_file_to_api(uploaded_file):
#     """Send the uploaded file to the Django API and return the file URL."""
#     # Prepare the file as a dictionary to send in a multipart/form-data POST request
#     files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

#     # Send POST request to the Django API with the uploaded file
#     response = requests.post(API_URL, files=files)

#     if response.status_code == 201:
#         # Successfully uploaded, return the file URL from the response
#         return response.json().get("file", None)
#     else:
#         st.error(f"Failed to upload file. Error: {response.text}")
#         return None

# def display_uploaded_files(file_urls):
#     """Display a list of uploaded file URLs in Streamlit."""
#     if file_urls:
#         st.write("### Uploaded Files:")
#         for url in file_urls:
#             st.markdown(f"[Click here to access the file]({url})")
#     else:
#         st.write("No files uploaded yet.")

# # Streamlit app UI
# st.title("File Upload with Django and Streamlit")

# # File uploader widget
# uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "flac", "ogg","pdf","jpg","pptx","jpeg","png"])

# if uploaded_file:
#     # Call the API to upload the file
#     file_url = upload_file_to_api(uploaded_file)

#     if file_url:
#         # Show success message and the file URL
#         st.success(f"File uploaded successfully! You can access the file at: {file_url}")

#         # Store the file URL in Streamlit session state to keep track of uploaded files
#         if "file_urls" not in st.session_state:
#             st.session_state.file_urls = []

#         # Add the newly uploaded file URL to the session state
#         st.session_state.file_urls.append(file_url)

# # Display all uploaded file URLs
# display_uploaded_files(st.session_state.get("file_urls", []))
