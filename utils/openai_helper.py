from openai import AzureOpenAI
from typing import Dict

class ContentGenerator:
    def __init__(self, 
                 api_key: str,
                 azure_endpoint: str,
                 deployment_name: str = "gpt-4",
                 api_version: str = "2024-02-15-preview"):
        
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        self.deployment_name = deployment_name
        
    def generate_content(self, 
                        campaign_goal: str,
                        persona: Dict,
                        content_type: str,
                        tone: str) -> str:
        
        prompt = self._create_prompt(
            campaign_goal,
            persona,
            content_type,
            tone
        )
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert marketing content creator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
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