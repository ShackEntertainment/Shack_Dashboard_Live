# 5_Partnerships.py - SHACK ENTERTAINMENT PARTNERSHIP COMMAND CENTER (FIXED)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import os
import base64
import random

st.set_page_config(page_title="Partnerships | Shack", page_icon="🤝", layout="wide", initial_sidebar_state="expanded")

# --- ASSET LOADER ---
def get_base64_image_safe(filename):
    try:
        paths = [os.path.join(os.path.dirname(__file__), '..', 'assets', filename), os.path.join(os.getcwd(), 'assets', filename)]
        for path in paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except: pass
    return None

logo_b64 = get_base64_image_safe('shack_main.png')

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #4CAF50; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    .kpi-card.orange { background: linear-gradient(145deg, #26231e 0%, #181614 100%); border-bottom: 4px solid #FF9800; }
    .kpi-card.cyan { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #00ACC1; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #F44336; }
    .kpi-label { font-size: 0.75em; color: #8b92a8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    .metric-detail { font-size: 0.8em; color: #8b92a8; margin-top: 8px; padding-top: 8px; border-top: 1px solid #2d323e; }
    .partner-card { background-color: #1e2330; border: 1px solid #2d323e; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; width: 100%; margin: 5px 0; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- COMPREHENSIVE PARTNERSHIP DATA ---
@st.cache_data
def load_partnership_data():
    # Active partnerships
    partners_data = []
    partner_names = ['Gallery West London', 'Live Nation UK', 'Arts Council England', 'Bristol Culture', 'Tate Modern', 'Royal Opera House', 'BBC Arts', 'Time Out London']
    partnership_types = ['Sponsorship', 'Collaboration', 'Licensing', 'Venue Partnership', 'Media Partnership', 'Educational']
    
    for i, partner in enumerate(partner_names):
        value = random.uniform(5000, 25000)
        partners_data.append({
            'Partner': partner,
            'Type': partnership_types[i % len(partnership_types)],
            'Status': random.choice(['Active', 'Active', 'Active', 'Pending', 'Renewal']),
            'Value': round(value, 2),
            'Start Date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%d/%m/%Y'),
            'End Date': (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%d/%m/%Y'),
            'ROI': round(random.uniform(1.2, 4.5), 1),
            'Contact': f"contact{i+1}@partner.com",
            'Projects': random.randint(1, 8)
        })
    
    # Sponsorship pipeline - FIXED: Using double quotes for names with apostrophes
    pipeline_data = []
    prospects = ["Victoria & Albert Museum", "Southbank Centre", "Barbican Centre", "Sadler's Wells", "National Theatre"]
    for prospect in prospects:
        pipeline_data.append({
            'Prospect': prospect,
            'Stage': random.choice(['Initial Contact', 'Proposal Sent', 'Negotiation', 'Contract Review', 'Final Approval']),
            'Estimated Value': round(random.uniform(10000, 50000), 2),
            'Probability': random.choice([25, 50, 60, 75, 90]),
            'Expected Close': (datetime.now() + timedelta(days=random.randint(30, 180))).strftime('%d/%m/%Y')
        })
    
    # Collaboration projects
    projects_data = []
    project_names = ['Summer Arts Festival 2026', 'Digital Innovation Lab', 'Youth Outreach Program', 'International Exchange', 'Sustainability Initiative']
    for project in project_names:
        projects_data.append({
            'Project': project,
            'Partners': random.choice(['Gallery West + Tate', 'BBC Arts + Time Out', 'Arts Council + Live Nation']),
            'Budget': round(random.uniform(15000, 75000), 2),
            'Status': random.choice(['Planning', 'Active', 'Completed', 'On Hold']),
            'Timeline': f"{random.randint(1,6)} months",
            'Impact Score': random.randint(6, 10)
        })
    
    # Revenue by partnership type
    revenue_by_type = {
        'Sponsorship': 45000,
        'Collaboration': 32000,
        'Licensing': 18500,
        'Venue Partnership': 28000,
        'Media Partnership': 15000,
        'Educational': 12000
    }
    
    return pd.DataFrame(partners_data), pd.DataFrame(pipeline_data), pd.DataFrame(projects_data), revenue_by_type

# --- SIDEBAR ---
with st.sidebar:
    if logo_b64: st.markdown(f'<div style="text-align:center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_b64}" width="140"></div>', unsafe_allow_html=True)
    else: st.markdown("### 🤝 Shack Entertainment")
    
    st.markdown("### 🤝 Partnership Command")
    st.markdown("*Strategic Alliance Management*")
    st.markdown("---")
    
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Sync Partnership Data", use_container_width=True):
        with st.spinner("Syncing all partnerships..."): 
            st.cache_data.clear()
            st.success("✅ All partnership data synced")
            st.rerun()
    
    if st.button("📝 Add New Partner", use_container_width=True):
        st.info("📝 **Partner Portal:** Opening partner registration form...")
    
    if st.button("📊 Generate Partnership Report", use_container_width=True):
        st.success("📊 Q2 2026 Partnership Report downloaded")
    
    if st.button("🤝 Schedule Partner Meeting", use_container_width=True):
        st.info("🤝 **Calendar:** Scheduling quarterly partner review...")
    
    if st.button("💼 Create Proposal", use_container_width=True):
        st.info("💼 **Proposal Builder:** Opening template...")
    
    st.markdown("---")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    st.caption("© 2026 Shack Entertainment | PARTNERSHIP MODE")

# --- HEADER ---
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if logo_b64: st.markdown(f'<div style="margin-top:10px;"><img src="data:image/png;base64,{logo_b64}" width="60"></div>', unsafe_allow_html=True)
    else: st.markdown("### 🤝")
with col_title:
    st.title("Partnerships")
    st.markdown(f"*Strategic Alliance & Sponsorship Management* |  {datetime.now().strftime('%d %B %Y')}")
st.markdown("---")

# --- LOAD DATA ---
partners_df, pipeline_df, projects_df, revenue_by_type = load_partnership_data()

# --- CALCULATE METRICS ---
total_partners = len(partners_df)
active_partnerships = len(partners_df[partners_df['Status'] == 'Active'])
total_partnership_value = partners_df['Value'].sum()
avg_roi = partners_df['ROI'].mean()
pipeline_value = pipeline_df['Estimated Value'].sum()
weighted_pipeline = (pipeline_df['Estimated Value'] * (pipeline_df['Probability'] / 100)).sum()
active_projects = len(projects_df[projects_df['Status'] == 'Active'])

# === TABS ===
tab_overview, tab_partners, tab_pipeline, tab_projects, tab_revenue = st.tabs([
    "📊 Partnership Overview",
    "👥 Partner Directory",
    "🎯 Sales Pipeline",
    "🚀 Collaboration Projects",
    "💰 Revenue Analytics"
])

# === TAB 1: OVERVIEW ===
with tab_overview:
    st.markdown("### 🎯 Partnership Performance Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card green">
            <div style="font-size: 35px; margin-bottom: 8px;">🤝</div>
            <div class="kpi-label">ACTIVE PARTNERS</div>
            <div class="kpi-value">{active_partnerships}</div>
            <div class="kpi-delta">↑ +3 this quarter</div>
            <div class="metric-detail">Of {total_partners} total partners</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div style="font-size: 35px; margin-bottom: 8px;">💷</div>
            <div class="kpi-label">TOTAL VALUE</div>
            <div class="kpi-value">£{total_partnership_value:,.2f}</div>
            <div class="kpi-delta">↑ +18% vs last quarter</div>
            <div class="metric-detail">Annual partnership revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div style="font-size: 35px; margin-bottom: 8px;">📈</div>
            <div class="kpi-label">AVG ROI</div>
            <div class="kpi-value">{avg_roi:.1f}x</div>
            <div class="kpi-delta">↑ +0.4x improvement</div>
            <div class="metric-detail">Return on partnership investment</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card orange">
            <div style="font-size: 35px; margin-bottom: 8px;">🎯</div>
            <div class="kpi-label">PIPELINE VALUE</div>
            <div class="kpi-value">£{weighted_pipeline:,.0f}</div>
            <div class="kpi-delta">Weighted forecast</div>
            <div class="metric-detail">Total: £{pipeline_value:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"""
        <div class="kpi-card cyan">
            <div style="font-size: 35px; margin-bottom: 8px;">🚀</div>
            <div class="kpi-label">ACTIVE PROJECTS</div>
            <div class="kpi-value">{active_projects}</div>
            <div class="kpi-delta">{len(projects_df)} total projects</div>
            <div class="metric-detail">Cross-partner collaborations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="kpi-card red">
            <div style="font-size: 35px; margin-bottom: 8px;">⏰</div>
            <div class="kpi-label">RENEWALS DUE</div>
            <div class="kpi-value">{len(partners_df[partners_df['Status'] == 'Renewal'])}</div>
            <div class="kpi-delta" style="color: #F44336;">Action required</div>
            <div class="metric-detail">Next 90 days</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Partnership Growth Chart
    st.markdown("### 📈 Partnership Growth Trend")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    growth_data = pd.DataFrame({
        'Month': months,
        'Active Partners': [5, 6, 7, 8, 9, 10],
        'New Partnerships': [1, 2, 1, 2, 1, 2]
    })
    
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Bar(x=growth_data['Month'], y=growth_data['New Partnerships'], name='New Partnerships', marker_color='#2196F3'))
    fig_growth.add_trace(go.Scatter(x=growth_data['Month'], y=growth_data['Active Partners'], name='Active Partners', line=dict(color='#4CAF50', width=3)))
    fig_growth.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=350, legend=dict(x=0, y=1))
    st.plotly_chart(fig_growth, use_container_width=True)

# === TAB 2: PARTNER DIRECTORY ===
with tab_partners:
    st.markdown("### 👥 Partner Directory & Management")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search partners...", key="partner_search")
    with col2:
        filter_type = st.selectbox("Filter by Type", ["All"] + list(partners_df['Type'].unique()))
    
    display_partners = partners_df.copy()
    if search:
        display_partners = display_partners[display_partners['Partner'].str.contains(search, case=False, na=False)]
    if filter_type != "All":
        display_partners = display_partners[display_partners['Type'] == filter_type]
    
    st.markdown(f"**{len(display_partners)} partners found**")
    st.markdown("---")
    
    for idx, row in display_partners.iterrows():
        with st.expander(f"**{row['Partner']}** - {row['Type']} | Value: £{row['Value']:,.2f} | ROI: {row['ROI']}x", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.metric("Partnership Value", f"£{row['Value']:,.2f}")
            col2.metric("ROI", f"{row['ROI']}x")
            col3.metric("Projects", row['Projects'])
            
            col4, col5 = st.columns(2)
            col4.write(f"**Status:** {row['Status']}")
            col5.write(f"**Contact:** {row['Contact']}")
            
            st.write(f"**Duration:** {row['Start Date']} - {row['End Date']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📧 Contact Partner", key=f"contact_{idx}"):
                    st.success(f"📧 Email opened for {row['Partner']}")
            with col_b:
                if st.button("📊 View Performance", key=f"perf_{idx}"):
                    st.info(f"📊 Performance report for {row['Partner']}")
    
    st.markdown("---")
    if st.button("📥 Export Partner Directory", use_container_width=True):
        csv = partners_df.to_csv(index=False)
        st.download_button("Download CSV", csv, "partners.csv", "text/csv")

# === TAB 3: SALES PIPELINE ===
with tab_pipeline:
    st.markdown("### 🎯 Partnership Sales Pipeline")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pipeline Value", f"£{pipeline_value:,.2f}")
    col2.metric("Weighted Value", f"£{weighted_pipeline:,.2f}", delta=f"{len(pipeline_df)} prospects")
    col3.metric("Avg Deal Size", f"£{pipeline_df['Estimated Value'].mean():,.2f}")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Pipeline by Stage")
    stage_summary = pipeline_df.groupby('Stage')['Estimated Value'].sum().reset_index()
    
    fig_pipeline = px.bar(stage_summary, x='Stage', y='Estimated Value', 
                          color='Estimated Value', color_continuous_scale='Blues')
    fig_pipeline.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=350, showlegend=False)
    st.plotly_chart(fig_pipeline, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Active Prospects")
    for idx, row in pipeline_df.iterrows():
        cols = st.columns([3, 2, 2, 2, 2, 1])
        cols[0].write(f"**{row['Prospect']}**")
        cols[1].write(f"Stage: {row['Stage']}")
        cols[2].write(f"Value: £{row['Estimated Value']:,.2f}")
        cols[3].write(f"Probability: {row['Probability']}%")
        cols[4].write(f"Close: {row['Expected Close']}")
        if cols[5].button("View", key=f"view_{idx}"):
            st.info(f"Details for {row['Prospect']}")
    
    st.markdown("---")
    if st.button("➕ Add New Prospect", use_container_width=True):
        st.info("➕ **New Prospect:** Opening intake form...")

# === TAB 4: COLLABORATION PROJECTS ===
with tab_projects:
    st.markdown("### 🚀 Collaboration Projects")
    
    col1, col2, col3 = st.columns(3)
    total_budget = projects_df['Budget'].sum()
    col1.metric("Total Project Budget", f"£{total_budget:,.2f}")
    col2.metric("Active Projects", active_projects)
    col3.metric("Avg Impact Score", f"{projects_df['Impact Score'].mean():.1f}/10")
    
    st.markdown("---")
    
    for idx, row in projects_df.iterrows():
        status_color = "green" if row['Status'] == "Completed" else "blue" if row['Status'] == "Active" else "orange"
        
        st.markdown(f"""
        <div class="partner-card" style="border-left: 4px solid {'#4CAF50' if row['Status'] == 'Completed' else '#2196F3' if row['Status'] == 'Active' else '#FF9800'};">
            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">{row['Project']}</div>
            <div style="color: #8b92a8; margin-bottom: 10px;"><strong>Partners:</strong> {row['Partners']}</div>
            <div style="display: flex; justify-content: space-between;">
                <div><strong>Budget:</strong> £{row['Budget']:,.2f}</div>
                <div><strong>Timeline:</strong> {row['Timeline']}</div>
                <div><strong>Impact:</strong> {row['Impact Score']}/10</div>
                <div><strong>Status:</strong> {row['Status']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        progress = 100 if row['Status'] == 'Completed' else 60 if row['Status'] == 'Active' else 20
        st.progress(progress / 100)
        st.markdown("---")
    
    if st.button("📊 Export Project Portfolio", use_container_width=True):
        csv = projects_df.to_csv(index=False)
        st.download_button("Download CSV", csv, "projects.csv", "text/csv")

# === TAB 5: REVENUE ANALYTICS ===
with tab_revenue:
    st.markdown("### 💰 Partnership Revenue Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Revenue by Partnership Type")
        rev_df = pd.DataFrame({
            'Type': list(revenue_by_type.keys()),
            'Revenue': list(revenue_by_type.values())
        })
        
        fig_pie = px.pie(rev_df, values='Revenue', names='Type', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### Revenue Breakdown")
        for ptype, amount in revenue_by_type.items():
            percentage = (amount / sum(revenue_by_type.values()) * 100)
            st.markdown(f"""
            <div class="kpi-card blue" style="margin-bottom: 10px;">
                <div class="kpi-label">{ptype.upper()}</div>
                <div class="kpi-value">£{amount:,.2f}</div>
                <div class="kpi-delta">{percentage:.1f}% of total</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 📈 Partner ROI Analysis")
    roi_df = partners_df.sort_values('ROI', ascending=True)
    
    fig_roi = px.bar(roi_df, x='ROI', y='Partner', orientation='h',
                     color='ROI', color_continuous_scale='RdYlGn')
    fig_roi.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=400,
                          xaxis_title='ROI (x)', yaxis_title='Partner')
    st.plotly_chart(fig_roi, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 💡 Partnership Insights")
    col1, col2, col3 = st.columns(3)
    col1.info("💡 **Top Performer:** Gallery West London - 4.5x ROI")
    col2.info("💡 **Growth Area:** Educational partnerships up 35%")
    col3.info("💡 **Opportunity:** 3 renewals due in Q3 - £45k value")

st.markdown("---")
st.caption("Shack Entertainment | Partnership Command Center | Strategic Alliance Management")