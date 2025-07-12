import streamlit as st
import time
import base64

# import whisper
import openai
import os
import shutil
from pydub import AudioSegment
from datetime import timedelta, datetime
import tempfile
from dotenv import load_dotenv

# ========== ENV ==========
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ========== CONFIG ==========
# MODEL_SIZE = "medium"  # Whisper model size: "tiny", "base", "small", "medium", "large"
CHUNK_DURATION_MINUTES = 2
# ===========================

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def local_font(path: str):
    if not os.path.exists(path):
        # st.error(f"Font file not found: {path}")
        return
    with open(path, "rb") as f:
        font_data = f.read()
    b64_font = base64.b64encode(font_data).decode()
    font_face = f"""
    <style>
    @font-face {{
        font-family: "MyFont";
        src: url(data:font/ttf;base64,{b64_font}) format("truetype");
    }}

    html, body, [class*="st-"] {{
        font-family: "MyFont", sans-serif;
        direction: rtl;
        text-align: right;
    }}
    </style>
    """
    st.markdown(font_face, unsafe_allow_html=True)


def format_time(ms):
    return str(timedelta(milliseconds=ms))


def split_audio(audio, chunk_duration_ms):
    return [
        audio[i : i + chunk_duration_ms]
        for i in range(0, len(audio), chunk_duration_ms)
    ]


def transcribe_audio_via_api(audio_path, prompt, index=None):
    label = f"بخش {index}" if index is not None else "فایل"
    st.info(f"🔊 در حال ارسال {label} به OpenAI gpt-4o-transcribe API...")

    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
            language="fa",  # Optional, but improves accuracy for Persian
            # prompt='نام شرکت ها مثل مکعب، نام افراد مانند عابد پور'
            prompt=prompt,
        )

    return transcript.text


def show_logs_ui():
    log_root = os.path.join(os.path.dirname(__file__), "log")
    st.sidebar.title("📁 تاریخچه و لاگ‌ها")
    if not os.path.exists(log_root):
        st.sidebar.info("هنوز لاگی وجود ندارد.")
        return

    # Get all log folders, sorted by timestamp descending
    log_folders = [
        f for f in os.listdir(log_root)
        if os.path.isdir(os.path.join(log_root, f))
    ]
    if not log_folders:
        st.sidebar.info("هنوز لاگی وجود ندارد.")
        return
    log_folders.sort(reverse=True)

    # Show most recent log by default
    selected_log = st.sidebar.selectbox(
        "یک لاگ را انتخاب کنید:", log_folders, format_func=lambda x: x.replace('_', ' ')
    )
    if not selected_log:
        return

    log_dir = os.path.join(log_root, selected_log)
    st.sidebar.markdown(f"**زمان:** `{selected_log}`")

    # List files in log folder, show text files first, then others
    files = sorted(os.listdir(log_dir), key=lambda x: (not x.endswith('.txt'), x))
    for fname in files:
        file_path = os.path.join(log_dir, fname)
        # Try to read as text, fallback to binary
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            is_text = True
        except Exception:
            with open(file_path, "rb") as f:
                content = f.read()
            is_text = False

        with st.sidebar.expander(fname):
            if is_text:
                st.code(content, language=None)
            else:
                st.write("(فایل غیر متنی)")
        st.sidebar.download_button(
            label=f"دانلود {fname}",
            data=content,
            file_name=fname,
            mime="text/plain" if is_text else "application/octet-stream",
        )


