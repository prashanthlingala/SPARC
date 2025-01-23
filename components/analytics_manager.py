from typing import Dict, List
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

class AnalyticsManager:
    def __init__(self):
        # Initialize analytics data in session state
        if 'analytics_data' not in st.session_state:
            st.session_state.analytics_data = {
                'twitter': self._generate_mock_twitter_data(),
                'email': self._generate_mock_email_data(),
                'overall': []
            }
    
    def _generate_mock_twitter_data(self):
        """Generate realistic mock data for Twitter"""
        data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            impressions = random.randint(2000, 8000)
            clicks = random.randint(100, int(impressions * 0.15))  # 5-15% CTR
            conversions = random.randint(10, int(clicks * 0.25))   # 10-25% conversion
            roi = random.uniform(2.0, 5.0)  # 200-500% ROI
            
            data.append({
                'platform': 'Twitter',
                'content_id': f'tweet_{i}',
                'content_preview': f'Engaging tweet about AI technology #{i}...',
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'roi': roi,
                'date': date.strftime("%Y-%m-%d %H:%M:%S")
            })
        return data
    
    def _generate_mock_email_data(self):
        """Generate realistic mock data for Email campaigns"""
        data = []
        for i in range(10):
            date = datetime.now() - timedelta(days=i*3)
            impressions = random.randint(8000, 20000)
            clicks = random.randint(800, int(impressions * 0.20))  # 10-20% CTR
            conversions = random.randint(80, int(clicks * 0.30))   # 10-30% conversion
            roi = random.uniform(3.0, 6.0)  # 300-600% ROI
            
            data.append({
                'platform': 'Email',
                'content_id': f'email_{i}',
                'content_preview': f'Monthly AI Innovation Newsletter #{i}',
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'roi': roi,
                'date': date.strftime("%Y-%m-%d %H:%M:%S")
            })
        return data

    def show_analytics_dashboard(self):
        """Display analytics dashboard"""
        st.title("📊 Campaign Analytics")
        
        # Time period and platform filters
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
        
        # Convert to DataFrame for analysis
        if all_data:
            df = pd.DataFrame(all_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] > date_filter]
            
            # Show key metrics in cards with custom styling
            st.markdown("""
            <style>
            .metric-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 2rem;
            }
            .metric-card {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                width: 23%;
            }
            .metric-value {
                font-size: 28px;
                font-weight: bold;
                color: #0068c9;
                margin-bottom: 0.5rem;
            }
            .metric-label {
                font-size: 16px;
                color: #555;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Calculate metrics
            total_impressions = df['impressions'].sum()
            avg_ctr = (df['clicks'].sum() / df['impressions'].sum() * 100) if df['impressions'].sum() > 0 else 0
            total_conversions = df['conversions'].sum()
            avg_roi = df['roi'].mean() * 100
            
            # Display metrics in cards
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value">{total_impressions:,.0f}</div>
                    <div class="metric-label">Total Impressions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_ctr:.1f}%</div>
                    <div class="metric-label">Click-Through Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_conversions:,.0f}</div>
                    <div class="metric-label">Total Conversions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_roi:.1f}%</div>
                    <div class="metric-label">Return on Investment</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show trends
            st.subheader("📈 Performance Trends")
            tab1, tab2 = st.tabs(["Engagement Metrics", "Conversion & ROI"])
            
            with tab1:
                # Daily engagement metrics
                daily_metrics = df.groupby([df['date'].dt.date, 'platform']).agg({
                    'impressions': 'sum',
                    'clicks': 'sum'
                }).reset_index()
                
                # Create two charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.caption("Daily Impressions")
                    st.line_chart(
                        daily_metrics.pivot(index='date', 
                                         columns='platform', 
                                         values='impressions')
                    )
                
                with col2:
                    st.caption("Daily Clicks")
                    st.line_chart(
                        daily_metrics.pivot(index='date', 
                                         columns='platform', 
                                         values='clicks')
                    )
            
            with tab2:
                # Daily conversion metrics
                daily_conv = df.groupby([df['date'].dt.date, 'platform']).agg({
                    'conversions': 'sum',
                    'roi': 'mean'
                }).reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.caption("Daily Conversions")
                    st.line_chart(
                        daily_conv.pivot(index='date', 
                                      columns='platform', 
                                      values='conversions')
                    )
                
                with col2:
                    st.caption("Daily ROI (%)")
                    st.line_chart(
                        daily_conv.pivot(index='date', 
                                      columns='platform', 
                                      values='roi') * 100
                    )
            
            # Campaign details table
            st.subheader("📋 Campaign Details")
            st.dataframe(
                df[[
                    'platform', 'content_preview', 'impressions', 
                    'clicks', 'conversions', 'roi', 'date'
                ]].sort_values('date', ascending=False),
                hide_index=True
            )
        else:
            st.info("No analytics data available for the selected period and platform.") 