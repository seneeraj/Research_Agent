import streamlit as st
import openai
import arxiv

# --- Load API Key from Streamlit Secrets ---
client = openai.OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

st.set_page_config(page_title="📚 Research Agent", layout="wide")

st.title("🧠 AI Research Agent")
st.write("Search academic papers on a topic and generate a synthesized literature review using LLMs.")

# --- User Input ---
topic = st.text_input("Enter a research topic:", value="Multilingual Large Language Models")

model = st.selectbox("Choose a model (OpenRouter)", [
    "openai/gpt-3.5-turbo",
    "mistralai/mixtral-8x7b",
    "google/gemini-pro",
    "meta-llama/llama-3-8b-instruct"
])

num_papers = st.slider("Number of papers to summarize:", 1, 10, 5)

# --- Search arXiv ---
@st.cache_data(show_spinner=False)
def search_arxiv(topic, max_results):
    search = arxiv.Search(query=topic, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    return list(search.results())

# --- Summarize Each Paper ---
def summarize_paper(title, model):
    prompt = f"Summarize the main contributions of the paper titled '{title}' in plain English."
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing: {e}"

# --- Combine Summaries into a Review ---
def synthesize_review(summaries, topic, model):
    joined = "\n\n".join(summaries)
    prompt = f"Based on the following summaries of academic papers on the topic '{topic}', generate a clear and concise literature review:\n\n{joined}"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating review: {e}"

# --- Run App ---
if st.button("🔍 Search & Summarize"):
    with st.spinner("🔎 Searching papers..."):
        papers = search_arxiv(topic, num_papers)

    with st.spinner("✍️ Summarizing papers..."):
        summaries = [summarize_paper(paper.title, model) for paper in papers]

    with st.spinner("🧠 Synthesizing literature review..."):
        review = synthesize_review(summaries, topic, model)

    st.subheader("📝 Synthesized Literature Review")
    st.write(review)

    st.subheader("📚 Paper Titles Summarized")
    for i, paper in enumerate(papers):
        st.markdown(f"**{i+1}. {paper.title}**")
        st.markdown(summaries[i])
