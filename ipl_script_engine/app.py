import streamlit as st
import json
import random
import time
from pathlib import Path
import os
import requests

st.set_page_config(page_title="The Scriptwriter's Revenge", page_icon="🎬")
# Material-like styling (Roboto font + card styles)
st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            html, body { font-family: 'Roboto', sans-serif; }
            .app-header { display:flex; align-items:center; gap:12px; }
            .app-title { font-size:28px; font-weight:700; margin:0; }
            .app-sub { color: #666; margin:0; }
            .mui-card { background: #fff; border-radius:12px; padding:16px; box-shadow: 0 6px 18px rgba(22,28,45,0.08); }
            .mui-row { display:flex; gap:12px; }
            .mui-card.small { flex:1; }
            .prediction-box { background: linear-gradient(90deg, #f7f9fb, #ffffff); border-radius:10px; padding:16px; color:#000 !important; }
            .prediction-box h4 { color:#000 !important; margin:0 0 8px 0 }
            .prediction-box, .prediction-box * { color: #000 !important; }
            .prediction-box a { color: #000 !important; text-decoration: underline; }
            .muted { color:#666; font-size:14px }
            .news-link { color:#1a73e8; text-decoration:none; }
            .icon { font-size:26px }
        </style>
        <div class="app-header">
            <div class="icon">🎬</div>
            <div>
                <div class="app-title">The Scriptwriter's Revenge</div>
                <div class="app-sub">Live IPL Conspiracy Generator — sentiment & quick predictions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
)

st.write("")

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

    # keep backward compatibility: simple list of strings
    simple_reactions = data.get("fan_reactions", [])
    detailed = data.get("fan_reactions_detailed", [])

    # build a merged reactions list: prioritize detailed entries formatted, then simple strings
    reactions = []
    for d in detailed:
        try:
            user = d.get('user') or d.get('handle') or 'user'
            time_str = d.get('created_at') or ''
            text = d.get('text') or ''
            reactions.append(f"{user}: {text} [{time_str}]")
        except Exception:
            continue
    # append simple legacy reactions
    reactions.extend(simple_reactions)
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

    # bilingual/Hindi support: occasionally insert Hindi phrases or mixed-language sentences
    hindi_clips = [
        "यह धोखाधड़ी लगती है",
        "क्या चल रहा है",
        "बॉल अचानक ऐसा घूम गया",
        "ये मैच कुछ गड़बड़ सा है",
        "फैंस गुस्से में हैं"
    ]
    # randomly include one Hindi clip to make the prediction bilingual
    import random as _rand
    if _rand.random() < 0.7:  # 70% chance to include Hindi flavor
        seed_phrases.append(_rand.choice(hindi_clips))

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
            sentences.append(f"\"{clean}\".")
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

col1, col2 = st.columns([2, 1])

with col1:
    if st.button('Generate New Plot Twist', key='generate'):
        points = get_script()
        # three small material-like cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='mui-card small'><strong>🚨 LEAKED SCRIPT</strong><div class='muted'>{points[0]}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='mui-card small'><strong>🕵️ MATCH ANOMALY</strong><div class='muted'>{points[1]}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='mui-card small'><strong>💀 THE CLIMAX</strong><div class='muted'>{points[2]}</div></div>", unsafe_allow_html=True)

        prediction = generate_prediction(points, min_words=40, max_words=100)
        st.markdown(f"<div class='mui-card prediction-box'><h4 style='margin:0 0 8px 0'>Prediction</h4><div>{prediction}</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='mui-card'><strong>Live Summary</strong></div>", unsafe_allow_html=True)
    st.write("- Monitoring sentiment for LSG vs CSK")
    st.write("- Latest reactions sampled from fan posts")
    st.write("")

st.write("---")
st.write("Monitoring live sentiment for LSG vs CSK...")


st.write("---")
st.markdown("<div class='muted'>News & external sources</div>", unsafe_allow_html=True)

# Sidebar: API keys and news search
st.sidebar.header("News & Settings")
query = st.sidebar.text_input("Search query", value="cricket tweets")
max_results = st.sidebar.slider("Max results", min_value=1, max_value=10, value=5)
gnews_key = st.sidebar.text_input("GNews API Key", value=os.environ.get('GNEWS_API_KEY') or '', help='Set GNEWS_API_KEY env var for deployments')
newsapi_key = st.sidebar.text_input("NewsAPI Key", value=os.environ.get('NEWSAPI_KEY') or '', help='Set NEWSAPI_KEY env var for deployments')
if st.sidebar.button('Fetch News', key='fetch'):
    with st.spinner('Fetching news...'):
        # if user filled keys in sidebar, use them temporarily
        if gnews_key:
            os.environ['GNEWS_API_KEY'] = gnews_key
        if newsapi_key:
            os.environ['NEWSAPI_KEY'] = newsapi_key
        articles = fetch_news(query, max_results=max_results)

    if not articles:
        st.info("No articles found or API keys not configured.")
    else:
        for a in articles:
            title = a.get('title') or 'No title'
            url = a.get('url') or '#'
            src = a.get('source') or 'unknown'
            desc = a.get('description') or ''
            st.markdown(f"<div class='mui-card'><strong>{title}</strong><div class='muted'>Source: {src} — <a class='news-link' href='{url}' target='_blank'>Open</a></div><div style='margin-top:8px'>{desc}</div></div>", unsafe_allow_html=True)
            st.write("")