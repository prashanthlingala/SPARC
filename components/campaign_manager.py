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
        self.tones = [
            "Professional",
            "Conversational",
            "Technical",
            "Casual",
            "Enthusiastic",
            "Authoritative"
        ]
        
    def create_campaign_form(self, personas: List[Dict]) -> Optional[Dict]:
        """Create form for campaign settings"""
        st.subheader("Campaign Settings")
        
        if not personas:
            st.error("Please create at least one persona first")
            return None
        
        with st.form("campaign_form"):
            campaign_goal = st.text_area(
                "Campaign Goal",
                placeholder="e.g., Increase awareness of our new product features"
            )
            
            selected_personas = st.multiselect(
                "Target Persona",
                options=[p["role"] for p in personas],
                help="Select the target persona for this campaign"
            )
            
            content_type = st.selectbox(
                "Content Type",
                self.content_types
            )
            
            tone = st.selectbox(
                "Content Tone",
                self.tones
            )
            
            hashtags = st.text_input(
                "Hashtags",
                placeholder="e.g., #AI, #Innovation (comma separated)"
            )
            
            keywords = st.text_input(
                "Keywords",
                placeholder="Enter keywords (comma separated)"
            )
            
            submitted = st.form_submit_button("🎯 Generate Content", type="primary")
            
            if submitted:
                if not campaign_goal:
                    st.error("Please enter a campaign goal")
                    return None
                elif not selected_personas:
                    st.error("Please select at least one persona")
                    return None
                else:
                    return {
                        "campaign_goal": campaign_goal,
                        "personas": [p for p in personas if p["role"] in selected_personas],
                        "hashtags": [tag.strip() for tag in hashtags.split(",") if tag],
                        "keywords": [kw.strip() for kw in keywords.split(",") if kw],
                        "content_type": content_type,
                        "tone": tone
                    }
        return None 