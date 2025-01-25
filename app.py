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
from components.campaign_scheduler import CampaignScheduler

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
        self.campaign_scheduler = CampaignScheduler()
        
    def main(self):
        st.title("Smart Personalised Automation for Remarkable Campaigns (S.P.A.R.C)")
        st.subheader("AI-Powered Marketing Campaign Generator")
        
        with st.sidebar:
            st.header("Navigation")
            page = st.radio(
                "Go to",
                ["Create Persona", "Generate Content", "Content Manager", "Campaign Scheduler", "Analytics"]
            )
        
        if page == "Campaign Scheduler":
            self.campaign_scheduler.show_scheduler()
        elif page == "Create Persona":
            self.persona_manager.create_persona_form()
            self.persona_manager.display_personas()
            
        elif page == "Generate Content":
            campaign_data = self.campaign_manager.create_campaign_form(
                self.persona_manager.get_personas()
            )
            
            if campaign_data:
                with st.spinner("🤖 AI is crafting your content..."):
                    try:
                        generated_content = self.content_generator.generate_content(
                            campaign_goal=campaign_data["campaign_goal"],
                            persona=campaign_data["persona"],
                            content_type=campaign_data["content_type"],
                            tone=campaign_data["tone"]
                        )

                        if generated_content:
                            # Save the generated content to database
                            content_data = {
                                "persona": campaign_data["persona"],
                                "content_type": campaign_data["content_type"],
                                "tone": campaign_data["tone"],
                                "content": generated_content,
                                "hashtags": campaign_data.get("hashtags", []),
                                "keywords": campaign_data.get("keywords", [])
                            }
                            self.campaign_manager.save_generated_content(
                                campaign_id=campaign_data["id"],
                                content_data=content_data
                            )

                            # Display the generated content
                            st.subheader("Generated Content")
                            st.markdown(generated_content)

                            # Show content preview options
                            self.show_content_preview(generated_content)

                    except Exception as e:
                        st.error(f"Error generating content: {str(e)}")
        
        elif page == "Analytics":
            self.analytics_manager.show_analytics_dashboard()
        
        elif page == "Content Manager":
            self.show_content_manager()
        
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

    def show_content_preview(self, content: str):
        """Display content preview and distribution options"""
        st.markdown("---")
        
        # Preview tabs
        tab1, tab2, tab3 = st.tabs(["📱 Social Media", "📧 Email", "📄 Raw Content"])
        
        with tab1:
            st.subheader("Social Media Preview")
            # Twitter preview
            with st.expander("Twitter Post", expanded=True):
                twitter_content = self.social_media_manager.optimize_for_twitter(content, [])
                st.text(twitter_content)
                st.write(f"Character count: {len(twitter_content)}/280")
                
                if st.button("🐦 Post to Twitter"):
                    # Initialize Twitter client if not already done
                    twitter_ready = self.social_media_manager.setup_twitter_auth(
                        api_key=os.getenv("TWITTER_API_KEY"),
                        api_secret=os.getenv("TWITTER_API_SECRET"),
                        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                    )
                    
                    if twitter_ready:
                        with st.spinner("Posting to Twitter..."):
                            result = self.social_media_manager.post_to_twitter(twitter_content, [])
                            if result["success"]:
                                st.success("Posted to Twitter successfully!")
                                st.markdown(f"[View Tweet]({result['url']})")
                            else:
                                st.error(f"Failed to post to Twitter: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("Twitter authentication not configured")
        
        with tab2:
            st.subheader("Email Preview")
            email_content = self.social_media_manager.format_email(content)
            st.write("**Subject:**", email_content["subject"])
            st.write("**Body:**")
            st.markdown(email_content["body"])
            
            recipients = st.text_area(
                "Email Recipients (one per line)",
                help="Enter email addresses, one per line"
            )
            
            if st.button("📨 Send Email"):
                recipient_list = [r.strip() for r in recipients.split('\n') if r.strip()]
                if not recipient_list:
                    st.error("Please enter at least one recipient email address.")
                else:
                    with st.spinner("Sending emails..."):
                        if self.email_service.send_email(
                            recipient_list,
                            email_content["subject"],
                            email_content["body"]
                        ):
                            st.success("Email campaign sent successfully!")
                            st.write(f"Sent to {len(recipient_list)} recipients")
                        else:
                            st.error("Failed to send email campaign")
        
        with tab3:
            st.subheader("Raw Content")
            st.markdown(content)

    def show_content_manager(self):
        """Enhanced content management interface"""
        st.header("📚 Content Manager")
        
        # Get all campaigns with their content
        campaigns = self.campaign_manager.get_all_campaigns()
        
        if not campaigns:
            st.info("No content has been generated yet.")
            return
        
        for campaign in campaigns:
            with st.expander(f"Campaign: {campaign['name']} - {campaign['created_at']}", expanded=False):
                st.write(f"**Goal:** {campaign['goal']}")
                st.write(f"**Status:** {campaign['status']}")
                
                # Get content for this campaign
                content_list = self.campaign_manager.get_campaign_content(campaign['id'])
                
                if content_list:
                    for content in content_list:
                        st.markdown("---")
                        tabs = st.tabs(["✍️ Blog Content", "📱 Social Media", "📧 Email"])
                        
                        with tabs[0]:
                            # Blog/Raw content editor
                            edited_content = st.text_area(
                                "Edit Blog Content",
                                value=content['content'],
                                height=300,
                                key=f"blog_{content['id']}"
                            )
                            if st.button("💾 Save Blog Changes", key=f"save_blog_{content['id']}"):
                                self.campaign_manager.update_content(
                                    content['id'],
                                    {'content': edited_content}
                                )
                                st.success("Content updated successfully!")
                        
                        with tabs[1]:
                            # Social Media content
                            twitter_content = self.social_media_manager.optimize_for_twitter(
                                content['content'], []
                            )
                            edited_twitter = st.text_area(
                                "Edit Twitter Content",
                                value=twitter_content,
                                height=100,
                                key=f"twitter_{content['id']}"
                            )
                            st.write(f"Character count: {len(edited_twitter)}/280")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("💾 Save Twitter Edit", key=f"save_twitter_{content['id']}"):
                                    self.campaign_manager.update_content(
                                        content['id'],
                                        {'twitter_content': edited_twitter}
                                    )
                                    st.success("Twitter content saved!")
                            
                            with col2:
                                if st.button("🐦 Post to Twitter", key=f"post_twitter_{content['id']}"):
                                    with st.spinner("Posting to Twitter..."):
                                        result = self.social_media_manager.post_to_twitter(
                                            edited_twitter, []
                                        )
                                        if result["success"]:
                                            st.success("Posted to Twitter!")
                                            st.markdown(f"[View Tweet]({result['url']})")
                                        else:
                                            st.error(f"Failed to post: {result.get('error')}")
                        
                        with tabs[2]:
                            # Email content
                            email_content = self.social_media_manager.format_email(content['content'])
                            
                            edited_subject = st.text_input(
                                "Edit Email Subject",
                                value=email_content["subject"],
                                key=f"subject_{content['id']}"
                            )
                            
                            edited_body = st.text_area(
                                "Edit Email Body",
                                value=email_content["body"],
                                height=300,
                                key=f"email_{content['id']}"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("💾 Save Email Content", key=f"save_email_{content['id']}"):
                                    self.campaign_manager.update_content(
                                        content['id'],
                                        {
                                            'email_subject': edited_subject,
                                            'email_body': edited_body
                                        }
                                    )
                                    st.success("Email content saved!")
                            
                            with col2:
                                recipients = st.text_area(
                                    "Email Recipients (one per line)",
                                    key=f"recipients_{content['id']}"
                                )
                                if st.button("📨 Send Email", key=f"send_email_{content['id']}"):
                                    recipient_list = [r.strip() for r in recipients.split('\n') if r.strip()]
                                    if not recipient_list:
                                        st.error("Please enter recipients")
                                    else:
                                        with st.spinner("Sending emails..."):
                                            if self.email_service.send_email(
                                                recipient_list,
                                                edited_subject,
                                                edited_body
                                            ):
                                                st.success("Emails sent successfully!")
                                            else:
                                                st.error("Failed to send emails")

if __name__ == "__main__":
    app = CampaignCraftAI()
    app.main() 