import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime

class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
    
    def setup_smtp(self, email: str, password: str):
        """Setup SMTP credentials"""
        self.sender_email = email
        self.sender_password = password
    
    def send_email(self, recipients: List[str], subject: str, body: str) -> bool:
        """Send email to recipients"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            # Add mock metrics (replace with real email service metrics)
            mock_metrics = {
                'opens': 0,
                'clicks': 0,
                'conversions': 0,
                'roi': 0.0
            }
            st.session_state.analytics_manager.add_email_metrics(
                f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                subject,
                mock_metrics
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error sending email: {str(e)}")
            return False 