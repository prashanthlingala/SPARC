from typing import Dict, Optional, Any, List
import streamlit as st
from utils.database import Database
import json

class PersonaManager:
    def __init__(self):
        self.db = Database()
        self.predefined_roles = [
            "Data Scientist",
            "Data Engineer",
            "Data Analyst",
            "Analytics Manager",
            "Business Intelligence Developer",
            "Machine Learning Engineer",
            "Data Architect",
            "Analytics Consultant",
            "Chief Data Officer",
            "Data Strategy Manager"
        ]

    def create_persona_form(self) -> Optional[Dict]:
        """Display form for creating a new persona"""
        st.subheader("Create Target Persona")
        
        with st.form("persona_form"):
            name = st.text_input("Persona Name", placeholder="e.g., Humans of Data")
            
            # Role selection with both predefined and custom options
            st.subheader("Role/Occupation")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_roles = st.multiselect(
                    "Select Roles",
                    options=self.predefined_roles,
                    default=[],
                    help="Choose from predefined roles or add custom roles"
                )
            
            with col2:
                custom_role = st.text_input(
                    "Add Custom Role",
                    placeholder="Enter custom role",
                    help="Enter custom role and press Enter"
                )
                if custom_role:
                    custom_roles = [r.strip() for r in custom_role.split(',')]
                    selected_roles.extend(custom_roles)
            
            # Remove duplicates while preserving order
            selected_roles = list(dict.fromkeys(selected_roles))
            
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
                if not name or not selected_roles:
                    st.error("Please fill in all required fields")
                    return None
                
                persona = {
                    "name": name,
                    "role": json.dumps(selected_roles),  # Store roles as JSON string
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
            # Parse roles from JSON string with error handling
            try:
                roles = json.loads(persona['role']) if isinstance(persona['role'], str) else [persona['role']]
            except json.JSONDecodeError:
                # Handle legacy data: convert single role to list
                roles = [persona['role']] if persona['role'] else []
            
            with st.expander(f"📋 {persona['name']} - {', '.join(roles)}", expanded=False):
                # Display current values
                st.write("**Roles:**")
                for role in roles:
                    st.write(f"- {role}")
                st.write(f"**Experience:** {persona['experience']}")
                st.write(f"**Technical Proficiency:** {persona['technical_proficiency']}")
                
                # Edit form
                with st.form(key=f"edit_persona_{persona['id']}"):
                    edited_name = st.text_input("Name", value=persona['name'])
                    
                    # Combine predefined roles with existing roles for options
                    all_role_options = list(set(self.predefined_roles + roles))
                    
                    # Role editing with both predefined and custom options
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        edited_roles = st.multiselect(
                            "Select Roles",
                            options=all_role_options,
                            default=roles,
                            help="Choose from predefined roles or add custom roles"
                        )
                    
                    with col2:
                        custom_role = st.text_input(
                            "Add Custom Role",
                            placeholder="Enter custom role",
                            help="Enter custom role and press Enter",
                            key=f"custom_role_{persona['id']}"
                        )
                        if custom_role:
                            custom_roles = [r.strip() for r in custom_role.split(',')]
                            edited_roles.extend(custom_roles)
                    
                    # Remove duplicates while preserving order
                    edited_roles = list(dict.fromkeys(edited_roles))
                    
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
                                'role': json.dumps(edited_roles),  # Store roles as JSON string
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
        """Return list of saved personas with properly formatted roles"""
        personas = self.db.get_personas()
        
        # Convert roles to proper format
        for persona in personas:
            try:
                # Try to parse as JSON
                if isinstance(persona['role'], str):
                    persona['role'] = json.loads(persona['role'])
            except json.JSONDecodeError:
                # Handle legacy data: convert single role to JSON string
                persona['role'] = json.dumps([persona['role']] if persona['role'] else [])
        
        return personas

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