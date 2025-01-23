# Standard library imports
import importlib.util
from typing import Dict, Optional, List

# Third-party imports
import streamlit as st

# Check if tweepy is installed
tweepy_spec = importlib.util.find_spec("tweepy")
TWITTER_AVAILABLE = tweepy_spec is not None

tweepy = None
if TWITTER_AVAILABLE:
    try:
        import tweepy
    except ImportError:
        TWITTER_AVAILABLE = False
        print("Failed to import tweepy")

# Local imports
from utils.openai_helper import ContentGenerator

class SocialMediaManager:
    def __init__(self, openai_client: ContentGenerator):
        self.openai_client = openai_client
        self.twitter_char_limit = 280
        self.twitter_enabled = TWITTER_AVAILABLE
        self.twitter_client = None
        
    def setup_twitter_auth(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """Initialize Twitter API client"""
        if not self.twitter_enabled:
            st.warning("To enable Twitter functionality, please run: pip install tweepy==4.14.0")
            return False
        
        try:
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.twitter_client = tweepy.API(auth)
            return True
        except Exception as e:
            st.error(f"Failed to initialize Twitter client: {str(e)}")
            return False
        
    def optimize_for_twitter(self, content: str, hashtags: list) -> str:
        """Optimize content for Twitter using OpenAI"""
        prompt = f"""
        Rewrite the following content for Twitter (max {self.twitter_char_limit} characters).
        Make it engaging and concise. Include these hashtags where appropriate: {' '.join(hashtags)}
        
        Original content:
        {content}
        """
        
        response = self.openai_client.generate_content(
            campaign_goal="Optimize content for Twitter",
            persona={"role": "Social Media Manager"},
            content_type="Social Media Post",
            tone="Conversational",
            custom_prompt=prompt
        )
        
        return response[:self.twitter_char_limit]
    
    def format_email(self, content: str, subject: str = None) -> Dict[str, str]:
        """Format content for email using OpenAI"""
        prompt = f"""
        Rewrite the following content as a professional email.
        Include a subject line, greeting, body, and signature.
        Make it engaging and professional.
        
        Original content:
        {content}
        """
        
        email_content = self.openai_client.generate_content(
            campaign_goal="Format content for email",
            persona={"role": "Email Marketing Specialist"},
            content_type="Email Newsletter",
            tone="Professional",
            custom_prompt=prompt
        )
        
        # Extract subject if not provided
        if not subject:
            # Simple extraction - can be made more sophisticated
            lines = email_content.split('\n')
            subject = next((line.replace('Subject:', '').strip() 
                          for line in lines if line.startswith('Subject:')), 
                         'New Campaign Update')
            
        return {
            "subject": subject,
            "body": email_content
        }
    
    def post_to_twitter(self, content: str, hashtags: list) -> Dict:
        """Post content to Twitter"""
        try:
            if not hasattr(self, 'twitter_client'):
                st.error("Twitter client not initialized. Please check your credentials.")
                return False
                
            optimized_content = self.optimize_for_twitter(content, hashtags)
            
            # Check content length and optimize if needed
            if len(optimized_content) > self.twitter_char_limit:
                st.warning("Content exceeds Twitter's character limit. Optimizing further...")
                prompt = f"""
                The following content is too long for Twitter ({len(optimized_content)} chars).
                Please shorten it to under {self.twitter_char_limit} characters while maintaining
                the key message. Include these hashtags if space permits: {' '.join(hashtags)}
                
                Content:
                {optimized_content}
                """
                optimized_content = self.openai_client.generate_content(
                    campaign_goal="Shorten content for Twitter",
                    persona={"role": "Social Media Manager"},
                    content_type="Social Media Post",
                    tone="Conversational",
                    custom_prompt=prompt
                )[:self.twitter_char_limit]
            
            # Preview the content before posting
            st.info("Posting the following content to Twitter:")
            st.code(optimized_content)
            
            with st.spinner("Posting to Twitter..."):
                tweet = self.twitter_client.update_status(optimized_content)
                tweet_url = f"https://twitter.com/user/status/{tweet.id}"
                
                # Add mock metrics (replace with real API calls)
                mock_metrics = {
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'roi': 0.0
                }
                st.session_state.analytics_manager.add_twitter_metrics(
                    tweet.id, 
                    optimized_content,
                    mock_metrics
                )
                
                return {"success": True, "url": tweet_url, "content": optimized_content}
        except Exception as e:
            if "duplicate" in str(e).lower():
                st.error("This content has already been posted to Twitter.")
            elif "authentication" in str(e).lower():
                st.error("Twitter authentication failed. Please check your credentials.")
            elif "rate limit" in str(e).lower():
                st.error("Twitter rate limit reached. Please try again later.")
            else:
                st.error(f"Error posting to Twitter: {str(e)}")
            return {"success": False, "error": str(e)} 