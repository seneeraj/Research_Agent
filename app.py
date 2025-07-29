import streamlit as st
import openai
import requests
import arxiv

# Title
st.title("🧠 Research Paper Summarizer")

# Load API Key
api_key = st.secrets["OPENROUTER_API_KEY"]

# Set base URL and headers for OpenRouter
base_url = "https://openrouter.ai/api/v1"
headers = {"Authorization": f"Bearer {api_key}"}

# Get Available Models from OpenRouter
@st.cache_data
def get_available_models():
    try:
        response = requests.get(f"{base_url}/models", headers=headers)
        response.raise_for_status()
        models = response.json()["data"]

        available_models = [
            m["id"] for m in models
            if "chat" in m.get("tags", []) or m.get("id", "").endswith("chat")
        ]
        if not available_models:
            return ["meta-llama/llama-3-8b-instruct"]
        return sorted(available_models)

    except Exception as e:
        print(f"⚠️ Model fetch error: {e}")
        return ["meta-llama/llama-3-8b-instruct"]  # Fallback

# Model selection dropdown
model = st.selectbox("✅ Choose a working LLM from OpenRouter", get_available_models())

# Paper search and summarization
topic = st.text_input("🔍 Enter research topic:")
num_papers = st.slider("📄 Number of papers to summarize:", 1, 10, 5)

def search_papers(topic, max_results=5):
    search = arxiv.Search(query=topic, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    return [result.title for result in search.results()]

def summarize_paper(title):
    prompt = f"Summarize the research paper titled '{title}' in simple terms, highlighting the main contribution."
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error summarizing: {e}"

def synthesize_review(summaries, topic):
    joined = "\n\n".join(summaries)
    prompt = f"Based on the following summaries, write a concise literature review about '{topic}':\n\n{joined}"
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error generating review: {e}"

# Main Execution
if st.button("Generate Summaries"):
    with st.spinner("⏳ Searching papers..."):
        papers = search_papers(topic, num_papers)

    st.subheader("📚 Paper Titles Summarized")
    summaries = []
    for i, title in enumerate(papers, 1):
        st.markdown(f"**{i}. {title}**")
        summary = summarize_paper(title)
        st.markdown(summary)
        summaries.append(summary)

    st.subheader("📝 Synthesized Literature Review")
    review = synthesize_review(summaries, topic)
    st.markdown(review)
