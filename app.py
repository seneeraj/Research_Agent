import streamlit as st
import openai
import arxiv
import time

# Initialize OpenRouter API key from Streamlit secrets
client = openai.OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

def search_papers(topic, max_results=5):
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    results = []
    for result in search.results():
        results.append(result.title)
    return results

def summarize_paper(title):
    prompt = f"Please summarize the main contributions and findings of a research paper titled: '{title}' in simple terms."
    try:
        response = client.chat.completions.create(
            model="openrouter/openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"Error summarizing: {str(e)}"

def synthesize_review(summaries, topic):
    joined_summaries = "\n\n".join(summaries)
    prompt = (
        f"Based on the following paper summaries about '{topic}', write a synthesized literature review suitable for a beginner researcher.\n\n"
        f"{joined_summaries}"
    )
    try:
        response = client.chat.completions.create(
            model="openrouter/openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        review = response.choices[0].message.content.strip()
        return review
    except Exception as e:
        return f"Error generating review: {str(e)}"

# Streamlit app UI
st.set_page_config(page_title="Research Review Agent", layout="centered")
st.title("🧠 AI Research Review Agent")
st.write("Enter a research topic below and get a literature review synthesized from recent papers.")

topic = st.text_input("🔍 Enter your research topic:", "Large Language Models")

if st.button("Generate Review"):
    if not topic.strip():
        st.warning("Please enter a valid topic.")
    else:
        with st.spinner("🔎 Searching and analyzing papers..."):
            papers = search_papers(topic)
            summaries = []
            for title in papers:
                summary = summarize_paper(title)
                summaries.append(summary)
                time.sleep(2)  # Be kind to API limits

            review = synthesize_review(summaries, topic)

        st.subheader("📝 Synthesized Literature Review")
        st.markdown(review)

        st.subheader("📚 Paper Titles Summarized")
        for i, title in enumerate(papers):
            st.markdown(f"**{i+1}. {title}**")
            st.markdown(summaries[i])
