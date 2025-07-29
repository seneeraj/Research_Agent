import streamlit as st
import arxiv
import openai

# Load OpenRouter API Key
openai.api_key = st.secrets["OPENROUTER_API_KEY"]
openai.base_url = "https://openrouter.ai/api/v1"

st.set_page_config(page_title="Research Agent", layout="wide")
st.title("🧠 Research Agent")

# Model options (you can dynamically fetch this too)
available_models = [
    "meta-llama/llama-3-8b-instruct",
    "mistralai/mistral-7b-instruct",
    "openchat/openchat-7b",
    "mistralai/mixtral-8x7b-instruct"
]

# Sidebar input
st.sidebar.title("🔍 Search Settings")
topic = st.sidebar.text_input("Enter a research topic", value="Multilingual LLMs")
selected_model = st.sidebar.selectbox("Choose an LLM", available_models)
max_results = st.sidebar.slider("Number of papers", 1, 10, 5)

# Search Arxiv papers
@st.cache_data(show_spinner=False)
def search_papers(topic, max_results=5):
    client = arxiv.Client(num_retries=3)
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    return list(client.results(search))

# Summarize each paper
def summarize_paper(title, abstract, model):
    prompt = f"""Summarize the following academic paper in 3 concise bullet points:

Title: {title}

Abstract:
{abstract}

Format the response as:
- Point 1
- Point 2
- Point 3"""

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error summarizing: {e}"

# Run search
if topic:
    with st.spinner("🔎 Searching papers..."):
        papers = search_papers(topic, max_results)

    if papers:
        st.markdown("## 📚 Paper Titles Summarized")
        for paper in papers:
            title = paper.title.strip()
            link = paper.entry_id
            abstract = paper.summary.strip()

            st.markdown(f"### 🔗 [{title}]({link})")
            with st.spinner(f"Summarizing: {title[:60]}..."):
                summary = summarize_paper(title, abstract, selected_model)
                st.markdown(summary)
            st.markdown("---")
    else:
        st.warning("No papers found for that topic.")
