import streamlit as st
import openai
import requests
from typing import List

# ---- SETUP ----
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Store securely in Streamlit Secrets

st.title("🔍 AI Research Agent: Literature Review Generator")
st.write("Enter a research topic below. The agent will search papers, summarize, cluster, and generate a literature review.")

# ---- INPUT ----
topic = st.text_input("Enter your research topic:", "AI for climate modeling")
submit = st.button("Generate Literature Review")

# ---- FUNCTIONS ----
def search_papers(query: str, max_results=5) -> List[str]:
    # Dummy paper titles for now; in production use arXiv or Semantic Scholar API
    return [
        f"Recent Advances in {query} Using Deep Learning",
        f"A Survey on {query} Applications",
        f"Transformer Models Applied to {query}",
        f"Satellite Data Fusion in {query}",
        f"Challenges in {query} Forecasting with AI"
    ]

def summarize_paper(title: str) -> str:
    prompt = f"""
    Summarize the following research paper title in 3-4 sentences:
    Title: {title}
    Provide a concise summary highlighting methods, results, and relevance.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def synthesize_review(summaries: List[str], topic: str) -> str:
    joined = "\n\n".join(summaries)
    prompt = f"""
    Create a literature review on the topic: {topic}.
    Use the following paper summaries:
    {joined}

    Write a structured review with Introduction, Thematic Summary, and Conclusion.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# ---- MAIN LOGIC ----
if submit:
    with st.spinner("🔎 Searching papers and generating summaries..."):
        papers = search_papers(topic)
        summaries = [summarize_paper(title) for title in papers]

    st.success("Summaries generated. Creating literature review...")

    with st.spinner("🧠 Writing the review..."):
        review = synthesize_review(summaries, topic)

    st.subheader("📄 Literature Review")
    st.markdown(review)

    st.subheader("📚 Sources")
    for paper in papers:
        st.markdown(f"- {paper}")
