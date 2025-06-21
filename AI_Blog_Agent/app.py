import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from datetime import datetime

# Environment variables
CLARIFAI_PAT = os.getenv("CLARIFAI_PAT")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Validate environment variables
if not CLARIFAI_PAT:
    st.error("Please set CLARIFAI_PAT environment variable")
    st.stop()

if not SERPER_API_KEY:
    st.error("Please set SERPER_API_KEY environment variable")
    st.stop()

# Configure Clarifai LLM (moved inside function to enable model switching)
def get_clarifai_llm(model_name="gcp/generate/models/gemini-2_5-pro"):
    return LLM(
        model=model_name,
        api_key=CLARIFAI_PAT,
        base_url="https://api.clarifai.com/v2/ext/openai/v1"
    )

# Initialize tools
search_tool = SerperDevTool()

# Define Agents (updated with enhanced descriptions)
def create_agents(model_name):
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Uncover cutting-edge developments and facts on a given topic",
        backstory="""Expert research analyst at a tech think tank with 10+ years experience. 
        Specializes in identifying emerging trends, gathering verified information, 
        and presenting actionable insights with academic rigor.""",
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
        llm=get_clarifai_llm(model_name)
    )

    writer = Agent(
        role="Tech Content Strategist",
        goal="Craft compelling blog posts on technical topics",
        backstory="""Award-winning content strategist with 15+ industry awards. 
        Transforms complex technical concepts into engaging narratives for tech-savvy audiences
        while maintaining factual accuracy and readability.""",
        verbose=True,
        allow_delegation=True,
        llm=get_clarifai_llm(model_name)
    )
    return researcher, writer

# Task creation with improved instructions
def create_tasks(topic, researcher, writer):
    research_task = Task(
        description=f"""Conduct comprehensive analysis of '{topic}'. 
        Identify: 
        - Key trends and breakthrough technologies 
        - Major players and institutions 
        - Potential industry impacts
        - Verified sources and data points""",
        expected_output="Detailed analysis report with bullet points and sources",
        agent=researcher
    )

    writing_task = Task(
        description=f"""Using research on '{topic}', develop an engaging blog post with:
        - Compelling headline
        - Clear introduction
        - 3-5 body paragraphs with supporting evidence
        - Conclusion with future outlook
        - Accessible language with technical terms explained
        Format requirements:
        # Title
        ## Section headers
        **Bold** for emphasis
        - Bullet points where appropriate
        > Blockquotes for important insights
        NO code blocks or triple backticks""",
        expected_output="4-5 paragraph blog post in clean markdown",
        agent=writer,
        context=[research_task]
    )
    return research_task, writing_task

# Enhanced execution with caching
@st.cache_data(ttl=3600, show_spinner=False)
def run_blog_generation(topic, model_name):
    researcher, writer = create_agents(model_name)
    research_task, writing_task = create_tasks(topic, researcher, writer)
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=1
    )
    return crew.kickoff()

# Streamlit App with UI improvements
def main():
    st.set_page_config(page_title="AI Blog Writer", page_icon="✍️")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        model_name = st.selectbox(
            "Clarifai Model",
            options=["gcp/generate/models/gemini-2_5-pro", "gcp/generate/models/gemini-2_0-pro"],
            index=0
        )
        st.divider()
        st.caption(f"Environment: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    st.title("✍️ AI Blog Writing Agent")
    st.markdown("*Powered by Clarifai & CrewAI*")

    with st.expander("How it works"):
        st.markdown("""
        - **Researcher Agent**: Gathers verified information from web sources
        - **Writer Agent**: Creates structured blog content
        - **Clarifai**: Uses `{model_name.split('/')[-1]}` model for AI processing
        """)

    topic = st.text_input(
        "Enter blog topic:",
        placeholder="e.g., Quantum Computing in Healthcare",
        help="Specific topics yield better results"
    )

    if st.button("🚀 Generate Blog", disabled=not topic.strip(), type="primary"):
        with st.status("🧠 Generating content...", expanded=True) as status:
            st.write("1. Researching topic...")
            st.write("2. Analyzing findings...")
            st.write("3. Writing blog post...")
            
            try:
                result = run_blog_generation(topic, model_name)
                status.update(label="✅ Blog generated!", state="complete")
                
                st.markdown("---")
                st.subheader("Generated Content")
                st.markdown(result)
                
                st.download_button(
                    "📥 Download Markdown",
                    data=result,
                    file_name=f"{topic.replace(' ', '_')[:30]}_blog.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
