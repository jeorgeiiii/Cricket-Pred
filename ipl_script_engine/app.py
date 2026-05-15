import streamlit as st
import json
import random
import time
from pathlib import Path
import os
import requests

st.set_page_config(page_title="The Scriptwriter's Revenge", page_icon="🎬")

st.title("🎬 The Scriptwriter's Revenge")
st.subheader("Live IPL Conspiracy Generator")

def get_script():
    data_path = Path(__file__).resolve().parent / 'data' / 'tweets.json'
    if not data_path.exists():
        st.error(f"Data file not found: {data_path}")
        return ["No data available"] * 3
    try:
        with data_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"Error reading data file: {e}")
        return ["No data available"] * 3

    reactions = data.get("fan_reactions", [])
    if len(reactions) < 3:
        return random.choices(reactions or ["No data available"], k=3)
    return random.sample(reactions, 3)


def analyze_reactions(reactions):
    import re
    from collections import Counter

    joined = " ".join(reactions)
    words = re.findall(r"\w+", joined.lower())
    stopwords = {
        'the','and','a','to','is','in','for','of','on','with','that','this','it','as','are','be'
    }
    filtered = [w for w in words if w not in stopwords]
    common = [w for w,_ in Counter(filtered).most_common(6)]

    # crude sentiment-ish score from simple positive/negative lists
    positive = {'great','good','win','love','amazing','fantastic','dominant','brilliant'}
    negative = {'bad','poor','loss','hate','terrible','suspicious','shocking','controversial'}
    score = sum(1 if w in positive else -1 if w in negative else 0 for w in filtered)
    tone = 'positive' if score > 0 else 'negative' if score < 0 else 'mixed/neutral'

    analysis_sentences = []
    analysis_sentences.append(f"Overall tone across the sampled fan reactions appears {tone}.")
    if common:
        analysis_sentences.append(f"The most frequent themes/words include: {', '.join(common)}.")
    analysis_sentences.append(
        "Comments frequently mention match events, player actions, and perceived anomalies — indicating focused engagement from fans about on-field incidents."
    )
    analysis_sentences.append(
        "This concentration of attention can amplify narratives rapidly on social platforms, which means small incidents may be framed as systemic issues by vocal groups."
    )
    analysis_sentences.append(
        "If the pattern continues, we may see stronger calls for official reviews, trending hashtags, and intensified media coverage, affecting team reputations and fan discourse."
    )

    analysis = " ".join(analysis_sentences)
    # Ensure at least 100 words — pad with explanatory text if necessary
    while len(analysis.split()) < 100:
        analysis += (
            " Further context: monitoring sentiment across more tweets and over time will clarify whether this is a transient spike or a lasting perception shift."
        )

    return analysis


def generate_prediction(reactions, min_words=40, max_words=100):
    import re
    from collections import Counter
    import random

    # prepare word tokens from reactions
    joined = " ".join(reactions)
    words = re.findall(r"\w+", joined.lower())
    stopwords = {
        'the','and','a','to','is','in','for','of','on','with','that','this','it','as','are','be'
    }
    filtered = [w for w in words if w not in stopwords]
    common = [w for w,_ in Counter(filtered).most_common(6)]

    # base sentences that reference the idea of a 'strategic' misfield
    seed_phrases = []
    if common:
        seed_phrases.append(f"Fans repeatedly mention {', '.join(common)} in their posts, which frames the context.")
    seed_phrases.append("Given the volume and tenor of reactions, social observers expect an incident framed as deliberate or 'strategic'.")
    seed_phrases.append("On the next over, narratives suggest a subtle fielding lapse will be interpreted as intentional by vocal groups.")
    seed_phrases.append("This could lead to trending hashtags, heated commentary, and renewed scrutiny of umpiring and team tactics.")

    # assemble paragraphs until min_words reached
    sentences = []
    # always state the core prediction early
    sentences.append("Prediction: A 'strategic' misfield is likely to occur in the next over, according to the prevailing fan chatter and sentiment.")
    sentences.extend(seed_phrases)

    # add a bit of explanatory padding using recycled reactions
    extras = [r for r in reactions if r and r != "No data available"]
    random.shuffle(extras)
    for e in extras:
        clean = re.sub(r"\s+", " ", e.strip())
        if clean:
            sentences.append(f"For example, users said: \"{clean}\".")
        if len(" ".join(sentences).split()) >= min_words:
            break

    # pad further with general context sentences if still short
    while len(" ".join(sentences).split()) < min_words:
        sentences.append(
            "Monitoring this thread over the next few minutes should confirm whether the reaction is transient or part of a larger pattern of orchestrated responses."
        )

    prediction = " ".join(sentences)
    # enforce maximum length
    words_list = prediction.split()
    if len(words_list) > max_words:
        prediction = " ".join(words_list[:max_words]).rstrip() + "..."

    return prediction


