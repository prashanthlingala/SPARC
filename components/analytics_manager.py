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
            impressions = random.randint(1000, 5000)
            clicks = random.randint(50, int(impressions * 0.1))  # 1-10% CTR
            conversions = random.randint(5, int(clicks * 0.2))   # 5-20% conversion
            roi = random.uniform(1.5, 4.0)  # 150-400% ROI
            
            data.append({
                'platform': 'Twitter',
                'content_id': f'tweet_{i}',
                'content_preview': f'Engaging tweet about product features #{i}...',
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
            impressions = random.randint(5000, 15000)
            clicks = random.randint(500, int(impressions * 0.15))  # 5-15% CTR
            conversions = random.randint(50, int(clicks * 0.25))   # 10-25% conversion
            roi = random.uniform(2.0, 5.0)  # 200-500% ROI
            
            data.append({
                'platform': 'Email',
                'content_id': f'email_{i}',
                'content_preview': f'Monthly Newsletter #{i}',
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
            
            # Show key metrics in cards
            st.markdown("### Key Performance Metrics")
            
            # Create a custom card style
            card_style = """
            <style>
                .metric-card {
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0066cc;
                }
                .metric-label {
                    font-size: 16px;
                    color: #666;
                }
            </style>
            """
            st.markdown(card_style, unsafe_allow_html=True)
            
            # Create metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_impressions = df['impressions'].sum()
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_impressions:,.0f}</div>
                        <div class="metric-label">Total Impressions</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                avg_ctr = (df['clicks'].sum() / df['impressions'].sum() * 100)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{avg_ctr:.1f}%</div>
                        <div class="metric-label">Click-Through Rate</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col3:
                total_conversions = df['conversions'].sum()
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_conversions:,.0f}</div>
                        <div class="metric-label">Total Conversions</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col4:
                avg_roi = df['roi'].mean() * 100
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{avg_roi:.1f}%</div>
                        <div class="metric-label">Average ROI</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Show trends
            st.markdown("### Performance Trends")
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
            st.markdown("### Campaign Details")
            st.dataframe(
                df[[
                    'platform', 'content_preview', 'impressions', 
                    'clicks', 'conversions', 'roi', 'date'
                ]].sort_values('date', ascending=False)
            )
        else:
            st.info("No analytics data available for the selected period and platform.") 