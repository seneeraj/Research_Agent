import streamlit as st
import requests
import arxiv
from openai import OpenAI

# Load API key securely from Streamlit secrets
api_key = st.secrets["OPENROUTER_API_KEY"]
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# --- 🔁 Fetch Available Models ---
@st.cache_data
def get_available_models():
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json()["data"]

        # Only include models that support 'chat' and are active
        available_models = [
            m["id"] for m in models
            if m.get("permissions", {}).get("completion") == "chat" and not m.get("deprecated", False)
        ]

        return sorted(available_models)
    except Exception as e:
        print(f"⚠️ Failed to load models: {e}")
        return ["meta-llama/llama-3-8b-instruct"]  # Fallback

# --- 🧠 LLM Calls ---
def summarize_paper(title, model):
    prompt = f"Summarize the key findings and contributions of this research paper titled: '{title}'"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error summarizing: {e}"

def synthesize_review(summaries, topic, model):
    joined = "\n\n".join(summaries)
    prompt = f"Based on the following summaries of research papers, write a concise literature review on the topic '{topic}':\n\n{joined}"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error generating review: {e}"

# --- 🎛️ UI ---
st.title("📄 Research Agent — Literature Review Synthesizer")
topic = st.text_input("Enter your research topic:", value="Deep Learning in Non-English Languages")
max_results = st.slider("How many top papers to retrieve?", 1, 10, 5)

model = st.selectbox("Choose a working LLM from OpenRouter", get_available_models())

if st.button("🔍 Generate Review"):
    st.markdown("⏳ **Fetching papers from arXiv...**")
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = [result.title for result in search.results()]
    
    st.markdown("📚 **Paper Titles Summarized**")
    summaries = []
    for idx, title in enumerate(papers, 1):
        st.markdown(f"**{idx}. {title}**")
        summary = summarize_paper(title, model)
        summaries.append(summary)
        st.markdown(summary)

    st.markdown("---")
    st.markdown("📝 **Synthesized Literature Review**")
    review = synthesize_review(summaries, topic, model)
    st.markdown(review)