def fetch_gnews(query, api_key, max_results=5, lang='en'):
    url = 'https://gnews.io/api/v4/search'
    params = {'q': query, 'token': api_key, 'lang': lang, 'max': max_results}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    articles = []
    for a in data.get('articles', [])[:max_results]:
        articles.append({
            'title': a.get('title'),
            'description': a.get('description'),
            'url': a.get('url'),
            'source': a.get('source', {}).get('name'),
            'publishedAt': a.get('publishedAt')
        })
    return articles


def fetch_newsapi(query, api_key, page_size=5):
    url = 'https://newsapi.org/v2/everything'
    params = {'q': query, 'apiKey': api_key, 'pageSize': page_size, 'language': 'en'}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    articles = []
    for a in data.get('articles', [])[:page_size]:
        articles.append({
            'title': a.get('title'),
            'description': a.get('description'),
            'url': a.get('url'),
            'source': a.get('source', {}).get('name'),
            'publishedAt': a.get('publishedAt')
        })
    return articles


def fetch_news(query, max_results=5):
    # Prefer GNews if key present, otherwise try NewsAPI. Keys must be set as env vars.
    gkey = os.environ.get('GNEWS_API_KEY') or os.environ.get('GNEWS_KEY')
    nkey = os.environ.get('NEWSAPI_KEY') or os.environ.get('NEWS_API_KEY')
    if gkey:
        try:
            return fetch_gnews(query, gkey, max_results=max_results)
        except Exception as e:
            st.warning(f"GNews fetch failed: {e}")
    if nkey:
        try:
            return fetch_newsapi(query, nkey, page_size=max_results)
        except Exception as e:
            st.warning(f"NewsAPI fetch failed: {e}")

    # If no keys or all failed, return empty and an instruction message
    st.info(
        "To enable live news fetching, set `GNEWS_API_KEY` or `NEWSAPI_KEY` environment variables with a free API key." 
        "GNews (gnews.io) and NewsAPI (newsapi.org) both offer free tiers for small projects."
    )
    return []

if st.button('Generate New Plot Twist'):
    points = get_script()
    st.info(f"🚨 **LEAKED SCRIPT:** {points[0]}")
    st.warning(f"🕵️ **MATCH ANOMALY:** {points[1]}")
    st.error(f"💀 **THE CLIMAX:** {points[2]}")
    prediction = generate_prediction(points, min_words=40, max_words=100)
    st.subheader("Prediction")
    st.write(prediction)

st.write("---")
st.write("Monitoring live sentiment for LSG vs CSK...")


st.write("---")
st.header("Cricket News Search")
query = st.text_input("Search query", value="cricket tweets")
max_results = st.slider("Max results", min_value=1, max_value=10, value=5)
if st.button('Fetch News'):
    with st.spinner('Fetching news...'):
        articles = fetch_news(query, max_results=max_results)

    if not articles:
        st.info("No articles found or API keys not configured.")
    else:
        for a in articles:
            title = a.get('title') or 'No title'
            url = a.get('url') or '#'
            src = a.get('source') or 'unknown'
            desc = a.get('description') or ''
            st.markdown(f"**{title}**  ")
            st.markdown(f"Source: {src} — [{url}]({url})")
            if desc:
                st.write(desc)
            st.write("---")