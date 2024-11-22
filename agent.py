
from groq import Groq
from dotenv import load_dotenv
import os

from datetime import datetime
import os
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
