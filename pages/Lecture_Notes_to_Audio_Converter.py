import streamlit as st
from gtts import gTTS
import io

st.title("Lecture Notes-to-Audio Converter📢")
st.markdown("Converts your notes into an MP3 file")

input_text = st.text_area("Paste Your Notes Here:", height=200)

if st.button("Generate Audio Lecture"):
    if not input_text:
        st.warning("Please paste some text before generating audio.")
        st.stop()

    try:
        with st.spinner("Synthesizing audio..."):
            tts = gTTS(text=input_text, lang='en')

            audio_io = io.BytesIO()
            tts.write_to_fp(audio_io)
            audio_io.seek(0)

            st.success("Audio generated successfully!")

            st.audio(audio_io, format='audio/mp3')

            st.download_button(
                label="Download Audio note",
                data=audio_io.getvalue(),
                file_name="Study_notes_audio.mp3",
                mime="audio/mp3"
            )
    except Exception as e:
        st.error(f"An error occurred during audio generation: {e}")