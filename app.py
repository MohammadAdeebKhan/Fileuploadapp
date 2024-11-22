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
import io
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
from pydub import AudioSegment
import tempfile
import torch
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
import librosa
import torchaudio
from transformers import pipeline
import torch
from gradio_client import Client, file
from transformers import pipeline, AutoModelForCausalLM, AutoModelForSpeechSeq2Seq, AutoProcessor
import whisper
import textwrap
from langchain_groq import ChatGroq
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
import time
from chunks import Chunking
import multiprocessing as mp
from agent import TranscribeAgent
from multiprocessing import Process, freeze_support


def agent(audio_file):
        
        full_transcription = ""
        
        load_dotenv()
        API_KEY = os.getenv("SECRET_KEY")
        # client = Groq(api_key = API_KEY)


        
        
        if not API_KEY:
            st.error("API_KEY not found in environment variables")
            return None
        
    

        llm = ChatGroq(api_key=API_KEY , model="llama3-8b-8192")

        
        agents = TranscribeAgent()
        full_transcription ,temp_file = agents.process_audio(audio_file)

        
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

chunk = Chunking()



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



