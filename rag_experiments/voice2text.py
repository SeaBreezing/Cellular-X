# pip install openai pyaudio pydub

from openai import OpenAI
import pyaudio
from pydub import AudioSegment
import threading

def recording():
    FORMAT = pyaudio.paInt16  # 16 depth bit
    CHANNELS = 1              # single channel
    RATE = 44100              # sample rate
    CHUNK = 1024              # frames per buffer
    OUTPUT_MP3 = "record.mp3" # mp3 file to save

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

    audio_segment = AudioSegment(
        data=b''.join(frames),
        sample_width=audio.get_sample_size(FORMAT),
        frame_rate=RATE,
        channels=CHANNELS
    )
    audio_segment.export(OUTPUT_MP3, format="mp3")

    print(f"Recording saved as {OUTPUT_MP3}")

def v2text(mp3_file, use_micro = False):
    import time
    a = time.time()
    if use_micro == True:
        recording()
    client = OpenAI(
        api_key="your_api_key",
        base_url="your_url"
    )
    audio_file = open(mp3_file, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="json"
    )
    b = time.time()
    print(b-a)
    return transcript.text # return a string 

def t2voice(text, answer_index=0):
    client = OpenAI(
    api_key="your_api_key",
    base_url="your_url"
    )
    response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
    response.stream_to_file(f"answer_{answer_index}.mp3")

if __name__ == "__main__":
    # text = v2text("record.mp3", use_micro = True) # use this line to record and convert to text
    text = v2text("revise.mp3") # use this line to convert local mp3 file to text
    # t2voice("What is the height of the BS antenna in the UMa scenario?", 2) # convert text to voice
    print(text)
