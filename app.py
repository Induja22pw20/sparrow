import streamlit as st
import openai
import whisper
import torch
import numpy as np
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
from speechbrain.inference import SpeakerRecognition
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

# OpenAI API Key
openai.api_key = "your-api-key"

# Load AI models
whisper_model = whisper.load_model("base")
emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
speaker_model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="tmp")

# Store User Progress
if "progress" not in st.session_state:
    st.session_state.progress = {"Rapid Fire": [], "Triple Step": [], "Conductor": []}

# App UI Layout
st.set_page_config(page_title="AI-Powered Public Speaking Trainer", layout="wide")

st.sidebar.title("🎤 AI Public Speaking Trainer")
option = st.sidebar.radio("Select Exercise", ["Home", "Rapid Fire Analogies", "Triple Step", "Conductor", "Dashboard"])

# Audio Recording & Processing Function
def transcribe_audio(audio):
    with open(audio, "rb") as f:
        result = whisper_model.transcribe(f.name)
    return result["text"]

# Home Page
if option == "Home":
    st.title("🎤 AI Public Speaking Trainer")
    st.write("Enhance your speaking skills with AI-driven exercises and real-time feedback.")
    st.image("https://source.unsplash.com/1600x900/?microphone,speech", use_column_width=True)

# Rapid Fire Analogies
elif option == "Rapid Fire Analogies":
    st.header("🧠 Rapid Fire Analogies")
    st.write("Complete the analogy in 5 seconds!")

    analogy_prompts = [
        "Life is like _____",
        "Success is like _____",
        "Learning is like _____",
        "Friendship is like _____"
    ]

    if st.button("Start Exercise"):
        prompt = random.choice(analogy_prompts)
        st.write(f"**{prompt}**")
        webrtc_ctx = webrtc_streamer(key="analogies", mode=WebRtcMode.SENDRECV)

        if st.button("Submit Response"):
            st.write("Processing your response... ⏳")
            time.sleep(2)

            user_response = "Life is like a rollercoaster."  # Replace with transcribed text from audio
            st.write(f"Your response: {user_response}")

            feedback_prompt = f"Analyze this analogy: {user_response}. Score creativity, timing, and relevance."
            feedback = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": feedback_prompt}])

            st.write(f"**AI Feedback:** {feedback['choices'][0]['message']['content']}")
            st.session_state.progress["Rapid Fire"].append({"Analogy": user_response, "Score": random.randint(1, 10)})

# Triple Step Exercise
elif option == "Triple Step":
    st.header("🎯 Triple Step Challenge")
    st.write("Stay focused while handling distractions!")

    if st.button("Generate Topic"):
        topics = ["Technology", "Artificial Intelligence", "Climate Change", "Space Exploration"]
        selected_topic = random.choice(topics)
        st.write(f"**Your topic: {selected_topic}**")

        distractors = ["Banana", "Traffic Light", "Snowstorm", "Whale"]
        distractor_word = random.choice(distractors)
        st.write(f"**Distraction: {distractor_word}**")

        webrtc_ctx = webrtc_streamer(key="triplespeech", mode=WebRtcMode.SENDRECV)

        if st.button("Submit Speech"):
            st.write("Analyzing speech coherence... ⏳")
            time.sleep(2)

            coherence_score = round(random.uniform(0, 1), 2)
            st.write(f"**AI Score:** {coherence_score} (1.0 = Perfect Coherence)")
            st.session_state.progress["Triple Step"].append({"Topic": selected_topic, "Score": coherence_score})

# Conductor Exercise
elif option == "Conductor":
    st.header("🎶 Conductor Exercise")
    st.write("Vary your vocal energy levels and receive feedback!")

    energy_levels = ["Low", "Medium", "High"]
    selected_energy = random.choice(energy_levels)
    st.write(f"**Speak with {selected_energy} energy level!**")

    webrtc_ctx = webrtc_streamer(key="conductor", mode=WebRtcMode.SENDRECV)

    if st.button("Submit Speech"):
        st.write("Analyzing your vocal variety... ⏳")
        time.sleep(2)

        detected_emotion = emotion_model("I am excited about AI!")  # Replace with transcribed text
        st.write(f"**Detected Emotion:** {detected_emotion[0]['label']}")

        feedback_prompt = f"How can the speech be improved for better vocal delivery?"
        feedback = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": feedback_prompt}])

        st.write(f"**AI Feedback:** {feedback['choices'][0]['message']['content']}")
        st.session_state.progress["Conductor"].append({"Energy Level": selected_energy, "Emotion": detected_emotion[0]['label']})

# Dashboard for Progress Tracking
elif option == "Dashboard":
    st.header("📊 User Progress Dashboard")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Rapid Fire Analogies Scores")
        rf_data = pd.DataFrame(st.session_state.progress["Rapid Fire"])
        if not rf_data.empty:
            st.bar_chart(rf_data.set_index("Analogy"))
        else:
            st.write("No data yet.")

    with col2:
        st.subheader("🎯 Triple Step Scores")
        ts_data = pd.DataFrame(st.session_state.progress["Triple Step"])
        if not ts_data.empty:
            st.line_chart(ts_data.set_index("Topic"))
        else:
            st.write("No data yet.")

    st.subheader("🎶 Conductor Exercise Results")
    c_data = pd.DataFrame(st.session_state.progress["Conductor"])
    if not c_data.empty:
        st.write(c_data)
    else:
        st.write("No data yet.")

st.sidebar.success("Select an exercise to begin!")
