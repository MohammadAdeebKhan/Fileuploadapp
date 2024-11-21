from pydub import AudioSegment




class Chunking:

    def __init__(self):
        pass

    def chunk_audio(self , file_path, chunk_length_ms=10000):
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