def summarize_text(transcript, gpt_prompt):
    st.info("🧠 Summarizing the transcription...")
    #     prompt = f"""

    # به صورت مفید و جامع بازنویسی و در قالب زیر گزارش بده
    # ۱ موضوع صحبت
    # ۲ اعضای حاضر در  ویس با اسم و فامیل
    # ۳ مدت زمان جلسه در حالت مفید
    # ۴ صحبت هایی که برای گزارش مفید است
    # ۵ مدت زمان غیر مفید جلسه (زمان های استراحت و سکوت )
    # ۶ زمان کل جلسه
    # ۷ نتیجه کلی جلسه
    # ۸ احساسات افراد در ابتدا و انتهای جلسه (به طور مقال مشتری با رضایت خداحافظی کرد ناراحت یا خنثی و أیا تمام خواسته ها شنیده شد یا خیر)
    # ۹ کارهای ارجاع شده چه بوده و چه کسی تا چه زمانی انجام داده؟
    # نکته : اگر یکی از موارد بالا در ویس مجهول بود بنویس به این موضوع پرداخته نشده است

    # {transcript}
    # """
    prompt = f"""
{gpt_prompt}

{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "تو یک دستیار هستی که متن‌های فارسی را خلاصه می‌کنی.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    summary = response.choices[0].message.content
    return summary.strip()


# ========== LOGGING ===========
def save_request_log(
    original_file_path,
    original_file_name,
    transcribe_prompt,
    transcript,
    gpt_prompt,
    summary,
    extra_data=None,
):
    log_root = os.path.join(os.path.dirname(__file__), "log")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_dir = os.path.join(log_root, timestamp)
    os.makedirs(log_dir, exist_ok=True)

    # Save original file
    if original_file_path and os.path.exists(original_file_path):
        shutil.copy2(
            original_file_path, os.path.join(log_dir, f"original_{original_file_name}")
        )

    # Save transcribe prompt
    with open(
        os.path.join(log_dir, "transcribe_prompt.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(transcribe_prompt or "")

    # Save transcript
    with open(os.path.join(log_dir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(transcript or "")

    # Save gpt prompt
    with open(os.path.join(log_dir, "gpt_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(gpt_prompt or "")

    # Save summary
    with open(os.path.join(log_dir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary or "")

    # Save any extra data
    if extra_data:
        for key, value in extra_data.items():
            with open(os.path.join(log_dir, f"{key}.txt"), "w", encoding="utf-8") as f:
                f.write(str(value))

    return log_dir


def main():
    st.set_page_config(
        page_title="Persian Audio Summarizer",
        layout="centered",
    )
    
    # show_logs_ui()

    print("🔵 App started: Setting up font and UI")
    local_font("fonts/IRANSansX-Regular.ttf")

    st.title("🧠 Persian Audio Summarizer")
    st.markdown("آپلود فایل صوتی فارسی و دریافت خلاصه آن با کمک هوش مصنوعی")

    uploaded_file = st.file_uploader(
        "🎙️ فایل صوتی را انتخاب کنید", type=["mp3", "wav", "m4a"]
    )
    print("🟢 File uploader rendered")

    transcribe_prompt = st.text_input(
        "راهنمایی gpt برای تشخیص درست متن: ",
        " نام شرکت ها مثل مکعب، نام افراد مانند عابد پور و بهرامی فر",
    )
    print("🟢 Transcribe prompt input rendered")

    gpt_prompt = st.text_area(
        "پرامپت gpt جهت خلاصه کردن متن:",
        """به صورت مفید و جامع بازنویسی و در قالب زیر گزارش بده 
