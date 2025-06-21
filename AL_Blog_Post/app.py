import streamlit as st
import os
import sys
from datetime import datetime

# Add error handling for imports
def check_and_install_packages():
    """Check if required packages are installed"""
    required_packages = {
        'crewai': 'crewai',
        'crewai_tools': 'crewai-tools',
    }
    
    missing_packages = []
    for package, install_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(install_name)
    
    if missing_packages:
        st.error(f"Missing required packages: {', '.join(missing_packages)}")
        st.code(f"pip install {' '.join(missing_packages)}")
        st.stop()

# Check packages first
check_and_install_packages()

# Now import the packages
try:
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai_tools import SerperDevTool
except ImportError as e:
    st.error(f"Import error: {str(e)}")
    st.info("Try upgrading CrewAI: `pip install --upgrade crewai crewai-tools`")
    st.stop()

def main():
    st.set_page_config(page_title="AI Blog Writer", page_icon="✍️")
    
    st.title("✍️ AI Blog Writing Agent")
    st.markdown("*Powered by Clarifai & CrewAI*")
    
    # Environment variables check
    with st.expander("🔧 Environment Setup", expanded=True):
        st.markdown("**Required Environment Variables:**")
        
        clarifai_pat = st.text_input(
            "CLARIFAI_PAT", 
            value=os.getenv("CLARIFAI_PAT", ""),
            type="password",
            help="Your Clarifai Personal Access Token"
        )
        
        serper_key = st.text_input(
            "SERPER_API_KEY", 
            value=os.getenv("SERPER_API_KEY", ""),
            type="password", 
            help="Your Serper API Key for web search"
        )
        
        if not clarifai_pat:
            st.warning("⚠️ CLARIFAI_PAT is required")
        if not serper_key:
            st.warning("⚠️ SERPER_API_KEY is required")
            
        if clarifai_pat and serper_key:
            st.success("✅ All environment variables are set")
    
    # Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        model_name = st.selectbox(
            "Clarifai Model",
            options=[
                "meta/llama-3_1-8b-instruct",
                "meta/llama-3_1-70b-instruct", 
                "mistralai/mistral-7b-instruct-v0_2",
                "google/gemma-2b-it"
            ],
            index=0,
            help="Select the model to use"
        )
        
        st.divider()
        st.caption(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Topic input
    topic = st.text_input(
        "Enter blog topic:",
        placeholder="e.g., Artificial Intelligence in Healthcare",
        help="Be specific for better results"
    )
    
    # Generate button
    if st.button("🚀 Generate Blog", type="primary", disabled=not (topic and clarifai_pat and serper_key)):
        if not topic.strip():
            st.warning("Please enter a valid topic")
            return
            
        if not clarifai_pat or not serper_key:
            st.error("Please provide both API keys")
            return
        
        # Set environment variables for the session
        os.environ["CLARIFAI_PAT"] = clarifai_pat
        os.environ["SERPER_API_KEY"] = serper_key
        
        try:
            with st.status("🧠 Generating content...", expanded=True) as status:
                st.write("1. Initializing LLM...")
                
                # Initialize LLM
                try:
                    llm = LLM(
                        model=f"clarifai/{model_name}",
                        api_key=clarifai_pat
                    )
                    st.write("✅ LLM initialized")
                except Exception as e:
                    st.error(f"LLM initialization failed: {str(e)}")
                    st.stop()
                
                st.write("2. Setting up search tool...")
                
                # Initialize search tool
                try:
                    search_tool = SerperDevTool(api_key=serper_key)
                    st.write("✅ Search tool ready")
                except Exception as e:
                    st.error(f"Search tool initialization failed: {str(e)}")
                    st.stop()
                
                st.write("3. Creating agents...")
                
                # Create agents
                researcher = Agent(
                    role="Research Analyst",
                    goal=f"Research comprehensive information about {topic}",
                    backstory="You are an expert research analyst with deep knowledge across various domains.",
                    tools=[search_tool],
                    llm=llm,
                    verbose=False,
                    allow_delegation=False
                )
                
                writer = Agent(
                    role="Content Writer", 
                    goal=f"Write an engaging blog post about {topic}",
                    backstory="You are a skilled content writer who creates engaging and informative blog posts.",
                    llm=llm,
                    verbose=False,
                    allow_delegation=False
                )
                
                st.write("✅ Agents created")
                st.write("4. Setting up tasks...")
                
                # Create tasks
                research_task = Task(
                    description=f"Research and gather comprehensive information about {topic}. Focus on recent developments, key facts, and reliable sources.",
                    expected_output="A detailed research summary with key findings and sources",
                    agent=researcher
                )
                
                writing_task = Task(
                    description=f"Write a well-structured blog post about {topic} using the research provided. Include an engaging title, introduction, main content sections, and conclusion.",
                    expected_output="A complete blog post in markdown format with proper headings and structure",
                    agent=writer,
                    context=[research_task]
                )
                
                st.write("✅ Tasks configured")
                st.write("5. Running crew...")
                
                # Create and run crew
                crew = Crew(
                    agents=[researcher, writer],
                    tasks=[research_task, writing_task],
                    process=Process.sequential,
                    verbose=False
                )
                
                # Execute
                result = crew.kickoff()
                
                status.update(label="✅ Blog generated successfully!", state="complete")
            
            # Display results
            st.markdown("---")
            st.subheader("Generated Blog Post")
            
            # Handle different result types
            if hasattr(result, 'raw'):
                content = result.raw
            elif isinstance(result, str):
                content = result
            else:
                content = str(result)
            
            st.markdown(content)
            
            # Download option
            st.download_button(
                "📥 Download as Markdown",
                data=content,
                file_name=f"{topic.replace(' ', '_')[:30]}_blog.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            
            # Show detailed error for debugging
            with st.expander("🐛 Debug Information"):
                st.code(f"""
Error Type: {type(e).__name__}
Error Message: {str(e)}
Python Version: {sys.version}
                """)
                
                # Check package versions
                try:
                    import crewai
                    st.write(f"CrewAI Version: {crewai.__version__}")
                except:
                    st.write("CrewAI Version: Unknown")

if __name__ == "__main__":
    main()
