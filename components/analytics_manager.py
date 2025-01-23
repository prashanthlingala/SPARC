from typing import Dict, List
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class AnalyticsManager:
    def __init__(self):
        # Initialize analytics data in session state
        if 'analytics_data' not in st.session_state:
            st.session_state.analytics_data = {
                'twitter': [],
                'email': [],
                'overall': []
            }
    
    def add_twitter_metrics(self, tweet_id: str, content: str, metrics: Dict):
        """Add Twitter metrics for a post"""
        data = {
            'platform': 'Twitter',
            'content_id': tweet_id,
            'content_preview': content[:50] + '...',
            'impressions': metrics.get('impressions', 0),
            'clicks': metrics.get('clicks', 0),
            'conversions': metrics.get('conversions', 0),
            'roi': metrics.get('roi', 0.0),
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.analytics_data['twitter'].append(data)
    
    def add_email_metrics(self, campaign_id: str, subject: str, metrics: Dict):
        """Add email campaign metrics"""
        data = {
            'platform': 'Email',
            'content_id': campaign_id,
            'content_preview': subject,
            'impressions': metrics.get('opens', 0),
            'clicks': metrics.get('clicks', 0),
            'conversions': metrics.get('conversions', 0),
            'roi': metrics.get('roi', 0.0),
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.analytics_data['email'].append(data)
    
    def show_analytics_dashboard(self):
        """Display analytics dashboard"""
        st.title("📊 Campaign Analytics")
        
        # Time period filter
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Time Period",
                ["Last 7 days", "Last 30 days", "All time"]
            )
        
        with col2:
            platform = st.selectbox(
                "Platform",
                ["All Platforms", "Twitter", "Email"]
            )
        
        # Calculate date filter
        if period == "Last 7 days":
            date_filter = datetime.now() - timedelta(days=7)
        elif period == "Last 30 days":
            date_filter = datetime.now() - timedelta(days=30)
        else:
            date_filter = datetime.min
        
        # Combine and filter data
        all_data = []
        if platform in ["All Platforms", "Twitter"]:
            all_data.extend(st.session_state.analytics_data['twitter'])
        if platform in ["All Platforms", "Email"]:
            all_data.extend(st.session_state.analytics_data['email'])
        
        # Convert to DataFrame for easier analysis
        if all_data:
            df = pd.DataFrame(all_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] > date_filter]
            
            # Show key metrics
            st.header("Key Metrics")
            metric1, metric2, metric3, metric4 = st.columns(4)
            
            with metric1:
                total_impressions = df['impressions'].sum()
                st.metric("Total Impressions", f"{total_impressions:,}")
            
            with metric2:
                avg_ctr = (df['clicks'].sum() / df['impressions'].sum() * 100) if df['impressions'].sum() > 0 else 0
                st.metric("Average CTR", f"{avg_ctr:.1f}%")
            
            with metric3:
                total_conversions = df['conversions'].sum()
                st.metric("Total Conversions", f"{total_conversions:,}")
            
            with metric4:
                avg_roi = df['roi'].mean()
                st.metric("Average ROI", f"{avg_roi:.1f}%")
            
            # Show trends
            st.header("Performance Trends")
            tab1, tab2 = st.tabs(["Impressions & Clicks", "Conversions & ROI"])
            
            with tab1:
                daily_metrics = df.groupby([df['date'].dt.date, 'platform']).agg({
                    'impressions': 'sum',
                    'clicks': 'sum'
                }).reset_index()
                
                st.line_chart(
                    daily_metrics.pivot(index='date', columns='platform', values='impressions')
                )
            
            with tab2:
                daily_conv = df.groupby([df['date'].dt.date, 'platform']).agg({
                    'conversions': 'sum',
                    'roi': 'mean'
                }).reset_index()
                
                st.line_chart(
                    daily_conv.pivot(index='date', columns='platform', values='roi')
                )
            
            # Show detailed data
            st.header("Campaign Details")
            st.dataframe(
                df[[
                    'platform', 'content_preview', 'impressions', 
                    'clicks', 'conversions', 'roi', 'date'
                ]].sort_values('date', ascending=False)
            )
        else:
            st.info("No analytics data available for the selected period and platform.") 