۱ موضوع صحبت
۲ اعضای حاضر در  ویس با اسم و فامیل 
۳ مدت زمان جلسه در حالت مفید
۴ صحبت هایی که برای گزارش مفید است
۵ مدت زمان غیر مفید جلسه (زمان های استراحت و سکوت )
۶ زمان کل جلسه
۷ نتیجه کلی جلسه
۸ احساسات افراد در ابتدا و انتهای جلسه (به طور مقال مشتری با رضایت خداحافظی کرد ناراحت یا خنثی و أیا تمام خواسته ها شنیده شد یا خیر)
۹ کارهای ارجاع شده چه بوده و چه کسی تا چه زمانی انجام داده؟
نکته : اگر یکی از موارد بالا در ویس مجهول بود بنویس به این موضوع پرداخته نشده است

    """,
        height=300,
    )
    print("🟢 GPT prompt input rendered")

    if uploaded_file is not None:
        print("🟡 File uploaded, saving temporarily...")
        with st.spinner("📁 در حال ذخیره فایل صوتی..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=uploaded_file.name[-4:]
            ) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name

        st.success("✅ فایل با موفقیت بارگذاری شد!")
        print(f"✅ File saved at {temp_path}")

        print("🟡 Loading and preprocessing audio...")
        with st.spinner("🎚️ در حال پردازش فایل صوتی..."):
            audio = (
                AudioSegment.from_file(temp_path).set_frame_rate(16000).set_channels(1)
            )
        print("✅ Audio loaded and preprocessed")

        chunk_duration_ms = CHUNK_DURATION_MINUTES * 60 * 1000
        if len(audio) > chunk_duration_ms:
            st.info(f"🎧 طول فایل صوتی زیاد است: {format_time(len(audio))}")
            print("🟡 Audio is long, splitting into chunks...")
            with st.spinner("✂️ در حال تقسیم فایل صوتی به بخش‌های کوچکتر..."):
                chunks = split_audio(audio, chunk_duration_ms)
            st.success(f"✅ فایل به {len(chunks)} بخش تقسیم شد.")
            print(f"✅ Audio split into {len(chunks)} chunks")
        else:
            chunks = [audio]
            print("✅ Audio is short, no split needed")

        full_transcript = ""
        progress_bar = st.progress(0, text="🔄 در حال تبدیل صوت به متن...")
        total_seconds = 0
        start_total = time.time()

        for idx, chunk in enumerate(chunks):
            print(f"🟡 Processing chunk {idx+1}/{len(chunks)}...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk:
                chunk.export(temp_chunk.name, format="wav")
                start = time.time()

                with st.spinner(f"🔊 بخش {idx+1} در حال پردازش است..."):
                    text = transcribe_audio_via_api(
                        temp_chunk.name, transcribe_prompt, index=idx + 1
                    )

                end = time.time()
                duration = end - start
                st.success(f"⏱️ بخش {idx+1} در {duration:.2f} ثانیه پردازش شد")
                print(f"✅ Chunk {idx+1} processed in {duration:.2f} seconds")

                full_transcript += text + "\n"
                total_seconds += len(chunk) / 1000  # ms to sec
                os.remove(temp_chunk.name)

            progress = int(((idx + 1) / len(chunks)) * 100)
            progress_bar.progress(
                progress, text=f"📦 پردازش {idx + 1} از {len(chunks)} بخش"
            )

        progress_bar.empty()
        end_total = time.time()
        st.info(f"🕒 کل زمان پردازش: {end_total - start_total:.2f} ثانیه")
        print(f"✅ All chunks processed in {end_total - start_total:.2f} seconds")

        total_minutes = total_seconds / 60
        cost_estimate = total_minutes * 0.006
        st.info(f"💰 هزینه تقریبی پردازش: ${cost_estimate:.4f} (به نرخ $0.006/min)")
        print(f"💰 Estimated cost: ${cost_estimate:.4f}")

        st.subheader("📄 متن کامل استخراج‌شده:")
        st.text_area("Transcript", full_transcript, height=200)
        print("🟢 Transcript displayed")

        # Copy transcript button
        st.code(full_transcript, language=None)
        st.caption("برای کپی کردن متن استخراج‌شده، روی آیکون 📋 کلیک کنید.")

        st.download_button(
            label="📥 دانلود متن کامل",
            data=full_transcript,
            file_name="transcript.txt",
            mime="text/plain",
        )
        print("🟢 Transcript download button rendered")

        with st.spinner("🧠 در حال خلاصه‌سازی متن..."):
            print("🟡 Summarizing transcript...")

            summary = summarize_text(full_transcript, gpt_prompt)
        print("✅ Summary generated")

        # Save log for this request
        save_request_log(
            original_file_path=temp_path,
            original_file_name=uploaded_file.name,
            transcribe_prompt=transcribe_prompt,
            transcript=full_transcript,
            gpt_prompt=gpt_prompt,
            summary=summary,
            extra_data={
                "cost_estimate": cost_estimate,
                "processing_time": end_total - start_total,
                "audio_length": format_time(len(audio)),
            },
        )

        st.subheader("📝 خلاصه متن:")
        st.success(summary)
        print("🟢 Summary displayed")

        # Copy summary button
        st.code(summary, language=None)
        st.caption("برای کپی کردن خلاصه، روی آیکون 📋 کلیک کنید.")

        st.download_button(
            label="📥 دانلود خلاصه",
            data=summary,
            file_name="summary.txt",
            mime="text/plain",
        )
        print("🟢 Summary download button rendered")

        os.remove(temp_path)
        print("🧽 Temporary files cleaned up")

    print("✅ App ready for next action")


if __name__ == "__main__":
    main()
