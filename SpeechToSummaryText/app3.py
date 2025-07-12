import openai

audio_file= open("/", "rb")

client = openai.audio.transcriptions.create(model='gpt-4o-transcribe')