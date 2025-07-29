import streamlit as st
import arxiv
import requests

# App title and description
st.title("🔍 Research Paper Summarizer")
st.write("Enter a research topic below and get summarized insights from recent arXiv papers.")

# Sidebar for model selection
st.sidebar.header("🔧 Options")
model = st.sidebar.selectbox(
    "Choose a model from OpenRouter",
    options=[
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mixtral-8x7b-instruct",
        "openchat/openchat-3.5-1210",
        "nousresearch/nous-capybara-7b",
    ],
    index=0
)

# Search input
topic = st.text_input("Enter your research topic", value="ethics in AI")
search_button = st.button("🔍 Search Papers")

# --- Function to search arXiv ---
def search_arxiv_papers(query, max_results=5):
    results = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    ).results()
    return list(results)

# --- Function to call OpenRouter API ---
def summarize_paper(title, abstract, model):
    prompt = f"""Summarize the following academic paper in 3 concise bullet points:

Title: {title}

Abstract:
{abstract}

Format the response as:
- Point 1
- Point 2
- Point 3
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30
        )

        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"❌ Error summarizing: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error summarizing: {str(e)}"

# --- Main execution ---
if search_button and topic:
    st.info(f"🔎 Searching for papers related to: **{topic}**")

    papers = search_arxiv_papers(topic)
    
    if not papers:
        st.warning("No papers found. Try a different keyword.")
    else:
        st.subheader("📚 Paper Summaries")
        for i, paper in enumerate(papers, 1):
            st.markdown(f"### 🔗 [{paper.title}]({paper.entry_id})")
            summary = summarize_paper(paper.title, paper.summary, model)
            st.markdown(summary)
