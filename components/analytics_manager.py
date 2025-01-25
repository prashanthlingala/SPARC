from typing import Dict, List, Optional
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from utils.database import Database
import altair as alt

class AnalyticsManager:
    def __init__(self):
        self.db = Database()
        self.platforms = ["All Platforms", "Twitter", "Email", "Blog"]
        self.metric_types = {
            "Engagement": ["impressions", "clicks", "shares", "comments"],
            "Conversion": ["leads", "conversions", "sign_ups"],
            "Performance": ["ctr", "conversion_rate", "bounce_rate"]
        }
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

    def generate_mock_metrics(self, start_date: datetime, end_date: datetime, platform: str) -> pd.DataFrame:
        """Generate realistic mock metrics data"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        data = []
        
        base_metrics = {
            "Twitter": {
                "impressions": (2000, 8000),
                "clicks": (100, 500),
                "shares": (50, 200),
                "comments": (20, 100),
                "leads": (10, 50),
                "conversions": (5, 25)
            },
            "Email": {
                "impressions": (5000, 15000),
                "clicks": (500, 2000),
                "shares": (100, 400),
                "comments": (50, 200),
                "leads": (30, 150),
                "conversions": (15, 75)
            },
            "Blog": {
                "impressions": (1000, 5000),
                "clicks": (200, 800),
                "shares": (30, 150),
                "comments": (10, 50),
                "leads": (5, 25),
                "conversions": (2, 15)
            }
        }

        for date in date_range:
            for plt in [platform] if platform != "All Platforms" else base_metrics.keys():
                metrics = base_metrics[plt]
                daily_data = {
                    "date": date,
                    "platform": plt,
                    "impressions": random.randint(*metrics["impressions"]),
                    "clicks": random.randint(*metrics["clicks"]),
                    "shares": random.randint(*metrics["shares"]),
                    "comments": random.randint(*metrics["comments"]),
                    "leads": random.randint(*metrics["leads"]),
                    "conversions": random.randint(*metrics["conversions"])
                }
                
                # Calculate derived metrics
                daily_data["ctr"] = (daily_data["clicks"] / daily_data["impressions"]) * 100
                daily_data["conversion_rate"] = (daily_data["conversions"] / daily_data["clicks"]) * 100
                daily_data["bounce_rate"] = random.uniform(30, 70)
                
                data.append(daily_data)
        
        return pd.DataFrame(data)

    def show_analytics_dashboard(self):
        """Display enhanced analytics dashboard"""
        st.header("📊 Campaign Analytics")

        # Get all campaigns
        campaigns = self.db.get_campaigns()
        
        if not campaigns:
            st.info("No campaigns available for analysis.")
            return

        # Filters section
        with st.container():
            st.subheader("📈 Analytics Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_campaign = st.selectbox(
                    "Select Campaign",
                    options=campaigns,
                    format_func=lambda x: f"{x['name']} ({x['created_at']})",
                )
            
            with col2:
                selected_platform = st.selectbox(
                    "Platform",
                    options=self.platforms
                )
            
            with col3:
                date_filter = st.selectbox(
                    "Date Range",
                    ["Last 7 days", "Last 30 days", "Last 90 days", "Custom Range"]
                )

        # Date range selection
        if date_filter == "Custom Range":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End Date", datetime.now())
        else:
            days = {
                "Last 7 days": 7,
                "Last 30 days": 30,
                "Last 90 days": 90
            }
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days[date_filter])

        # Generate mock data for the selected period
        df = self.generate_mock_metrics(start_date, end_date, selected_platform)

        # Overview metrics with card style
        st.markdown("""
        <style>
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.25);
            transition: all 0.3s ease-in-out;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2e59d9;
            margin: 0;
            padding: 0;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #858796;
            margin: 0;
            padding: 0;
            text-transform: uppercase;
        }
        .metric-change {
            font-size: 0.8rem;
            color: #28a745;
            margin-top: 0.5rem;
        }
        .negative {
            color: #dc3545;
        }
        </style>
        """, unsafe_allow_html=True)

        st.subheader("📊 Overview")
        
        # Calculate metrics
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_conversions = df['conversions'].sum()
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        
        # Calculate period-over-period changes (mock data)
        prev_impressions = total_impressions * random.uniform(0.8, 1.2)
        prev_clicks = total_clicks * random.uniform(0.8, 1.2)
        prev_conversions = total_conversions * random.uniform(0.8, 1.2)
        prev_ctr = (prev_clicks / prev_impressions * 100) if prev_impressions > 0 else 0
        
        # Calculate changes
        impression_change = ((total_impressions - prev_impressions) / prev_impressions) * 100
        click_change = ((total_clicks - prev_clicks) / prev_clicks) * 100
        conversion_change = ((total_conversions - prev_conversions) / prev_conversions) * 100
        ctr_change = avg_ctr - prev_ctr

        # Create metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">Total Impressions</p>
                <p class="metric-value">{total_impressions:,.0f}</p>
                <p class="metric-change {'negative' if impression_change < 0 else ''}">
                    {impression_change:+.1f}% vs previous period
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">Total Clicks</p>
                <p class="metric-value">{total_clicks:,.0f}</p>
                <p class="metric-change {'negative' if click_change < 0 else ''}">
                    {click_change:+.1f}% vs previous period
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">Total Conversions</p>
                <p class="metric-value">{total_conversions:,.0f}</p>
                <p class="metric-change {'negative' if conversion_change < 0 else ''}">
                    {conversion_change:+.1f}% vs previous period
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">Average CTR</p>
                <p class="metric-value">{avg_ctr:.2f}%</p>
                <p class="metric-change {'negative' if ctr_change < 0 else ''}">
                    {ctr_change:+.2f}% vs previous period
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Add some spacing after the cards
        st.markdown("<br>", unsafe_allow_html=True)

        # Metrics over time
        st.subheader("📈 Metrics Over Time")
        metric_type = st.selectbox(
            "Metric Type",
            list(self.metric_types.keys())
        )
        
        selected_metrics = st.multiselect(
            "Select Metrics",
            self.metric_types[metric_type],
            default=[self.metric_types[metric_type][0]]
        )

        if selected_metrics:
            # Prepare data for time series chart
            chart_data = df.melt(
                id_vars=['date', 'platform'],
                value_vars=selected_metrics,
                var_name='metric',
                value_name='value'
            )

            # Create time series chart
            time_chart = alt.Chart(chart_data).mark_line().encode(
                x='date:T',
                y='value:Q',
                color='metric:N',
                strokeDash='platform:N',
                tooltip=['date', 'platform', 'metric', 'value']
            ).properties(
                height=400
            ).interactive()

            st.altair_chart(time_chart, use_container_width=True)

        # Platform comparison
        if selected_platform == "All Platforms":
            st.subheader("📱 Platform Comparison")
            platform_metrics = df.groupby('platform').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum'
            }).reset_index()

            # Create bar chart for platform comparison
            platform_chart = alt.Chart(platform_metrics).mark_bar().encode(
                x='platform:N',
                y='impressions:Q',
                color='platform:N',
                tooltip=['platform', 'impressions', 'clicks', 'conversions']
            ).properties(
                height=300
            )

            st.altair_chart(platform_chart, use_container_width=True)

        # Detailed metrics table
        st.subheader("📋 Detailed Metrics")
        daily_metrics = df.groupby(['date', 'platform']).agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'shares': 'sum',
            'comments': 'sum',
            'conversions': 'sum',
            'ctr': 'mean',
            'conversion_rate': 'mean'
        }).round(2).reset_index()

        st.dataframe(
            daily_metrics.sort_values('date', ascending=False),
            use_container_width=True
        )

        # Campaign Content Performance
        st.subheader("📑 Content Performance")
        content_list = self.db.get_campaign_content(selected_campaign['id'])
        
        if content_list:
            for content in content_list:
                with st.expander(f"Content: {content['content_type']} ({content['created_at']})"):
                    st.write("**Type:** ", content['content_type'])
                    st.write("**Tone:** ", content['tone'])
                    if content.get('hashtags'):
                        st.write("**Hashtags:** ", ", ".join(eval(content['hashtags'])))
                    if content.get('keywords'):
                        st.write("**Keywords:** ", ", ".join(eval(content['keywords'])))
                    
                    # Generate mock metrics for this content
                    content_metrics = {
                        "Impressions": random.randint(1000, 5000),
                        "Clicks": random.randint(50, 200),
                        "Engagement Rate": f"{random.uniform(1, 5):.2f}%",
                        "Conversions": random.randint(5, 20)
                    }
                    
                    # Display metrics in columns
                    cols = st.columns(len(content_metrics))
                    for col, (metric, value) in zip(cols, content_metrics.items()):
                        col.metric(metric, value)

    def record_metric(self, campaign_id: int, metric_name: str, value: float, content_id: Optional[int] = None):
        """Record a new analytics metric"""
        self.db.save_analytics(campaign_id, metric_name, value, content_id) 