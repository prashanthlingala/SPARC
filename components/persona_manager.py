from typing import Dict, Optional, Any, List
import streamlit as st
from utils.database import Database

class PersonaManager:
    def __init__(self):
        self.db = Database()

    def create_persona_form(self) -> Optional[Dict]:
        """Display form for creating a new persona"""
        st.subheader("Create Target Persona")
        
        with st.form("persona_form"):
            name = st.text_input("Persona Name", placeholder="e.g., Humans of Data")
            role = st.text_input("Role/Occupation", placeholder="e.g., Data Engineer, Analytics Manager")
            experience = st.selectbox(
                "Experience Level",
                ["Entry Level", "Mid Level", "Senior Level", "Leadership"]
            )
            technical_proficiency = st.select_slider(
                "Technical Proficiency",
                options=["Basic", "Intermediate", "Advanced", "Expert"]
            )
            
            submitted = st.form_submit_button("Save Persona")
            
            if submitted:
                if not name or not role:
                    st.error("Please fill in all required fields")
                    return None
                
                persona = {
                    "name": name,
                    "role": role,
                    "experience": experience,
                    "technical_proficiency": technical_proficiency
                }
                
                # Save to database
                persona_id = self.db.save_persona(persona)
                persona['id'] = persona_id
                st.success(f"Persona '{name}' saved successfully!")
                return persona
        return None

    def display_personas(self):
        """Display saved personas with edit and delete options"""
        st.subheader("Saved Personas")
        personas = self.get_personas()
        
        if not personas:
            st.info("No personas created yet.")
            return

        for persona in personas:
            with st.expander(f"📋 {persona['name']} - {persona['role']}", expanded=False):
                # Display current values
                st.write(f"**Experience:** {persona['experience']}")
                st.write(f"**Technical Proficiency:** {persona['technical_proficiency']}")
                
                # Edit form
                with st.form(key=f"edit_persona_{persona['id']}"):
                    edited_name = st.text_input("Name", value=persona['name'])
                    edited_role = st.text_input("Role", value=persona['role'])
                    edited_experience = st.selectbox(
                        "Experience Level",
                        ["Entry Level", "Mid Level", "Senior Level", "Leadership"],
                        index=["Entry Level", "Mid Level", "Senior Level", "Leadership"].index(persona['experience'])
                    )
                    edited_proficiency = st.select_slider(
                        "Technical Proficiency",
                        options=["Basic", "Intermediate", "Advanced", "Expert"],
                        value=persona['technical_proficiency']
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            updates = {
                                'name': edited_name,
                                'role': edited_role,
                                'experience': edited_experience,
                                'technical_proficiency': edited_proficiency
                            }
                            if self.update_persona(persona['id'], updates):
                                st.success("Persona updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update persona")
                    
                    with col2:
                        if st.form_submit_button("🗑️ Delete Persona", type="secondary"):
                            if self.delete_persona(persona['id']):
                                st.success("Persona deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete persona")

    def get_personas(self):
        """Return list of saved personas"""
        return self.db.get_personas()

    def get_persona(self, persona_id: int) -> Optional[Dict]:
        """Retrieve a specific persona"""
        personas = self.db.get_personas()
        return next((p for p in personas if p['id'] == persona_id), None)

    def update_persona(self, persona_id: int, updates: Dict) -> bool:
        """Update persona in database"""
        return self.db.update_persona(persona_id, updates)

    def delete_persona(self, persona_id: int) -> bool:
        """Delete persona from database"""
        return self.db.delete_persona(persona_id) 