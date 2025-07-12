import streamlit as st
import whisper

# import openai
import os
from pydub import AudioSegment
from datetime import timedelta
import tempfile
from dotenv import load_dotenv
import requests
import json

# ========== ENV ==========
load_dotenv()
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = OPENAI_API_KEY

# ========== CONFIG ==========
# MODEL_SIZE = "medium"  # Whisper model size: "tiny", "base", "small", "medium", "large"
# CHUNK_DURATION_MINUTES = 10
# # ===========================

# client = openai.OpenAI(api_key=OPENAI_API_KEY)


def format_time(ms):
    return str(timedelta(milliseconds=ms))


def split_audio(audio, chunk_duration_ms):
    return [
        audio[i : i + chunk_duration_ms]
        for i in range(0, len(audio), chunk_duration_ms)
    ]


def transcribe_audio(audio_file, model, index=None):
    label = f"chunk {index}" if index is not None else "file"
    st.info(f"🔊 Transcribing {label}...")
    result = model.transcribe(audio_file, language="fa")
    return result["text"]


def summarize_text(transcript):
    st.info("🧠 Summarizing the transcription...")

    prompt = f"""متن زیر را به صورت خلاصه و روان در چند جمله بیان کن:\n\n{transcript}"""

    payload = {
        "model": "llama3",  # or any model you've pulled
        "messages": [
            {
                "role": "system",
                "content": "تو یک دستیار هستی که متن‌های فارسی را خلاصه می‌کنی.",
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        response.raise_for_status()
        summary = response.json()["message"]["content"]
        return summary.strip()

    except requests.exceptions.RequestException as e:
        st.error("❌ خطا در اتصال به مدل Ollama")
        st.error(str(e))
        return "خلاصه‌سازی انجام نشد."


def main():
    st.set_page_config(page_title="Persian Audio Summarizer", layout="centered")
    st.title("🧠 Persian Audio Summarizer")
    st.markdown("آپلود فایل صوتی فارسی و دریافت خلاصه آن با کمک هوش مصنوعی")

    uploaded_file = st.file_uploader(
        "🎙️ فایل صوتی را انتخاب کنید", type=["mp3", "wav", "m4a"]
    )

    if uploaded_file is not None:
        # 🟢 Step 1: Save uploaded file temporarily
        with st.spinner("📁 در حال ذخیره فایل صوتی..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=uploaded_file.name[-4:]
            ) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name

        st.success("✅ فایل با موفقیت بارگذاری شد!")

        # 🎧 Step 2: Load & preprocess audio
        with st.spinner("🎚️ در حال پردازش فایل صوتی..."):
            audio = (
                AudioSegment.from_file(temp_path).set_frame_rate(16000).set_channels(1)
            )

        # ✂️ Step 3: Split audio if too long
        chunk_duration_ms = CHUNK_DURATION_MINUTES * 60 * 1000
        if len(audio) > chunk_duration_ms:
            st.info(f"🎧 طول فایل صوتی زیاد است: {format_time(len(audio))}")
            with st.spinner("✂️ در حال تقسیم فایل صوتی به بخش‌های کوچکتر..."):
                chunks = split_audio(audio, chunk_duration_ms)
            st.success(f"✅ فایل به {len(chunks)} بخش تقسیم شد.")
        else:
            chunks = [audio]

        # 📦 Step 4: Load Whisper model
        with st.spinner("🔁 در حال بارگذاری مدل Whisper..."):
            whisper_model = whisper.load_model(MODEL_SIZE)

        # 🔊 Step 5: Transcribe chunks
        full_transcript = ""
        progress_bar = st.progress(0, text="🔄 در حال تبدیل صوت به متن...")

        for idx, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk:
                chunk.export(temp_chunk.name, format="wav")

                with st.spinner(f"🔊 بخش {idx+1} در حال پردازش است..."):
                    text = transcribe_audio(
                        temp_chunk.name, whisper_model, index=idx + 1
                    )

                full_transcript += text + "\n"
                os.remove(temp_chunk.name)

            progress = int(((idx + 1) / len(chunks)) * 100)
            progress_bar.progress(
                progress, text=f"📦 پردازش {idx + 1} از {len(chunks)} بخش"
            )

        progress_bar.empty()

        # 📄 Step 6: Show transcript
        st.subheader("📄 متن کامل استخراج‌شده:")
        st.text_area("Transcript", full_transcript[:3000], height=200)

        # 🧠 Step 7: Summarize transcript
        with st.spinner("🧠 در حال خلاصه‌سازی متن..."):
            summary = summarize_text(full_transcript)

        # 📝 Step 8: Show summary
        st.subheader("📝 خلاصه متن:")
        st.success(summary)

        # 🧽 Cleanup
        os.remove(temp_path)


if __name__ == "__main__":
    main()
