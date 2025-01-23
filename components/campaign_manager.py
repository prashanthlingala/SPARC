import streamlit as st
from typing import Dict, Optional, List

class CampaignManager:
    def __init__(self):
        self.content_types = [
            "Leadership Content",
            "Product Deep Dives",
            "Customer Stories",
            "Technical Documentation"
        ]
        
    def create_campaign_form(self, personas: list) -> Optional[Dict]:
        """Display form for creating a new campaign"""
        st.subheader("Campaign Setup")
        
        with st.form("campaign_form"):
            campaign_goal = st.text_area(
                "Campaign Goal",
                placeholder="What do you want to achieve with this campaign?"
            )
            
            selected_persona = st.selectbox(
                "Select Target Persona",
                options=[p["role"] for p in personas],
                format_func=lambda x: f"Persona: {x}"
            ) if personas else st.error("Please create a persona first")
            
            hashtags = st.text_input(
                "Campaign Hashtags",
                placeholder="Enter hashtags separated by commas"
            )
            
            keywords = st.text_input(
                "Keywords",
                placeholder="Enter keywords separated by commas"
            )
            
            content_type = st.selectbox(
                "Content Type",
                options=self.content_types
            )
            
            tone = st.select_slider(
                "Content Tone",
                options=["Technical", "Professional", "Conversational", "Casual"]
            )
            
            submitted = st.form_submit_button("Generate Content")
            
            if submitted and campaign_goal and selected_persona:
                return {
                    "campaign_goal": campaign_goal,
                    "persona": next(p for p in personas if p["role"] == selected_persona),
                    "hashtags": [tag.strip() for tag in hashtags.split(",") if tag],
                    "keywords": [kw.strip() for kw in keywords.split(",") if kw],
                    "content_type": content_type,
                    "tone": tone
                }
        return None 