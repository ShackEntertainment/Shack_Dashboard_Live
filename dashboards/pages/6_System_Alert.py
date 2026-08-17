# 6_System_Alert.py - SHACK ENTERTAINMENT SYSTEM MONITORING
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import os
import base64
import random

st.set_page_config(page_title="System Alert | Shack", page_icon="🚨", layout="wide", initial_sidebar_state="expanded")

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

logo_b64 = get_base64_image_safe('shack_trans.png')

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stApp { background-color: #0e1117 !important; }
    header { visibility: hidden; }
    [data-testid="stHeader"] { background-color: #0e1117; padding: 0; }
    /* [data-testid="stToolbar"] { visibility: hidden; } */
    [data-testid="stSidebar"] a, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #e2e8f0 !important; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #4CAF50; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #F44336; }
    .kpi-card.yellow { background: linear-gradient(145deg, #26231e 0%, #181614 100%); border-bottom: 4px solid #FFC107; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    .kpi-label { font-size: 0.75em; color: #8b92a8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    .metric-detail { font-size: 0.8em; color: #8b92a8; margin-top: 8px; padding-top: 8px; border-top: 1px solid #2d323e; }
    .alert-critical { background-color: rgba(244, 67, 54, 0.2); border-left: 4px solid #F44336; padding: 10px; margin: 10px 0; border-radius: 5px; }
    .alert-warning { background-color: rgba(255, 193, 7, 0.2); border-left: 4px solid #FFC107; padding: 10px; margin: 10px 0; border-radius: 5px; }
    .alert-info { background-color: rgba(33, 150, 243, 0.2); border-left: 4px solid #2196F3; padding: 10px; margin: 10px 0; border-radius: 5px; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; width: 100%; margin: 5px 0; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)






# --- NAVIGATION BAR ---

current = "Alerts"  # auto-detected from filename
cols = st.columns(8)
for i, (name, path, label) in enumerate([
    ("Home", r"Home.py", "Home"),
    ("Artists", r"pages/1_Artists_Unlimited.py", "Artists"),
    ("Live Exchange", r"pages/2_Live_Exchange.py", "Live Exchange"),
    ("News Network", r"pages/3_News_Network.py", "News Network"),
    ("Finance", r"pages/4_Financial_Overview.py", "Finance"),
    ("Partnerships", r"pages/5_Partnerships.py", "Partnerships"),
    ("Alerts", r"pages/6_System_Alert.py", "Alerts"),
    ("Command", r"pages/7_Command_Center.py", "Command"),
]):
    with cols[i]:
        if name == current:
            st.button(label, disabled=True, use_container_width=True, type="primary")
        else:
            if st.button(label, use_container_width=True):
                st.switch_page(path)
st.markdown("---")


# --- SYSTEM DATA GENERATORS ---
@st.cache_data
def load_system_data():
    # System health metrics
    system_health = {
        'Database': {'status': 'Online', 'uptime': '99.98%', 'response_time': '45ms', 'last_check': datetime.now()},
        'API Gateway': {'status': 'Online', 'uptime': '99.95%', 'response_time': '120ms', 'last_check': datetime.now()},
        'File Storage': {'status': 'Online', 'uptime': '99.99%', 'response_time': '30ms', 'last_check': datetime.now()},
        'Email Service': {'status': 'Degraded', 'uptime': '98.50%', 'response_time': '850ms', 'last_check': datetime.now()},
        'Payment Gateway': {'status': 'Online', 'uptime': '99.97%', 'response_time': '200ms', 'last_check': datetime.now()},
        'CDN': {'status': 'Online', 'uptime': '99.99%', 'response_time': '25ms', 'last_check': datetime.now()}
    }
    
    # Active alerts
    alerts_data = []
    alert_types = ['Critical', 'Warning', 'Info']
    alert_messages = [
        'Database connection pool near capacity (85%)',
        'Email service response time elevated',
        'API rate limit approaching threshold (75%)',
        'Storage usage at 78% capacity',
        'Scheduled maintenance in 2 hours',
        'New user registration spike detected',
        'Cache hit ratio below optimal (65%)',
        'SSL certificate expires in 45 days'
    ]
    
    for i in range(8):
        alerts_data.append({
            'Timestamp': (datetime.now() - timedelta(minutes=random.randint(5, 480))).strftime('%Y-%m-%d %H:%M:%S'),
            'Severity': random.choice(alert_types),
            'Component': random.choice(['Database', 'API', 'Email', 'Storage', 'Payment', 'CDN']),
            'Message': alert_messages[i],
            'Status': random.choice(['Active', 'Acknowledged', 'Resolved'])
        })
    
    # Error logs
    error_logs = []
    error_types = ['Error', 'Warning', 'Critical', 'Info']
    for i in range(20):
        error_logs.append({
            'Timestamp': (datetime.now() - timedelta(hours=random.randint(0, 168))).strftime('%Y-%m-%d %H:%M:%S'),
            'Level': random.choice(error_types),
            'Component': random.choice(['Auth', 'Database', 'API', 'Frontend', 'Payment', 'Email']),
            'Message': f"{'Error' if random.random() > 0.5 else 'Warning'} in module {random.randint(1, 10)}: {random.choice(['Connection timeout', 'Null pointer', 'Validation failed', 'Rate limit exceeded', 'Auth failed'])}",
            'User': f"user{random.randint(1000, 9999)}"
        })
    
    # Performance metrics (last 24 hours)
    perf_data = []
    for hour in range(24):
        perf_data.append({
            'Hour': f"{hour:02d}:00",
            'Response Time (ms)': random.uniform(50, 250),
            'Requests': random.randint(100, 500),
            'Error Rate (%)': random.uniform(0.1, 2.5)
        })
    
    # Uptime history (last 30 days)
    uptime_data = []
    for day in range(30):
        uptime_data.append({
            'Date': (datetime.now() - timedelta(days=29-day)).strftime('%m/%d'),
            'Uptime (%)': random.uniform(99.5, 100),
            'Downtime (min)': random.randint(0, 15)
        })
    
    # Active users
    user_sessions = {
        'Current Active': random.randint(45, 120),
        'Peak Today': random.randint(150, 300),
        'Avg Session': f"{random.randint(5, 15)} min",
        'Bounce Rate': f"{random.uniform(25, 45):.1f}%"
    }
    
    return system_health, pd.DataFrame(alerts_data), pd.DataFrame(error_logs), pd.DataFrame(perf_data), pd.DataFrame(uptime_data), user_sessions

# --- SIDEBAR ---
with st.sidebar:
    if logo_b64: st.markdown(f'<div style="text-align:center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_b64}" width="140"></div>', unsafe_allow_html=True)
    else: st.markdown("### 🚨 Shack Entertainment")
    
    st.markdown("### 🚨 System Monitor")
    st.markdown("*Backend Health & Operations*")
    st.markdown("---")
    
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Refresh All Metrics", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ All system metrics refreshed")
        st.rerun()
    
    if st.button("📊 Generate System Report", use_container_width=True):
        st.success("📊 System health report downloaded")
    
    if st.button("🔔 Test Alert System", use_container_width=True):
        st.info("🔔 **Test Alert:** Notification sent to admin@shack.com")
    
    if st.button("🗑️ Clear Resolved Alerts", use_container_width=True):
        st.success("🗑️ 12 resolved alerts archived")
    
    if st.button("⚙️ System Settings", use_container_width=True):
        st.info("⚙️ **Settings:** Opening configuration panel...")
    
    st.markdown("---")
    st.caption("© 2026 Shack Entertainment | SYSTEM MONITORING ACTIVE")

# --- HEADER ---
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if logo_b64: st.markdown(f'<div style="margin-top:10px;"><img src="data:image/png;base64,{logo_b64}" width="60"></div>', unsafe_allow_html=True)
    else: st.markdown("### 🚨")
with col_title:
    st.title("System Alert")
    st.markdown(f"*Backend Health & Operations Monitoring* |  {datetime.now().strftime('%d %B %Y | %H:%M:%S')}")
st.markdown("---")

# --- LOAD DATA ---
system_health, alerts_df, error_logs_df, perf_df, uptime_df, user_sessions = load_system_data()

# --- CALCULATE METRICS ---
total_alerts = len(alerts_df[alerts_df['Status'] == 'Active'])
critical_alerts = len(alerts_df[(alerts_df['Severity'] == 'Critical') & (alerts_df['Status'] == 'Active')])
avg_response_time = perf_df['Response Time (ms)'].mean()
avg_uptime = uptime_df['Uptime (%)'].mean()
total_errors = len(error_logs_df[error_logs_df['Level'] == 'Error'])

# === TABS ===
tab_overview, tab_health, tab_alerts, tab_logs, tab_performance = st.tabs([
    "📊 System Overview",
    "💚 Service Health",
    "🚨 Active Alerts",
    "📝 Error Logs",
    "📈 Performance"
])

# === TAB 1: SYSTEM OVERVIEW ===
with tab_overview:
    st.markdown("### 🎯 System Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card green">
            <div style="font-size: 35px; margin-bottom: 8px;">💚</div>
            <div class="kpi-label">SYSTEM STATUS</div>
            <div class="kpi-value">{"OPERATIONAL" if critical_alerts == 0 else "DEGRADED"}</div>
            <div class="kpi-delta">{len(system_health)} services online</div>
            <div class="metric-detail">All systems functional</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card yellow">
            <div style="font-size: 35px; margin-bottom: 8px;">🚨</div>
            <div class="kpi-label">ACTIVE ALERTS</div>
            <div class="kpi-value">{total_alerts}</div>
            <div class="kpi-delta" style="color: {'#F44336' if critical_alerts > 0 else '#4CAF50'};">{critical_alerts} critical</div>
            <div class="metric-detail">Requires attention</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div style="font-size: 35px; margin-bottom: 8px;">⚡</div>
            <div class="kpi-label">AVG RESPONSE</div>
            <div class="kpi-value">{avg_response_time:.0f}ms</div>
            <div class="kpi-delta">↓ -12ms vs yesterday</div>
            <div class="metric-detail">24-hour average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div style="font-size: 35px; margin-bottom: 8px;">📊</div>
            <div class="kpi-label">UPTIME (30D)</div>
            <div class="kpi-value">{avg_uptime:.2f}%</div>
            <div class="kpi-delta">↑ +0.05% improvement</div>
            <div class="metric-detail">Industry standard: 99.9%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"""
        <div class="kpi-card green">
            <div style="font-size: 35px; margin-bottom: 8px;">👥</div>
            <div class="kpi-label">{user_sessions['Current Active']}</div>
            <div class="kpi-label">ACTIVE USERS</div>
            <div class="kpi-delta">Peak today: {user_sessions['Peak Today']}</div>
            <div class="metric-detail">Avg session: {user_sessions['Avg Session']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="kpi-card red">
            <div style="font-size: 35px; margin-bottom: 8px;">⚠️</div>
            <div class="kpi-label">{total_errors}</div>
            <div class="kpi-label">ERRORS (7D)</div>
            <div class="kpi-delta">↓ -8 vs last week</div>
            <div class="metric-detail">Error rate trending down</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status Timeline
    st.markdown("### 📈 System Performance (24 Hours)")
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(x=perf_df['Hour'], y=perf_df['Response Time (ms)'], mode='lines', name='Response Time', line=dict(color='#2196F3', width=2)))
    fig_perf.add_trace(go.Scatter(x=perf_df['Hour'], y=perf_df['Error Rate (%)'], mode='lines', name='Error Rate %', line=dict(color='#F44336', width=2), yaxis='y2'))
    fig_perf.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=350, 
                           yaxis=dict(title='Response Time (ms)', gridcolor='#262730'),
                           yaxis2=dict(title='Error Rate (%)', overlaying='y', side='right', gridcolor='#262730'),
                           legend=dict(x=0, y=1))
    st.plotly_chart(fig_perf, use_container_width=True)

# === TAB 2: SERVICE HEALTH ===
with tab_health:
    st.markdown("### 💚 Service Health Status")
    
    for service, metrics in system_health.items():
        status_color = "green" if metrics['status'] == "Online" else "yellow" if metrics['status'] == "Degraded" else "red"
        status_emoji = "✅" if metrics['status'] == "Online" else "⚠️" if metrics['status'] == "Degraded" else "❌"
        
        st.markdown(f"""
        <div class="kpi-card {status_color}" style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 1.3em; font-weight: bold;">{status_emoji} {service}</div>
                <div style="font-size: 1.1em; color: {'#4CAF50' if metrics['status'] == 'Online' else '#FFC107' if metrics['status'] == 'Degraded' else '#F44336'};">
                    {metrics['status']}
                </div>
            </div>
            <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                <div><strong>Uptime:</strong> {metrics['uptime']}</div>
                <div><strong>Response:</strong> {metrics['response_time']}</div>
                <div><strong>Last Check:</strong> {metrics['last_check'].strftime('%H:%M:%S')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Uptime History Chart
    st.markdown("### 📊 30-Day Uptime History")
    fig_uptime = go.Figure()
    fig_uptime.add_trace(go.Scatter(x=uptime_df['Date'], y=uptime_df['Uptime (%)'], mode='lines+markers', 
                                     name='Uptime %', line=dict(color='#4CAF50', width=2), fill='tozeroy', fillcolor='rgba(76,175,80,0.1)'))
    fig_uptime.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=300, 
                             yaxis=dict(title='Uptime (%)', range=[99, 100], gridcolor='#262730'))
    st.plotly_chart(fig_uptime, use_container_width=True)

# === TAB 3: ACTIVE ALERTS ===
with tab_alerts:
    st.markdown("### 🚨 Active Alerts & Notifications")
    
    # Alert summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active", total_alerts)
    col2.metric("Critical", critical_alerts, delta_color="inverse" if critical_alerts > 0 else "normal")
    col3.metric("Acknowledged", len(alerts_df[alerts_df['Status'] == 'Acknowledged']))
    
    st.markdown("---")
    
    # Filter alerts
    filter_severity = st.multiselect("Filter by Severity", ['Critical', 'Warning', 'Info'], default=['Critical', 'Warning', 'Info'])
    
    display_alerts = alerts_df[alerts_df['Severity'].isin(filter_severity)]
    
    for idx, row in display_alerts.iterrows():
        alert_class = "alert-critical" if row['Severity'] == "Critical" else "alert-warning" if row['Severity'] == "Warning" else "alert-info"
        
        st.markdown(f"""
        <div class="{alert_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{row['Severity'].upper()}</strong> - {row['Component']}
                    <div style="margin-top: 5px; color: #8b92a8;">{row['Message']}</div>
                </div>
                <div style="color: #8b92a8; font-size: 0.9em;">{row['Timestamp']}</div>
            </div>
            <div style="margin-top: 10px;">
                <span style="background-color: {'#F44336' if row['Status'] == 'Active' else '#4CAF50' if row['Status'] == 'Resolved' else '#FFC107'}; 
                             padding: 3px 10px; border-radius: 3px; font-size: 0.85em;">{row['Status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("📧 Email Alert Summary", use_container_width=True):
        st.success("📧 Alert summary sent to operations team")

# === TAB 4: ERROR LOGS ===
with tab_logs:
    st.markdown("### 📝 Error Logs & Debugging")
    
    # Log statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Errors", len(error_logs_df[error_logs_df['Level'] == 'Error']))
    col2.metric("Warnings", len(error_logs_df[error_logs_df['Level'] == 'Warning']))
    col3.metric("Critical", len(error_logs_df[error_logs_df['Level'] == 'Critical']))
    
    st.markdown("---")
    
    # Filter logs
    col1, col2 = st.columns([3, 1])
    with col1:
        search_log = st.text_input("🔍 Search logs...", key="log_search")
    with col2:
        filter_level = st.selectbox("Level", ["All", "Critical", "Error", "Warning", "Info"])
    
    display_logs = error_logs_df.copy()
    if search_log:
        display_logs = display_logs[display_logs['Message'].str.contains(search_log, case=False, na=False)]
    if filter_level != "All":
        display_logs = display_logs[display_logs['Level'] == filter_level]
    
    st.dataframe(display_logs, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Logs (CSV)", use_container_width=True):
            csv = error_logs_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "error_logs.csv", "text/csv")
    with col2:
        if st.button("🗑️ Clear Old Logs", use_container_width=True):
            st.success("🗑️ Logs older than 30 days archived")

# === TAB 5: PERFORMANCE ===
with tab_performance:
    st.markdown("### 📈 Performance Analytics")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Response Time", f"{avg_response_time:.0f}ms", delta="-12ms faster")
    col2.metric("Total Requests (24h)", f"{perf_df['Requests'].sum():,}")
    col3.metric("Avg Error Rate", f"{perf_df['Error Rate (%)'].mean():.2f}%", delta="-0.3% improvement")
    
    st.markdown("---")
    
    # Response time distribution
    st.markdown("#### Response Time Distribution")
    fig_hist = px.histogram(perf_df, x='Response Time (ms)', nbins=20, 
                            color_discrete_sequence=['#2196F3'])
    fig_hist.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=300)
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    
    # Request volume
    st.markdown("#### Request Volume (24 Hours)")
    fig_requests = go.Figure()
    fig_requests.add_trace(go.Bar(x=perf_df['Hour'], y=perf_df['Requests'], 
                                   marker_color='#4CAF50', name='Requests'))
    fig_requests.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=300, 
                               xaxis=dict(gridcolor='#262730'), yaxis=dict(gridcolor='#262730'))
    st.plotly_chart(fig_requests, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 💡 Performance Insights")
    col1, col2, col3 = st.columns(3)
    col1.info("💡 **Peak Hours:** 14:00-16:00 (highest traffic)")
    col2.info("💡 **Fastest Service:** CDN (25ms avg)")
    col3.info("💡 **Optimization:** Enable caching for 15% improvement")

st.markdown("---")
st.caption("Shack Entertainment | System Monitoring | Backend Health Operations | Last updated: " + datetime.now().strftime('%H:%M:%S'))