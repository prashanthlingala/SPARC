from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
from utils.database import Database

class CampaignScheduler:
    def __init__(self):
        self.db = Database()
        self.platforms = {
            "twitter": "Twitter 🐦",
            "email": "Email 📧",
            "linkedin": "LinkedIn 💼",
            "blog": "Blog ✍️"
        }

    def show_scheduler(self):
        st.header("📅 Campaign Scheduler")
        
        # Get all campaigns with content
        campaigns = self.db.get_campaigns_with_content()
        
        if not campaigns:
            st.info("No campaigns available for scheduling.")
            return

        # Create new schedule
        with st.expander("➕ Create New Schedule", expanded=True):
            self.create_schedule_form(campaigns)

        # View existing schedules
        st.subheader("📋 Scheduled Campaigns")
        self.show_scheduled_campaigns()

    def create_schedule_form(self, campaigns: List[Dict]):
        with st.form("schedule_form"):
            # Campaign selection
            selected_campaign = st.selectbox(
                "Select Campaign",
                options=campaigns,
                format_func=lambda x: f"{x['name']} ({x['created_at'][:10]})"
            )

            if selected_campaign and selected_campaign.get('content'):
                # Content selection
                content_options = selected_campaign['content']
                selected_content = st.selectbox(
                    "Select Content",
                    options=content_options,
                    format_func=lambda x: f"{x['content_type']} - {x['created_at'][:10]}"
                )

                # Platform selection
                col1, col2 = st.columns(2)
                with col1:
                    platforms = st.multiselect(
                        "Select Platforms",
                        options=list(self.platforms.keys()),
                        format_func=lambda x: self.platforms[x],
                        help="Select platforms for campaign delivery"
                    )

                # Schedule datetime
                with col2:
                    min_date = datetime.now()
                    max_date = min_date + timedelta(days=365)
                    scheduled_date = st.date_input(
                        "Select Date",
                        min_value=min_date.date(),
                        max_value=max_date.date()
                    )
                    scheduled_time = st.time_input(
                        "Select Time",
                        value=datetime.now().replace(minute=0, second=0, microsecond=0)
                    )

                submitted = st.form_submit_button("📅 Schedule Campaign")
                
                if submitted:
                    if not platforms:
                        st.error("Please select at least one platform")
                        return

                    # Combine date and time
                    scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
                    
                    if scheduled_datetime <= datetime.now():
                        st.error("Please select a future date and time")
                        return

                    # Create schedules for each platform
                    for platform in platforms:
                        schedule_data = {
                            "campaign_id": selected_campaign['id'],
                            "content_id": selected_content['id'],
                            "platform": platform,
                            "scheduled_time": scheduled_datetime.isoformat()
                        }
                        self.db.save_schedule(schedule_data)
                    
                    st.success("Campaign scheduled successfully!")
                    st.rerun()

    def show_scheduled_campaigns(self):
        schedules = self.db.get_campaign_schedules()
        
        if not schedules:
            st.info("No scheduled campaigns found.")
            return

        # Group schedules by date
        current_date = None
        for schedule in schedules:
            scheduled_time = datetime.fromisoformat(schedule['scheduled_time'])
            schedule_date = scheduled_time.date()
            
            if schedule_date != current_date:
                current_date = schedule_date
                st.subheader(schedule_date.strftime("%B %d, %Y"))
            
            with st.expander(
                f"🕒 {scheduled_time.strftime('%I:%M %p')} - {schedule['campaign_name']}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Campaign:** {schedule['campaign_name']}")
                    st.write(f"**Content Type:** {schedule['content_type']}")
                    st.write(f"**Platform:** {self.platforms[schedule['platform']]}")
                    st.write(f"**Status:** {schedule['status'].title()}")
                
                with col2:
                    if schedule['status'] == 'pending':
                        if st.button("🗑️ Cancel", key=f"cancel_{schedule['id']}"):
                            # Add cancel functionality
                            st.info("Schedule cancellation to be implemented") 