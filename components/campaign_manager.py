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
        # Default hashtag suggestions
        self.suggested_hashtags = [
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
        # Default keyword suggestions
        self.suggested_keywords = [
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
        
        # Add industries list
        self.industries = [
            "Business Services",
            "Entertainment & Media",
            "Financial Services",
            "Healthcare & Life Sciences",
            "Industrial & Manufacturing",
            "Insurance",
            "Logistics & Supply Chain",
            "Non-Profit",
            "Public Sector",
            "Technology",
            "Retail & CPG",
            "Education",
            "Telecommunications",
            "Energy & Utilities",
            "Real Estate",
            "Professional Services"
        ]
        
        # Initialize industries in session state if not exists
        if 'selected_industries' not in st.session_state:
            st.session_state.selected_industries = []
        if 'suggested_industries' not in st.session_state:
            st.session_state.suggested_industries = self.industries.copy()

    def create_campaign_form(self, personas: List[Dict]) -> Optional[Dict]:
        """Create form for campaign settings"""
        st.subheader("Campaign Settings")
        st.markdown("Fields marked with * are mandatory")
        
        if not personas:
            st.error("Please create at least one persona first")
            return None

        # Initialize session state
        if 'selected_hashtags' not in st.session_state:
            st.session_state.selected_hashtags = []
        if 'selected_keywords' not in st.session_state:
            st.session_state.selected_keywords = []
        if 'suggested_hashtags' not in st.session_state:
            st.session_state.suggested_hashtags = self.suggested_hashtags.copy()
        if 'suggested_keywords' not in st.session_state:
            st.session_state.suggested_keywords = self.suggested_keywords.copy()
        if 'selected_industries' not in st.session_state:
            st.session_state.selected_industries = []
        if 'suggested_industries' not in st.session_state:
            st.session_state.suggested_industries = self.industries.copy()

        # Custom industry form
        with st.form(key="industry_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                custom_industry = st.text_input(
                    "Add Custom Industry",
                    placeholder="Enter industry name",
                    help="Enter comma-separated industries",
                    key="industry_input"
                )
            with col2:
                add_industry = st.form_submit_button("➕ Add Industry")
                if add_industry and custom_industry:
                    # Process custom industries
                    for industry in custom_industry.split(','):
                        industry = industry.strip().title()  # Capitalize each word
                        if industry:
                            if industry not in st.session_state.suggested_industries:
                                st.session_state.suggested_industries.append(industry)
                            if industry not in st.session_state.selected_industries:
                                st.session_state.selected_industries.append(industry)
                    st.rerun()

        # Custom hashtag form
        with st.form(key="hashtag_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                custom_hashtag = st.text_input(
                    "Add Custom Hashtags",
                    placeholder="#YourHashtag",
                    help="Enter without # to add multiple (comma-separated)",
                    key="hashtag_input"
                )
            with col2:
                add_hashtag = st.form_submit_button("➕ Add Hashtag")
                if add_hashtag and custom_hashtag:
                    # Process custom hashtags
                    for tag in custom_hashtag.split(','):
                        tag = tag.strip().strip('#')
                        if tag:
                            tag = f"#{tag}" if not tag.startswith('#') else tag
                            if tag not in st.session_state.suggested_hashtags:
                                st.session_state.suggested_hashtags.append(tag)
                            if tag not in st.session_state.selected_hashtags:
                                st.session_state.selected_hashtags.append(tag)
                    st.rerun()

        # Custom keyword form
        with st.form(key="keyword_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                custom_keyword = st.text_input(
                    "Add Custom Keywords",
                    placeholder="Your keyword",
                    help="Enter comma-separated keywords",
                    key="keyword_input"
                )
            with col2:
                add_keyword = st.form_submit_button("➕ Add Keyword")
                if add_keyword and custom_keyword:
                    # Process custom keywords
                    for key in custom_keyword.split(','):
                        key = key.strip().lower()
                        if key:
                            if key not in st.session_state.suggested_keywords:
                                st.session_state.suggested_keywords.append(key)
                            if key not in st.session_state.selected_keywords:
                                st.session_state.selected_keywords.append(key)
                    st.rerun()

        # Main campaign form
        with st.form("campaign_form"):
            campaign_name = st.text_input(
                "Campaign Name *",
                placeholder="e.g., Q1 Product Launch"
            )
            
            campaign_goal = st.text_area(
                "Campaign Goal *",
                placeholder="e.g., Increase awareness of our new product features"
            )
            
            # Industry selection
            st.subheader("Additional Information")
            selected_industries = st.multiselect(
                "Select Industries *",
                options=st.session_state.suggested_industries,
                default=[i for i in st.session_state.selected_industries if i in st.session_state.suggested_industries],
                help="Choose target industries for your campaign"
            )

            selected_persona = st.selectbox(
                "Target Persona *",
                options=personas,
                format_func=lambda x: x['name'],
                help="Select the target persona for this campaign"
            )
            
            content_type = st.selectbox(
                "Content Type *",
                self.content_types
            )
            
            tone = st.selectbox(
                "Content Tone *",
                self.tones
            )

            # Hashtags selection
            st.subheader("📊 Hashtags")
            selected_hashtags = st.multiselect(
                "Select or Enter Hashtags",
                options=st.session_state.suggested_hashtags,
                default=[h for h in st.session_state.selected_hashtags if h in st.session_state.suggested_hashtags],
                help="Choose from suggested hashtags or add custom ones"
            )

            # Keywords selection
            st.subheader("🎯 SEO Keywords")
            selected_keywords = st.multiselect(
                "Select or Enter Keywords",
                options=st.session_state.suggested_keywords,
                default=[k for k in st.session_state.selected_keywords if k in st.session_state.suggested_keywords],
                help="Choose from suggested SEO keywords or add your own"
            )

            # Generate content button
            submitted = st.form_submit_button("🎯 Generate Content", type="primary")
            
            if submitted:
                if not campaign_name or not campaign_goal or not selected_industries:
                    st.error("Please fill in all required fields including target industries")
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
                    "industries": selected_industries,
                    "persona": selected_persona,
                    "content_type": content_type,
                    "tone": tone,
                    "hashtags": selected_hashtags,
                    "keywords": selected_keywords
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

    def show_content_manager(self):
        """Enhanced content management interface"""
        st.header("📚 Content Manager")
        
        # Use spinner while loading data
        with st.spinner("Loading campaigns..."):
            # Get all campaigns with their content
            campaigns = self.get_all_campaigns_with_content()
            
            if not campaigns:
                st.info("No content has been generated yet.")
                return

            # Create tabs for better organization
            tab_labels = [f"{campaign['name']} ({campaign['created_at'][:10]})" for campaign in campaigns]
            tabs = st.tabs(tab_labels)
            
            # Render each campaign in its own tab
            for tab, campaign in zip(tabs, campaigns):
                with tab:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Goal:** {campaign['goal']}")
                    with col2:
                        st.markdown(f"**Status:** {campaign['status']}")
                    
                    if campaign.get('content'):
                        for content in campaign['content']:
                            with st.expander(
                                f"📄 {content['content_type']} - {content['created_at'][:10]}", 
                                expanded=False
                            ):
                                content_tabs = st.tabs(["✍️ Content", "🐦 Twitter", "📧 Email"])
                                
                                with content_tabs[0]:
                                    st.markdown("##### Content Details")
                                    st.markdown(f"**Type:** {content['content_type']}")
                                    st.markdown(f"**Tone:** {content['tone']}")
                                    
                                    edited_content = st.text_area(
                                        "Edit Content",
                                        value=content['content'],
                                        height=200,
                                        key=f"content_{content['id']}"
                                    )
                                    if st.button("💾 Save Changes", key=f"save_{content['id']}"):
                                        if self.update_content(content['id'], {'content': edited_content}):
                                            st.success("Content updated!")
                                
                                with content_tabs[1]:
                                    twitter_content = content.get('twitter_content', '')
                                    edited_twitter = st.text_area(
                                        "Twitter Content",
                                        value=twitter_content,
                                        height=100,
                                        key=f"twitter_{content['id']}"
                                    )
                                    st.write(f"Character count: {len(edited_twitter)}/280")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("💾 Save", key=f"save_twitter_{content['id']}"):
                                            if self.update_content(content['id'], {'twitter_content': edited_twitter}):
                                                st.success("Saved!")
                                    with col2:
                                        if st.button("🐦 Post", key=f"post_{content['id']}"):
                                            st.info("Twitter posting functionality here")
                                
                                with content_tabs[2]:
                                    email_subject = content.get('email_subject', '')
                                    email_body = content.get('email_body', '')
                                    
                                    edited_subject = st.text_input(
                                        "Subject",
                                        value=email_subject,
                                        key=f"subject_{content['id']}"
                                    )
                                    edited_body = st.text_area(
                                        "Email Body",
                                        value=email_body,
                                        height=200,
                                        key=f"email_{content['id']}"
                                    )
                                    
                                    if st.button("💾 Save Email", key=f"save_email_{content['id']}"):
                                        updates = {
                                            'email_subject': edited_subject,
                                            'email_body': edited_body
                                        }
                                        if self.update_content(content['id'], updates):
                                            st.success("Email content saved!")
                    else:
                        st.info("No content generated for this campaign yet.")

    def get_all_campaigns_with_content(self) -> List[Dict]:
        """Get all campaigns with their content in a single query"""
        return self.db.get_campaigns_with_content() 