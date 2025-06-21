# debug_test.py
# Run this script to identify the specific error
# Usage: python debug_test.py

import sys
print(f"Python version: {sys.version}")
print("="*50)

# Test imports one by one
print("Testing imports...")

try:
    import streamlit as st
    print("✅ streamlit imported successfully")
    print(f"   Streamlit version: {st.__version__}")
except ImportError as e:
    print(f"❌ streamlit import failed: {e}")

try:
    import crewai
    print("✅ crewai imported successfully")
    print(f"   CrewAI version: {crewai.__version__}")
except ImportError as e:
    print(f"❌ crewai import failed: {e}")

try:
    from crewai import Agent, Task, Crew, Process
    print("✅ crewai core components imported successfully")
except ImportError as e:
    print(f"❌ crewai core components import failed: {e}")

try:
    from crewai import LLM
    print("✅ crewai LLM imported successfully")
except ImportError as e:
    print(f"❌ crewai LLM import failed: {e}")
    try:
        from langchain_community.llms import LLM
        print("✅ LLM imported from langchain_community")
    except ImportError as e2:
        print(f"❌ LLM import from langchain_community also failed: {e2}")

try:
    import crewai_tools
    print("✅ crewai_tools imported successfully")
except ImportError as e:
    print(f"❌ crewai_tools import failed: {e}")

try:
    from crewai_tools import SerperDevTool
    print("✅ SerperDevTool imported successfully")
except ImportError as e:
    print(f"❌ SerperDevTool import failed: {e}")

print("="*50)
print("Environment variables check:")

import os
clarifai_pat = os.getenv("CLARIFAI_PAT")
serper_key = os.getenv("SERPER_API_KEY")

if clarifai_pat:
    print(f"✅ CLARIFAI_PAT is set (length: {len(clarifai_pat)})")
else:
    print("❌ CLARIFAI_PAT is not set")

if serper_key:
    print(f"✅ SERPER_API_KEY is set (length: {len(serper_key)})")
else:
    print("❌ SERPER_API_KEY is not set")

print("="*50)
print("Basic functionality test:")

if clarifai_pat and serper_key:
    try:
        from crewai import LLM
        from crewai_tools import SerperDevTool
        
        print("Testing LLM initialization...")
        llm = LLM(
            model="meta/llama-3_1-8b-instruct",
            api_key=clarifai_pat
        )
        print("✅ LLM initialization successful")
        
        print("Testing SerperDevTool initialization...")
        search_tool = SerperDevTool(api_key=serper_key)
        print("✅ SerperDevTool initialization successful")
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
else:
    print("⚠️ Skipping functionality test - missing API keys")

print("="*50)
print("Test completed!")
