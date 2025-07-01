import whisper
import openai
import os
from pydub import AudioSegment
from datetime import timedelta
import tempfile
from dotenv import load_dotenv

load_dotenv()


# ========== CONFIG ==========
AUDIO_PATH = "voice/New Recording.m4a"  # 🔁 Replace with your file path
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY',default=None)           # 🔁 Replace with your API key
MODEL_SIZE = "medium"               # Options: "base", "medium", "large"
CHUNK_DURATION_MINUTES = 10        # Split if longer than this
# =============================

# ✅ Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def format_time(ms):
    return str(timedelta(milliseconds=ms))

def split_audio(audio, chunk_duration_ms):
    chunks = []
    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        chunks.append(chunk)
    return chunks

def transcribe_audio(audio_file, model, index=None):
    label = f"chunk {index}" if index is not None else "file"
    print(f"[2] Transcribing {label}...")
    result = model.transcribe(audio_file, language="fa")
    return result["text"]

def summarize_text(transcript):
    print("[3] Summarizing with GPT-4...")

    prompt = f"""متن زیر را به صورت خلاصه و روان در چند جمله بیان کن:

{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "تو یک دستیار هستی که متن‌های فارسی را خلاصه می‌کنی."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response.choices[0].message.content
    return summary.strip()

def main():
    if not os.path.exists(AUDIO_PATH):
        print(f"⚠️ File not found: {AUDIO_PATH}")
        return

    print(f"[1] Loading audio: {AUDIO_PATH}")
    audio = AudioSegment.from_file(AUDIO_PATH)
    audio = audio.set_frame_rate(16000).set_channels(1)

    chunk_duration_ms = CHUNK_DURATION_MINUTES * 60 * 1000
    if len(audio) > chunk_duration_ms:
        print(f"[1.1] Audio is long ({format_time(len(audio))}). Splitting...")
        chunks = split_audio(audio, chunk_duration_ms)
    else:
        chunks = [audio]

    model = whisper.load_model(MODEL_SIZE)
    full_transcript = ""

    for idx, chunk in enumerate(chunks):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk:
            chunk.export(temp_chunk.name, format="wav")
            transcript = transcribe_audio(temp_chunk.name, model, index=idx+1)
            full_transcript += transcript + "\n"
            os.remove(temp_chunk.name)

    print("\n📄 Combined Transcript Preview (first 500 chars):")
    print(full_transcript[:500] + "...\n")

    summary = summarize_text(full_transcript)

    print("\n📝 Final Summary:")
    print(summary)

if __name__ == "__main__":
    main()
