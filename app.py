import streamlit as st
import arxiv
import requests

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Research Paper Summarizer",
    page_icon="🔍",
    layout="wide"
)

# ---------------------------------------------------
# App Title
# ---------------------------------------------------
st.title("🔍 Research Paper Summarizer")
st.write(
    "Enter a research topic below and get summarized insights "
    "from recent arXiv papers."
)

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
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

max_results = st.sidebar.slider(
    "Number of papers",
    min_value=1,
    max_value=10,
    value=5
)

# ---------------------------------------------------
# Supported Research Domains
# ---------------------------------------------------

SUPPORTED_TOPICS = {
    "Artificial Intelligence": [
        "machine learning",
        "deep learning",
        "generative ai",
        "llm",
        "computer vision",
        "nlp",
        "reinforcement learning",
        "ai ethics"
    ],

    "Cybersecurity": [
        "malware detection",
        "network security",
        "phishing",
        "cyber attacks",
        "cryptography"
    ],

    "Healthcare AI": [
        "medical imaging",
        "cancer detection",
        "drug discovery",
        "healthcare analytics"
    ],

    "Robotics": [
        "robotics",
        "autonomous systems",
        "robot navigation"
    ],

    "Mathematics": [
        "statistics",
        "probability",
        "linear algebra",
        "optimization"
    ],

    "Physics": [
        "quantum computing",
        "astrophysics",
        "particle physics"
    ]
}






# ---------------------------------------------------
# Search Input
# ---------------------------------------------------
topic = st.text_input(
    "Enter your research topic",
    value="ethics in AI"
)

search_button = st.button("🔍 Search Papers")

# ---------------------------------------------------
# Function to Search arXiv Papers
# ---------------------------------------------------
def search_arxiv_papers(query, max_results=5):
    try:
        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = list(client.results(search))
        return results

    except Exception as e:
        st.error(f"❌ Error fetching papers: {str(e)}")
        return []

# ---------------------------------------------------
# Function to Summarize Paper
# ---------------------------------------------------
def summarize_paper(title, abstract, model):
    prompt = f"""
Summarize the following academic paper in 3 concise bullet points.

Title:
{title}

Abstract:
{abstract}

Format:
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
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5
            },
            timeout=60
        )

        # Check status code
        if response.status_code != 200:
            return f"❌ API Error ({response.status_code}): {response.text}"

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]

        return "❌ No summary returned from model."

    except requests.exceptions.Timeout:
        return "❌ Request timed out."

    except Exception as e:
        return f"❌ Error summarizing: {str(e)}"

# ---------------------------------------------------
# Main Execution
# ---------------------------------------------------
if search_button:

    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    st.info(f"🔎 Searching for papers related to: **{topic}**")

    with st.spinner("Fetching papers from arXiv..."):
        papers = search_arxiv_papers(topic, max_results)

    if not papers:
        st.warning("No papers found. Try a different keyword.")

    else:
        st.success(f"✅ Found {len(papers)} papers")

        st.subheader("📚 Paper Summaries")

        for i, paper in enumerate(papers, 1):

            with st.container():

                st.markdown("---")

                st.markdown(f"## 📄 Paper {i}")

                st.markdown(
                    f"### 🔗 [{paper.title}]({paper.entry_id})"
                )

                authors = ", ".join(
                    [author.name for author in paper.authors]
                )

                st.write(f"**👨‍🔬 Authors:** {authors}")

                st.write(
                    f"**📅 Published:** "
                    f"{paper.published.strftime('%d %b %Y')}"
                )

                with st.expander("📖 View Abstract"):
                    st.write(paper.summary)

                with st.spinner("Generating AI summary..."):
                    summary = summarize_paper(
                        paper.title,
                        paper.summary,
                        model
                    )

                st.markdown("### 🧠 AI Summary")
                st.markdown(summary)

                st.markdown(
                    f"📥 [Download PDF]({paper.pdf_url})"
                )

# ---------------------------------------------------
# Footer
# ---------------------------------------------------
st.markdown("---")
st.caption(
    "Built with Streamlit, arXiv API, and OpenRouter AI"
)
