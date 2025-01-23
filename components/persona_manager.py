from typing import Dict, Optional, Any
import streamlit as st

class PersonaManager:
    def __init__(self):
        if 'personas' not in st.session_state:
            st.session_state.personas = []
        if 'content_history' not in st.session_state:
            st.session_state.content_history = []

    def create_persona_form(self) -> Optional[Dict]:
        """Display form for creating a new persona"""
        st.subheader("Create Target Persona")
        
        with st.form("persona_form"):
            role = st.text_input("Role/Occupation", placeholder="e.g., Data Engineer, Analytics Manager")
            experience = st.selectbox(
                "Experience Level",
                ["Entry Level", "Mid Level", "Senior Level", "Leadership"]
            )
            technical_proficiency = st.select_slider(
                "Technical Proficiency",
                options=["Basic", "Intermediate", "Advanced", "Expert"]
            )
            content_style = st.multiselect(
                "Preferred Content Style",
                ["Technical", "Strategic", "Practical", "Theoretical"]
            )
            pain_points = st.text_area(
                "Key Pain Points",
                placeholder="What challenges does this persona face?"
            )
            
            submitted = st.form_submit_button("Save Persona")
            
            if submitted:
                persona = {
                    "id": len(st.session_state.personas) + 1,
                    "role": role,
                    "experience": experience,
                    "technical_proficiency": technical_proficiency,
                    "content_style": content_style,
                    "pain_points": pain_points
                }
                st.session_state.personas.append(persona)
                st.success(f"Persona '{role}' saved successfully!")
                return persona
        return None

    def get_personas(self):
        """Return list of saved personas"""
        return st.session_state.personas 