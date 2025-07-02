import whisper
# import openai
import os
from pydub import AudioSegment
from datetime import timedelta
import tempfile
# from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# load_dotenv()


# ========== CONFIG ==========
AUDIO_PATH = "voice/New Recording.m4a"  # 🔁 Replace with your file path
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY',default=None)           # 🔁 Replace with your API key
MODEL_SIZE = "medium"  # Options: "base", "medium", "large"
CHUNK_DURATION_MINUTES = 10  # Split if longer than this
SUMMARY_MODEL = "ahmeddbahaa/mT5_multilingual_XLSum-finetuned-fa"
# =============================

# model_name = "ahmeddbahaa/mT5_multilingual_XLSum-finetuned-fa"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# def split_audio(audio, chunk_duration_ms):
#     chunks = []
#     for i in range(0, len(audio), chunk_duration_ms):
#         chunk = audio[i:i + chunk_duration_ms]
#         chunks.append(chunk)
#     return chunks


def format_time(ms):
    return str(timedelta(milliseconds=ms))


def split_audio(audio, chunk_ms):
    return [audio[i : i + chunk_ms] for i in range(0, len(audio), chunk_ms)]


# Load summarization model
tokenizer = AutoTokenizer.from_pretrained(SUMMARY_MODEL)
summ_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARY_MODEL, trust_remote_code=True, use_safetensors=True)


def transcribe_audio(audio_file, model, index=None):
    label = f"chunk {index}" if index is not None else "file"
    print(f"[2] Transcribing {label}...")
    result = model.transcribe(audio_file, language="fa")
    return result["text"]


def transcribe_whisper(path, model, idx=None):
    label = f"chunk {idx}" if idx is not None else "file"
    print(f"[2] Transcribing {label}...")
    return model.transcribe(path, language="fa")["text"]


def summarize_text(text):
    print("[3] Summarizing with mT5...")
    inputs = tokenizer.encode(
        text, return_tensors="pt", truncation=True, max_length=1024
    )
    summary_ids = summ_model.generate(
        inputs, num_beams=4, max_length=150, min_length=60, early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()


def main():
    # if not os.path.exists(AUDIO_PATH):
    #     print("⚠️ File not found.")
    #     return

    # audio = AudioSegment.from_file(AUDIO_PATH).set_frame_rate(16000).set_channels(1)
    # chunk_ms = CHUNK_DURATION_MINUTES * 60 * 1000
    # chunks = split_audio(audio, chunk_ms) if len(audio) > chunk_ms else [audio]

    # whisper_model = whisper.load_model(MODEL_SIZE)
    # full_text = ""
    # for i, chunk in enumerate(chunks, 1):
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
    #         chunk.export(tmp.name, format="wav")
    #         full_text += transcribe_whisper(tmp.name, whisper_model, idx=i) + "\n"
    #         os.remove(tmp.name)

    # print("\n📄 Transcript sample:")
    # print(full_text[:500] + "...")
    
    full_text = """
     سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست
 سلام من ایمان هستم این یک وئیس تستی برای پروژه من هست

    """

    summary = summarize_text(full_text)
    print("\n📝 Summary:")
    print(summary)


if __name__ == "__main__":
    main()
