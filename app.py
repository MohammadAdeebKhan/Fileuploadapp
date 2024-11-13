import torch
from  transformers import WhisperProcessor , WhisperForConditionalGeneration
import librosa
import numpy
from groq import Groq
from dotenv import load_dotenv
import os
import pymysql
import json
from tinytag import TinyTag
import streamlit as st
from datetime import datetime
import os
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
import ffmpeg
from pydub import AudioSegment
import io`
from mutagen import File
from moviepy.editor import AudioFileClip
from mutagen.id3 import ID3

from django.core.files.storage import FileSystemStorage
from pathlib import Path
import audio_metadata
from io import BytesIO
from mutagen import File
from mutagen.easyid3 import EasyID3
from mp3_tagger import MP3File
import music_tag

# def get_metadata(audio_file):

#     audio_bytes = BytesIO(audio_file.getvalue())
#     tags = music_tag.load_file(audio_bytes)
#     print(tags)

def process_audio(audio_file):
    try:
        
        # path = Path("tmp")
        # path.mkdir(parents=False,exist_ok=True)
        # fs = FileSystemStorage(location="tmp")
        # file_name = fs.save(audio_file.name , audio_file)
        # file_path = fs.url(file_name)

        temp_file = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        
        with open(temp_file, "wb") as f:
            data = audio_file.getvalue()
            if data:
                #print(data)


                f.write(data)
            else:
                print("No data to write to the file ")
            timestamp = os.path.getctime(temp_file)
            creation_date = datetime.fromtimestamp(timestamp)
            print(f"This is creation date {creation_date}")
        

        # Load environment variables
        load_dotenv()
        API_KEY = os.getenv("SECRET_KEY")
        
        if not API_KEY:
            st.error("API_KEY not found in environment variables")
            return None

        # Initialize Groq client
        client = Groq(api_key=API_KEY)

        # Transcribe audio
        with open(temp_file, "rb") as file:
            audio_data = file.read()
            transcription = client.audio.transcriptions.create(
                file=(temp_file, audio_data),
                #file = file , 
                model="whisper-large-v3",
                prompt="specify content and spelling and the sponsor name",
                response_format="json",
                language="en",
                temperature=0.0
            )

        

        transcribe_text = transcription.text
        
        # Get sponsor information using chat completion
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You have to find the sponsor name from the text just give the sponsor name no extra text from your side"
                },
                {
                    "role": "user",
                    "content": transcribe_text
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.0
        )

        sponsor_name = chat_completion.choices[0].message.content


        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You have to find the show name from the current text just give show name no extra text from your side"
                },
                {
                    "role": "user",
                    "content": transcribe_text
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.0
        )

        show_name = chat_completion.choices[0].message.content


        # Clean up temporary file
        os.remove(temp_file)

        # Save to database
        save_to_database(sponsor_name, show_name, transcribe_text)
        
        return {
            "transcription": transcribe_text,
            "sponsor": sponsor_name,
            "show_name": show_name
        }

    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None


def save_to_database(sponsor_name, show_name, transcribe_text):
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
        
        cursor.execute(insert_query, (sponsor_name, show_name, transcribe_text))
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
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload Audio", "View Records"])

    if page == "Upload Audio":
        st.header("Upload Audio File")
        
        uploaded_file = st.file_uploader("Choose an audio file", type = ['mp3', 'wav', 'm4a'])
        
        if uploaded_file is not None:
            st.audio(uploaded_file)
            
            if st.button("Process Audio"):
                with st.spinner("Processing audio..."):
                    #get_metadata(uploaded_file)
                    result = process_audio(uploaded_file)
                    
                if result:
                    st.success("Audio processed successfully!")
                    
                    st.subheader("Transcription")
                    st.write(result["transcription"])
                    
                    st.subheader("Sponsor Information")
                    st.write(result["sponsor"])
                    
                    st.subheader("Show Name")
                    st.write(result["show_name"])

    else:  # View Records page
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



