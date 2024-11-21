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






class TranscribeAgent:

    def __init__(self):
        pass

    def process_audio(self , chunk):

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




        


        chunk = Chunking()
        chunks = chunk.chunk_audio(temp_file)
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
