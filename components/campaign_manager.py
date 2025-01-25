import streamlit as st
from typing import Dict, Optional, List
from utils.database import Database

class CampaignManager:
    def __init__(self):
        self.db = Database()
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
        # Sample trending hashtags (you can replace this with an API call)
        self.trending_hashtags = [
            "#DataScience",
            "#AI",
            "#MachineLearning",
            "#BigData",
            "#Analytics",
            "#Tech",
            "#Innovation",
            "#DigitalTransformation",
            "#CloudComputing",
            "#Programming"
        ]
        # Sample SEO keywords (you can replace this with an API integration)
        self.seo_keywords = [
            "artificial intelligence",
            "machine learning",
            "data analytics",
            "business intelligence",
            "cloud computing",
            "digital transformation",
            "data science",
            "big data",
            "predictive analytics",
            "automation"
        ]
        
    def create_campaign_form(self, personas: List[Dict]) -> Optional[Dict]:
        """Create form for campaign settings"""
        st.subheader("Campaign Settings")
        
        if not personas:
            st.error("Please create at least one persona first")
            return None
        
        with st.form("campaign_form"):
            campaign_name = st.text_input(
                "Campaign Name",
                placeholder="e.g., Q1 Product Launch"
            )
            
            campaign_goal = st.text_area(
                "Campaign Goal",
                placeholder="e.g., Increase awareness of our new product features"
            )
            
            selected_persona = st.selectbox(
                "Target Persona",
                options=personas,
                format_func=lambda x: x['name'],
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

            # Hashtags section with suggestions
            st.subheader("📊 Hashtags")
            col1, col2 = st.columns([2, 1])
            with col1:
                hashtags = st.multiselect(
                    "Select or Enter Hashtags",
                    options=self.trending_hashtags,
                    default=[],
                    help="Choose from trending hashtags or enter your own"
                )
            with col2:
                custom_hashtag = st.text_input(
                    "Add Custom Hashtag",
                    placeholder="#YourHashtag",
                    help="Enter without # to add multiple (comma-separated)"
                )
                if custom_hashtag:
                    custom_tags = [f"#{tag.strip('#').strip()}" for tag in custom_hashtag.split(',')]
                    hashtags.extend(custom_tags)

            # Keywords section with suggestions
            st.subheader("🎯 SEO Keywords")
            col1, col2 = st.columns([2, 1])
            with col1:
                keywords = st.multiselect(
                    "Select or Enter Keywords",
                    options=self.seo_keywords,
                    default=[],
                    help="Choose from suggested SEO keywords or enter your own"
                )
            with col2:
                custom_keyword = st.text_input(
                    "Add Custom Keywords",
                    placeholder="Your keyword",
                    help="Enter comma-separated keywords"
                )
                if custom_keyword:
                    custom_keys = [k.strip() for k in custom_keyword.split(',')]
                    keywords.extend(custom_keys)

            submitted = st.form_submit_button("🎯 Generate Content", type="primary")
            
            if submitted:
                if not campaign_name or not campaign_goal:
                    st.error("Please fill in all required fields")
                    return None
                
                # Save campaign to database
                campaign = {
                    "name": campaign_name,
                    "goal": campaign_goal,
                    "status": "draft"
                }
                campaign_id = self.db.save_campaign(campaign)
                
                return {
                    "id": campaign_id,
                    "name": campaign_name,
                    "campaign_goal": campaign_goal,
                    "persona": selected_persona,
                    "content_type": content_type,
                    "tone": tone,
                    "hashtags": list(set(hashtags)),  # Remove duplicates
                    "keywords": list(set(keywords))   # Remove duplicates
                }
        return None

    def save_generated_content(self, campaign_id: int, content_data: Dict) -> Dict:
        """Save generated content to database"""
        data = {
            "campaign_id": campaign_id,
            "persona_id": content_data["persona"]["id"],
            "content_type": content_data["content_type"],
            "tone": content_data["tone"],
            "content": content_data["content"],
            "hashtags": content_data.get("hashtags", []),  # Add hashtags
            "keywords": content_data.get("keywords", [])   # Add keywords
        }
        content_id = self.db.save_generated_content(data)
        return {"id": content_id, **data}

    def get_campaign_content(self, campaign_id: int) -> List[Dict]:
        """Get all content for a campaign"""
        return self.db.get_campaign_content(campaign_id)

    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns"""
        return self.db.get_campaigns()

    def display_campaign_history(self):
        """Display campaign history"""
        campaigns = self.get_all_campaigns()
        
        if not campaigns:
            st.info("No campaigns created yet")
            return
        
        for campaign in campaigns:
            with st.expander(f"Campaign: {campaign['name']}"):
                st.write(f"**Goal:** {campaign['goal']}")
                st.write(f"**Status:** {campaign['status']}")
                
                content_list = self.get_campaign_content(campaign['id'])
                if content_list:
                    for content in content_list:
                        st.write(f"**Content Type:** {content['content_type']}")
                        st.write(f"**Tone:** {content['tone']}")
                        st.write("**Generated Content:**")
                        st.markdown(content['content'])
                else:
                    st.info("No content generated yet for this campaign")

    def update_content(self, content_id: int, updates: Dict) -> bool:
        """Update content in the database"""
        return self.db.update_content(content_id, updates) 