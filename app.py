import streamlit as st
import openai
import arxiv
from openai import OpenAI
import os

# Load OpenRouter API key securely from Streamlit secrets
api_key = st.secrets["OPENROUTER_API_KEY"]

# Initialize OpenAI client with OpenRouter base
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

st.title("🔬 Research Agent - Literature Review Generator")

# Step 1: Get Research Topic
topic = st.text_input("Enter your research topic:", "")

# Step 2: Choose Model
st.markdown("💡 Currently only tested models are shown below. You can add others once verified.")
model = st.selectbox("Choose an OpenRouter-supported model", [
    "meta-llama/llama-3-8b-instruct",
    "meta-llama/llama-2-70b-chat"
])

# Function to search papers using arXiv
def search_papers(topic):
    search = arxiv.Search(
        query=topic,
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance
    )
    return [result.title for result in search.results()]

# Function to summarize a paper using the selected model
def summarize_paper(title):
    prompt = f"Summarize this research paper title in 3-4 bullet points, avoiding repetition:\n\n'{title}'"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error summarizing: {e}"

# Function to generate a synthesized review
def synthesize_review(summaries, topic):
    joined = "\n\n".join(summaries)
    prompt = f"You are an AI researcher. Write a 300-word literature review about this topic: **{topic}**, using the following summaries:\n\n{joined}"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error generating review: {e}"

if st.button("🔍 Generate Literature Review"):
    if topic:
        with st.spinner("Searching for papers and generating summaries..."):
            papers = search_papers(topic)
            summaries = [summarize_paper(title) for title in papers]
            review = synthesize_review(summaries, topic)

        st.subheader("📝 Synthesized Literature Review")
        st.write(review)

        st.subheader("📚 Paper Titles Summarized")
        for i, (title, summary) in enumerate(zip(papers, summaries), 1):
            st.markdown(f"**{i}. {title}**")
            st.write(summary)
    else:
        st.warning("Please enter a topic.")
