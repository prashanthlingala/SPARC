from openai import AzureOpenAI
from typing import Dict

class ContentGenerator:
    def __init__(self, 
                 api_key: str,
                 azure_endpoint: str,
                 deployment_name: str = "gpt-4o-mini",
                 api_version: str = "2024-02-15-preview"):
        """Initialize the Azure OpenAI client"""
        if not api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI API key and endpoint are required")
            
        try:
            self.client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                http_client=None  # Explicitly set to None to avoid proxy issues
            )
            self.deployment_name = deployment_name
        except Exception as e:
            print(f"Error initializing Azure OpenAI client: {str(e)}")
            raise
        
    def generate_content(self, 
                        campaign_goal: str,
                        persona: Dict,
                        content_type: str,
                        tone: str,
                        custom_prompt: str = None) -> str:
        """Generate content using Azure OpenAI"""
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f"""
            Generate content for a marketing campaign with the following details:
            
            Goal: {campaign_goal}
            
            Target Persona:
            - Role: {persona['role']}
            - Experience: {persona.get('experience', 'Not specified')}
            - Technical Level: {persona.get('technical_proficiency', 'Not specified')}
            
            Content Type: {content_type}
            Tone: {tone}
            
            Make the content engaging and relevant for the target persona.
            """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert marketing content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return f"Error generating content: {str(e)}"
        
    def _create_prompt(self, goal, persona, content_type, tone):
        return f"""
        Create {content_type} content with the following specifications:
        
        Campaign Goal: {goal}
        Target Audience: {persona['role']} with {persona['experience']} experience
        Technical Level: {persona['technical_proficiency']}
        Tone: {tone}
        
        The content should be engaging, informative, and specifically tailored for 
        professionals in the data industry. Include relevant technical details while 
        maintaining the specified tone.
        """ 