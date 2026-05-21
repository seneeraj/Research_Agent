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
    "Search research papers from arXiv and get AI-generated summaries."
)

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
st.sidebar.header("🔧 Options")

model = st.sidebar.selectbox(
    "Choose AI Model",
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
# Supported Research Topics
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
        "ai ethics",
        "artificial intelligence"
    ],

    "Cybersecurity": [
        "malware detection",
        "network security",
        "phishing",
        "cyber attacks",
        "cryptography",
        "cybersecurity"
    ],

    "Healthcare AI": [
        "medical imaging",
        "cancer detection",
        "drug discovery",
        "healthcare analytics",
        "healthcare ai"
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
# Show Supported Topics
# ---------------------------------------------------
with st.expander("📚 Supported Research Topics"):

    for category, keywords in SUPPORTED_TOPICS.items():

        st.markdown(f"### {category}")

        st.write(", ".join(keywords))

# ---------------------------------------------------
# Search Input
# ---------------------------------------------------
topic = st.text_input(
    "Enter your research topic",
    value="ethics in AI"
)

search_button = st.button("🔍 Search Papers")

# ---------------------------------------------------
# Validate Topic
# ---------------------------------------------------
def is_topic_supported(user_topic):

    user_topic = user_topic.lower().strip()

    for category, keywords in SUPPORTED_TOPICS.items():

        for keyword in keywords:

            if keyword in user_topic:
                return True

    return False

# ---------------------------------------------------
# Search arXiv Papers
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
# Summarize Paper using OpenRouter
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

        if response.status_code != 200:

            return (
                f"❌ API Error ({response.status_code}): "
                f"{response.text}"
            )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:

            return data["choices"][0]["message"]["content"]

        return "❌ No summary returned from AI model."

    except requests.exceptions.Timeout:

        return "❌ Request timed out."

    except Exception as e:

        return f"❌ Error summarizing paper: {str(e)}"

# ---------------------------------------------------
# Main Execution
# ---------------------------------------------------
if search_button:

    # Empty topic validation
    if not topic.strip():

        st.warning("⚠ Please enter a research topic.")

        st.stop()

    # Scope validation
    if not is_topic_supported(topic):

        st.error(
            "❌ This topic is currently out of scope for this application."
        )

        st.info(
            "Please search within supported research domains listed below."
        )

        st.subheader("📚 Supported Topics")

        for category, keywords in SUPPORTED_TOPICS.items():

            st.markdown(f"### {category}")

            st.write(", ".join(keywords))

        st.stop()

    # Search status
    st.info(
        f"🔎 Searching for papers related to: **{topic}**"
    )

    # Fetch papers
    with st.spinner("Fetching papers from arXiv..."):

        papers = search_arxiv_papers(topic, max_results)

    # No papers found
    if not papers:

        st.warning(
            "⚠ No papers found on arXiv for this topic."
        )

    # Display results
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
