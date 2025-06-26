# pip install openai pyaudio pydub
import traceback

from openai import OpenAI
import pyaudio, wave
from pydub import AudioSegment
import threading, io

def recording(OUTPUT_WAV):
    FORMAT = pyaudio.paInt16  # 16 depth bit
    CHANNELS = 1              # single channel
    RATE = 44100              # sample rate
    CHUNK = 1024              # frames per buffer

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    frames = []
    global stop_recording 
    stop_recording = False

    def record_audio():
        while not stop_recording:
            data = stream.read(CHUNK)
            frames.append(data)

    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

    input("Press 'Enter' to stop recording...")

    stop_recording = True
    recording_thread.join() 

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # audio_segment = AudioSegment(
    #     data=b''.join(frames),
    #     sample_width=audio.get_sample_size(FORMAT),
    #     frame_rate=RATE,
    #     channels=CHANNELS
    # )
    # audio_segment.export(OUTPUT_MP3, format="mp3")

    # print(f"Recording saved as {OUTPUT_MP3}")
    # Save as WAV file directly using wave module
    with wave.open(OUTPUT_WAV, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Recording saved as {OUTPUT_WAV}")

def v2text(wav_file, use_micro = False):
    import time
    a = time.time()
    if use_micro == True:
        recording(wav_file)
    client = OpenAI(
        api_key="YOUR_API_KEY_HERE",
        base_url="YOUR_API_FORWARDING_URL_HERE"
    )
    with open(wav_file, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="json"
        )        
    b = time.time()
    # print(b-a)
    return transcript.text # return a string 

def t2voice(text, answer_index=0):
    import wave
    import pyaudio
    from openai import OpenAI
    
    client = OpenAI(
        api_key="YOUR_API_KEY_HERE",
        base_url="YOUR_API_FORWARDING_URL_HERE"
    )
    
    # Generate the WAV file
    # response = client.audio.speech.create(
    #             model="tts-1",
    #             voice="alloy",
    #             input=text,
    #             response_format="wav"
    #         )
    # output_file = f"answer_{answer_index}.wav"
    # response.stream_to_file(output_file)

    with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=text,
    response_format="wav"
    ) as response:
        output_file = f"answer_{answer_index}.wav"
        with open(output_file, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    
    # Open the generated WAV file for playback
    with wave.open(output_file, 'rb') as wf:
        pa = pyaudio.PyAudio()
        
        # Open the sound card for output
        stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        # Play the audio (properly stops when file ends)
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        
        while data:
            stream.write(data)  # Write audio data to output stream
            data = wf.readframes(chunk_size)
            # print('*')
        
        # Close everything
        stream.stop_stream()
        stream.close()
        pa.terminate()

if __name__ == "__main__":
    # text = v2text("record.wav", True) # use this line to convert local mp3 file to text
    # print(text)
    t2voice('What is transmit gain of RF configuration?')
    