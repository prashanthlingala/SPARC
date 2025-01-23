import streamlit as st
from dotenv import load_dotenv
import os
from components.persona_manager import PersonaManager
from components.campaign_manager import CampaignManager
from utils.openai_helper import ContentGenerator
from utils.config_loader import load_config

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
        
        # Setup page config
        st.set_page_config(
            page_title="CampaignCraft AI",
            page_icon="🎯",
            layout="wide"
        )
        
    def main(self):
        st.title("🎯 CampaignCraft AI")
        st.subheader("AI-Powered Marketing Campaign Content Generator")
        
        # Sidebar navigation
        with st.sidebar:
            st.header("Navigation")
            page = st.radio("Go to", ["Create Persona", "Generate Content"])
        
        if page == "Create Persona":
            self.persona_manager.create_persona_form()
            
            # Display saved personas
            if st.session_state.personas:
                st.subheader("Saved Personas")
                for persona in st.session_state.personas:
                    st.write(f"📋 {persona['role']} ({persona['experience']})")
        
        else:  # Generate Content
            campaign_data = self.campaign_manager.create_campaign_form(
                self.persona_manager.get_personas()
            )
            
            if campaign_data:
                with st.spinner("Generating content..."):
                    content = self.content_generator.generate_content(
                        campaign_goal=campaign_data["campaign_goal"],
                        persona=campaign_data["persona"],
                        content_type=campaign_data["content_type"],
                        tone=campaign_data["tone"]
                    )
                    
                    st.subheader("Generated Content")
                    st.write(content)
                    
                    # Display metadata
                    with st.expander("Campaign Details"):
                        st.write(f"**Content Type:** {campaign_data['content_type']}")
                        st.write(f"**Tone:** {campaign_data['tone']}")
                        st.write(f"**Target Persona:** {campaign_data['persona']['role']}")
                        if campaign_data['hashtags']:
                            st.write(f"**Hashtags:** {', '.join(campaign_data['hashtags'])}")

if __name__ == "__main__":
    app = CampaignCraftAI()
    app.main() 