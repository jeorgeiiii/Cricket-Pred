import streamlit as st
import json
import random
import time

st.set_page_config(page_title="The Scriptwriter's Revenge", page_icon="🎬")

st.title("🎬 The Scriptwriter's Revenge")
st.subheader("Live IPL Conspiracy Generator")

def get_script():
    with open('data/tweets.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    reactions = data.get("fan_reactions", [])
    return random.sample(reactions, 3)

if st.button('Generate New Plot Twist'):
    points = get_script()
    st.info(f"🚨 **LEAKED SCRIPT:** {points[0]}")
    st.warning(f"🕵️ **MATCH ANOMALY:** {points[1]}")
    st.error(f"💀 **THE CLIMAX:** {points[2]}")
    st.success("Prediction: A 'strategic' misfield is coming next over.")

st.write("---")
st.write("Monitoring live sentiment for LSG vs CSK...")