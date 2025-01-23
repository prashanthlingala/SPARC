# Standard library imports
import os
from typing import Dict, Optional
from datetime import datetime

# Third-party imports
import streamlit as st
from dotenv import load_dotenv

# Local imports
from components.persona_manager import PersonaManager
from components.campaign_manager import CampaignManager
from components.social_media_manager import SocialMediaManager
from components.email_service import EmailService
from components.analytics_manager import AnalyticsManager
from utils.openai_helper import ContentGenerator
from utils.config_loader import load_config
from utils.db_manager import DatabaseManager

# Must be the first Streamlit command
st.set_page_config(
    page_title="Smart Personalised Automation for Remarkable Campaigns (S.P.A.R.C)",
    page_icon="🎯",
    layout="wide"
)

class CampaignCraftAI:
    def __init__(self):
        load_dotenv()
        self.config = load_config()
        
        # Initialize session state for content history
        if 'content_history' not in st.session_state:
            st.session_state.content_history = []
        
        # Initialize state for Twitter posting
        if 'twitter_post_status' not in st.session_state:
            st.session_state.twitter_post_status = None
        if 'current_content' not in st.session_state:
            st.session_state.current_content = None
        if 'current_campaign_data' not in st.session_state:
            st.session_state.current_campaign_data = None
        if 'twitter_preview' not in st.session_state:
            st.session_state.twitter_preview = None
        
        # Initialize Azure OpenAI
        self.content_generator = ContentGenerator(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=self.config["azure_openai"]["deployment_name"],
            api_version=self.config["azure_openai"]["api_version"]
        )
        
        # Initialize components
        self.persona_manager = PersonaManager()
        self.campaign_manager = CampaignManager()
        self.social_media_manager = SocialMediaManager(self.content_generator)
        self.email_service = EmailService(
            self.config["email"]["smtp_server"],
            self.config["email"]["smtp_port"]
        )
        self.analytics_manager = AnalyticsManager()
        
    def main(self):
        st.title("Smart Personalised Automation for Remarkable Campaigns (S.P.A.R.C)")
        st.subheader("AI-Powered Marketing Campaign Content Generator")
        
        # Sidebar navigation
        with st.sidebar:
            st.header("Navigation")
            page = st.radio("Go to", ["Create Persona", "Generate Content", "Content History", "Analytics"])
        
        if page == "Create Persona":
            self.persona_manager.create_persona_form()
            
            # Display saved personas
            personas = self.persona_manager.get_personas()
            if personas:
                st.subheader("Saved Personas")
                for persona in personas:
                    st.write(f"📋 {persona['role']} ({persona['experience']})")
        
        elif page == "Generate Content":
            campaign_data = self.campaign_manager.create_campaign_form(
                self.persona_manager.get_personas()
            )
            
            if campaign_data:
                with st.spinner("Generating content..."):
                    content = self.content_generator.generate_content(
                        campaign_goal=campaign_data["campaign_goal"],
                        persona=campaign_data["personas"][0],  # Use first persona for content generation
                        content_type=campaign_data["content_type"],
                        tone=campaign_data["tone"]
                    )
                    
                    # Store current content and campaign data in session state
                    st.session_state.current_content = content
                    st.session_state.current_campaign_data = campaign_data
                    
                    # Save to content history
                    content_data = {
                        "id": len(st.session_state.content_history) + 1,
                        "campaign_goal": campaign_data["campaign_goal"],
                        "content_type": campaign_data["content_type"],
                        "tone": campaign_data["tone"],
                        "content": content,
                        "persona_roles": [p["role"] for p in campaign_data["personas"]],
                        "hashtags": campaign_data["hashtags"],
                        "tweet_url": None,  # Will be updated when posted
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.content_history.append(content_data)
                    
                    st.subheader("Generated Content")
                    st.write(content)
                    
                    # Display metadata
                    with st.expander("Campaign Details"):
                        st.write(f"**Content Type:** {campaign_data['content_type']}")
                        st.write(f"**Tone:** {campaign_data['tone']}")
                        st.write("**Target Personas:**")
                        for persona in campaign_data['personas']:
                            st.write(f"- {persona['role']}")
                        if campaign_data['hashtags']:
                            st.write(f"**Hashtags:** {', '.join(campaign_data['hashtags'])}")

                    # Show distribution options
                    st.markdown("---")
                    self.show_distribution_options(content, campaign_data)
                    
                    # Add preview of Twitter content
                    with st.expander("Preview Twitter Content", expanded=True):
                        twitter_content = self.social_media_manager.optimize_for_twitter(
                            content, 
                            campaign_data["hashtags"]
                        )
                        st.text(twitter_content)
                        st.write(f"Character count: {len(twitter_content)}/280")
        
        elif page == "Analytics":
            self.analytics_manager.show_analytics_dashboard()
        
        else:  # Content History
            self.show_content_history()

    def show_distribution_options(self, content: str, campaign_data: Dict):
        st.subheader("📤 Share Content")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🐦 Twitter")
            st.info("Share this content on Twitter")
            
            # Generate Twitter preview once and store in session state
            if st.session_state.twitter_preview is None:
                st.session_state.twitter_preview = self.social_media_manager.optimize_for_twitter(
                    content, 
                    campaign_data["hashtags"]
                )
            
            # Show Twitter preview
            with st.expander("Preview Twitter Content", expanded=True):
                st.text(st.session_state.twitter_preview)
                st.write(f"Character count: {len(st.session_state.twitter_preview)}/280")
            
            # Initialize Twitter client if not already done
            twitter_ready = self.social_media_manager.setup_twitter_auth(
                api_key=os.getenv("TWITTER_API_KEY"),
                api_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            )
            
            # Handle Twitter posting
            if twitter_ready and st.button("🚀 Post to Twitter", type="primary"):
                st.session_state.twitter_post_status = "posting"
            
            # Show posting status
            if st.session_state.twitter_post_status == "posting":
                result = self.social_media_manager.post_to_twitter(
                    st.session_state.twitter_preview,
                    campaign_data["hashtags"]
                )
                if result["success"]:
                    st.session_state.twitter_post_status = "success"
                    st.success("Posted to Twitter successfully!")
                    st.markdown(f"[View Tweet]({result['url']})")
                    # Update content history with tweet URL
                    for item in st.session_state.content_history:
                        if item["content"] == content:
                            item["tweet_url"] = result["url"]
                    st.balloons()
                else:
                    st.session_state.twitter_post_status = "failed"
                    st.error(f"Failed to post to Twitter: {result.get('error', 'Unknown error')}")
        
        with col2:
            st.subheader("📧 Email Campaign")
            st.info("Send this content via email")
            
            # Show selected personas
            st.write("**Selected Personas:**")
            for persona in campaign_data['personas']:
                st.write(f"- {persona['role']}")
            
            recipients = st.text_area(
                "Email Recipients (one per line)",
                help="Enter email addresses, one per line"
            )
            
            if st.button("📨 Send Email Campaign", type="primary"):
                email_content = self.social_media_manager.format_email(content)
                
                recipient_list = [r.strip() for r in recipients.split('\n') if r.strip()]
                
                if not recipient_list:
                    st.error("Please enter at least one recipient email address.")
                    return
                
                if self.email_service.send_email(
                    recipient_list,
                    email_content["subject"],
                    email_content["body"]
                ):
                    st.success("Email campaign sent successfully!")
                    st.write(f"Sent to {len(recipient_list)} recipients")
                    st.balloons()

    def show_content_history(self):
        """Display content generation history"""
        st.header("📚 Content History")
        
        if not st.session_state.content_history:
            st.info("No content has been generated yet.")
            return
        
        for item in reversed(st.session_state.content_history):
            with st.expander(f"{item['content_type']} - {item['created_at']}"):
                st.write(f"**Campaign Goal:** {item['campaign_goal']}")
                st.write("**Target Personas:**")
                for role in item['persona_roles']:
                    st.write(f"- {role}")
                st.write(f"**Tone:** {item['tone']}")
                st.text(item['content'])
                if item['hashtags']:
                    st.write(f"**Hashtags:** {', '.join(item['hashtags'])}")
                if item.get('tweet_url'):
                    st.markdown(f"**[View Tweet]({item['tweet_url']})**")
                
                # Add repost option
                if st.button("🔄 Repost to Twitter", key=f"repost_{item['id']}"):
                    st.session_state.current_content = item['content']
                    st.session_state.current_campaign_data = {
                        "hashtags": item['hashtags'],
                        "content_type": item['content_type'],
                        "tone": item['tone']
                    }
                    st.session_state.twitter_post_status = "posting"
                    st.experimental_rerun()

if __name__ == "__main__":
    app = CampaignCraftAI()
    app.main() 