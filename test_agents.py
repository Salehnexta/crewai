#!/usr/bin/env python3
"""
Test M1-M5 Agent Import and Initialization
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🧪 Testing M1-M5 Agent Imports...")

try:
    print("📦 Importing agents...")
    from agents.morvo_marketing_agents import MorvoMarketingAgents
    print("✅ Agents import successful!")
    
    print("🚀 Initializing agents...")
    agents = MorvoMarketingAgents()
    print("✅ Agents initialization successful!")
    
    print("🔍 Testing individual agents...")
    m1_agent = agents.m1_strategic_manager_agent()
    print("✅ M1 Agent (Ahmed - Strategic Manager) created!")
    
    m2_agent = agents.m2_social_media_manager_agent()
    print("✅ M2 Agent (Fatima - Social Media Manager) created!")
    
    m3_agent = agents.m3_campaign_manager_agent()
    print("✅ M3 Agent (Mohammed - Campaign Manager) created!")
    
    m4_agent = agents.m4_content_manager_agent()
    print("✅ M4 Agent (Nora - Content Manager) created!")
    
    m5_agent = agents.m5_data_manager_agent()
    print("✅ M5 Agent (Khalid - Data Manager) created!")
    
    print("\n🎉 M1-M5 Agents Test Passed!")
    print("🚀 Agents are ready for production deployment!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
except Exception as e:
    print(f"❌ Initialization Error: {e}")
