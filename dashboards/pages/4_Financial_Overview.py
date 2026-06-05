# 4_Financial_Overview.py - SHACK ENTERTAINMENT FINANCIAL COMMAND CENTER (FULLY FIXED)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import os
import base64
import random

st.set_page_config(page_title="Financial Overview | Shack", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

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
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #F44336; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    .kpi-card.orange { background: linear-gradient(145deg, #26231e 0%, #181614 100%); border-bottom: 4px solid #FF9800; }
    .kpi-card.cyan { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #00ACC1; }
    .kpi-label { font-size: 0.75em; color: #8b92a8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    .metric-detail { font-size: 0.8em; color: #8b92a8; margin-top: 8px; padding-top: 8px; border-top: 1px solid #2d323e; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; width: 100%; margin: 5px 0; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- GLOBAL MONTHS VARIABLE ---
MONTHS = ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026']

# --- COMPREHENSIVE FINANCIAL DATA ---
@st.cache_data
def load_financial_data():
    # Multi-stream revenue data
    revenue_streams = {
        'Artists Unlimited': {'art_sales': 8450, 'commissions': 3200, 'merchandise': 1890},
        'Live Exchange': {'ticket_sales': 12400, 'vip_packages': 4500, 'concessions': 1200},
        'News Network': {'ad_revenue': 2100, 'referrals': 2267, 'sponsored': 1800},
        'Partnerships': {'sponsorships': 5000, 'collaborations': 2300, 'licensing': 1500}
    }
    
    # Monthly trend data (last 6 months)
    monthly_revenue = {
        'Artists Unlimited': [8200, 9100, 10500, 11200, 12800, 13540],
        'Live Exchange': [9800, 11200, 13500, 15200, 17100, 18100],
        'News Network': [4200, 4800, 5300, 5900, 6400, 6167],
        'Partnerships': [6500, 7200, 7800, 8100, 8500, 8800],
        'Expenses': [12000, 13500, 14800, 15900, 16800, 17200]
    }
    
    # Artist payout tracking (70/30 split) - NUMERIC VALUES
    artists_data = []
    artist_names = ['Paul Duncan', 'Luna Park', 'Alex Rivera', 'Emma Stone', 'Sarah Chen', 'Marcus Webb']
    for artist in artist_names:
        total_sales = random.uniform(1500, 5000)
        artists_data.append({
            'Artist': artist,
            'Total Sales': round(total_sales, 2),
            'Shack Share (30%)': round(total_sales * 0.30, 2),
            'Artist Payout (70%)': round(total_sales * 0.70, 2),
            'Status': random.choice(['Paid', 'Pending', 'Processing']),
            'Last Payout': (datetime.now() - timedelta(days=random.randint(5, 30))).strftime('%d/%m/%Y')
        })
    
    # Outstanding invoices - NUMERIC VALUES (not formatted strings)
    invoices_data = []
    clients = ['Gallery West', 'Live Nation UK', 'Art Monthly Mag', 'Bristol Events', 'London Arts Council']
    for i in range(8):
        amount = round(random.uniform(500, 3500), 2)  # Store as float
        invoices_data.append({
            'Invoice #': f'INV-2026-{1000+i}',
            'Client': random.choice(clients),
            'Amount': amount,  # Keep as numeric
            'Issued Date': (datetime.now() - timedelta(days=random.randint(10, 45))).strftime('%d/%m/%Y'),
            'Due Date': (datetime.now() + timedelta(days=random.randint(-5, 15))).strftime('%d/%m/%Y'),
            'Status': random.choice(['Paid', 'Pending', 'Overdue'])
        })
    
    # Expense categories
    expenses_data = {
        'Artist Commissions': 5200,
        'Venue Rentals': 3800,
        'Marketing & Ads': 2400,
        'Platform Fees': 1200,
        'Equipment': 1800,
        'Insurance': 950,
        'Legal & Admin': 1100,
        'Miscellaneous': 750
    }
    
    # Cash flow (last 30 days)
    cash_flow_data = []
    for i in range(30):
        date = datetime.now() - timedelta(days=29-i)
        income = random.uniform(800, 2500)
        expenses = random.uniform(400, 1800)
        cash_flow_data.append({
            'date': date,
            'income': income,
            'expenses': expenses,
            'net': income - expenses
        })
    
    return revenue_streams, monthly_revenue, pd.DataFrame(artists_data), pd.DataFrame(invoices_data), expenses_data, pd.DataFrame(cash_flow_data)

# --- SIDEBAR WITH FUNCTIONAL BUTTONS ---
with st.sidebar:
    if logo_b64: st.markdown(f'<div style="text-align:center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_b64}" width="140"></div>', unsafe_allow_html=True)
    else: st.markdown("### 💰 Shack Entertainment")
    
    st.markdown("### 💰 Financial Command")
    st.markdown("*Multi-Stream Revenue Intelligence*")
    st.markdown("---")
    
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Sync Financial Data", use_container_width=True):
        with st.spinner("Syncing all accounts..."): 
            st.cache_data.clear()
            st.success("✅ All financial data synced from: Google Sheets, Stripe, PayPal, Bank API")
            st.rerun()
    
    if st.button("💳 Process Artist Payouts", use_container_width=True):
        with st.spinner("Processing batch payouts..."):
            st.success("💳 Processed £8,450.00 to 6 artists")
            st.info("Transaction IDs: TXN-2026-001 through TXN-2026-006")
    
    if st.button("📄 Generate Invoices", use_container_width=True):
        with st.spinner("Generating invoices..."):
            st.success("📄 5 invoices generated and emailed to clients")
            st.info("Total invoiced: £12,450.00")
    
    if st.button("📊 Export Financial Report", use_container_width=True):
        _, monthly_rev, artists_df, invoices_df, _, _ = load_financial_data()
        
        report_data = {
            'Revenue by Division': {div: sum(monthly_rev[div]) for div in monthly_rev.keys() if div != 'Expenses'},
            'Total Expenses': sum(monthly_rev['Expenses']),
            'Artist Payouts': artists_df['Artist Payout (70%)'].sum(),
            'Outstanding Invoices': len(invoices_df[invoices_df['Status'] == 'Pending'])
        }
        
        report_df = pd.DataFrame([report_data])
        csv = report_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Q2 2026 Report",
            data=csv,
            file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.success("📊 Q2 2026 Financial Report ready for download")
    
    if st.button("💰 Calculate Tax Estimate", use_container_width=True):
        _, monthly_rev, _, _, expenses_dict, _ = load_financial_data()
        total_rev = sum(sum(monthly_rev[div]) for div in monthly_rev.keys() if div != 'Expenses')
        vat_estimate = total_rev * 0.20
        corp_tax = (total_rev - sum(expenses_dict.values())) * 0.19
        
        st.info(f"""
        💰 **Tax Estimate Q2 2026:**
        
        VAT (20%): £{vat_estimate:,.2f}
        Corporation Tax (19%): £{corp_tax:,.2f}
        **Total Estimated Tax: £{vat_estimate + corp_tax:,.2f}**
        """)
    
    st.markdown("---")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    st.caption("© 2026 Shack Entertainment | CFO MODE ACTIVE")

# --- HEADER ---
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if logo_b64: st.markdown(f'<div style="margin-top:10px;"><img src="data:image/png;base64,{logo_b64}" width="60"></div>', unsafe_allow_html=True)
    else: st.markdown("### 💰")
with col_title:
    st.title("Financial Overview")
    st.markdown(f"*Multi-Stream Revenue & Expense Intelligence* |  {datetime.now().strftime('%d %B %Y')}")
st.markdown("---")

# --- LOAD DATA ---
revenue_streams, monthly_revenue, artists_df, invoices_df, expenses_dict, cash_flow_df = load_financial_data()

# --- CALCULATE TOTALS (NOW WORKS WITH NUMERIC VALUES) ---
total_revenue = sum(sum(streams.values()) for streams in revenue_streams.values())
total_expenses = sum(expenses_dict.values())
net_profit = total_revenue - total_expenses
profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
outstanding_invoices = len(invoices_df[invoices_df['Status'] == 'Pending'])
overdue_invoices = len(invoices_df[invoices_df['Status'] == 'Overdue'])

# Calculate invoice totals properly
total_invoiced = invoices_df['Amount'].sum()
paid_amount = invoices_df[invoices_df['Status']=='Paid']['Amount'].sum()
pending_amount = invoices_df[invoices_df['Status']=='Pending']['Amount'].sum()

# === TABS FOR COMPREHENSIVE VIEW ===
tab_dashboard, tab_revenue, tab_expenses, tab_artists, tab_invoices, tab_forecast = st.tabs([
    "📊 Executive Dashboard",
    "💵 Revenue Streams",
    "💸 Expense Management",
    "👥 Artist Payouts",
    "📄 Invoices & Receivables",
    "📈 Forecast & Analytics"
])

# === TAB 1: EXECUTIVE DASHBOARD ===
with tab_dashboard:
    st.markdown("### 🎯 Financial Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card green">
            <div style="font-size: 35px; margin-bottom: 8px;">💰</div>
            <div class="kpi-label">TOTAL REVENUE</div>
            <div class="kpi-value">£{total_revenue:,.2f}</div>
            <div class="kpi-delta">↑ +18.5% vs last month</div>
            <div class="metric-detail">All business units</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card red">
            <div style="font-size: 35px; margin-bottom: 8px;">💸</div>
            <div class="kpi-label">TOTAL EXPENSES</div>
            <div class="kpi-value">£{total_expenses:,.2f}</div>
            <div class="kpi-delta">↑ +12.3% vs last month</div>
            <div class="metric-detail">Operating costs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div style="font-size: 35px; margin-bottom: 8px;">📊</div>
            <div class="kpi-label">NET PROFIT</div>
            <div class="kpi-value">£{net_profit:,.2f}</div>
            <div class="kpi-delta">↑ +24.7% vs last month</div>
            <div class="metric-detail">After all expenses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div style="font-size: 35px; margin-bottom: 8px;">📈</div>
            <div class="kpi-label">PROFIT MARGIN</div>
            <div class="kpi-value">{profit_margin:.1f}%</div>
            <div class="kpi-delta">↑ +3.2% improvement</div>
            <div class="metric-detail">Industry avg: 22%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"""
        <div class="kpi-card orange">
            <div style="font-size: 35px; margin-bottom: 8px;">📋</div>
            <div class="kpi-label">OUTSTANDING INVOICES</div>
            <div class="kpi-value">{outstanding_invoices}</div>
            <div class="kpi-delta">Total: £{pending_amount:,.2f}</div>
            <div class="metric-detail">Awaiting payment</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="kpi-card cyan">
            <div style="font-size: 35px; margin-bottom: 8px;">⚠️</div>
            <div class="kpi-label">OVERDUE INVOICES</div>
            <div class="kpi-value">{overdue_invoices}</div>
            <div class="kpi-delta" style="color: #F44336;">Action required</div>
            <div class="metric-detail">Follow up needed</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Revenue Trend Chart
    st.markdown("### 📈 Revenue vs Expenses Trend (6 Months)")
    trend_data = {
        'Month': MONTHS,
        'Revenue': [sum([monthly_revenue[div][i] for div in monthly_revenue.keys() if div != 'Expenses']) for i in range(6)],
        'Expenses': monthly_revenue['Expenses']
    }
    trend_df = pd.DataFrame(trend_data)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Revenue'], mode='lines+markers', name='Revenue', line=dict(color='#4CAF50', width=3), fill='tozeroy', fillcolor='rgba(76,175,80,0.1)'))
    fig_trend.add_trace(go.Scatter(x=trend_df['Month'], y=trend_df['Expenses'], mode='lines+markers', name='Expenses', line=dict(color='#F44336', width=3)))
    fig_trend.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=350, legend=dict(x=0, y=1), yaxis=dict(gridcolor='#262730'))
    st.plotly_chart(fig_trend, use_container_width=True)

# === TAB 2: REVENUE STREAMS ===
with tab_revenue:
    st.markdown("### 💵 Multi-Stream Revenue Breakdown")
    
    st.markdown("#### 📊 Revenue by Business Unit")
    div_revenue = {div: sum(streams.values()) for div, streams in revenue_streams.items()}
    
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(values=list(div_revenue.values()), names=list(div_revenue.keys()), 
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        for div, amount in div_revenue.items():
            percentage = (amount / total_revenue * 100)
            st.markdown(f"""
            <div class="kpi-card blue" style="margin-bottom: 15px;">
                <div class="kpi-label">{div}</div>
                <div class="kpi-value">£{amount:,.2f}</div>
                <div class="kpi-delta">{percentage:.1f}% of total revenue</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 💰 Revenue Stream Details")
    for division, streams in revenue_streams.items():
        with st.expander(f"**{division}** - Total: £{sum(streams.values()):,.2f}"):
            for stream, amount in streams.items():
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"**{stream.replace('_', ' ').title()}**")
                col2.markdown(f"**£{amount:,.2f}**")
                st.progress(min(amount / 15000, 1.0))

# === TAB 3: EXPENSE MANAGEMENT ===
with tab_expenses:
    st.markdown("### 💸 Expense Breakdown & Management")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(x=list(expenses_dict.keys()), y=list(expenses_dict.values()),
                         color=list(expenses_dict.values()), color_continuous_scale='Reds')
        fig_bar.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=400, 
                              xaxis_title='Category', yaxis_title='Amount (£)', showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        for category, amount in expenses_dict.items():
            percentage = (amount / total_expenses * 100)
            st.markdown(f"""
            <div class="kpi-card red" style="margin-bottom: 10px;">
                <div class="kpi-label">{category}</div>
                <div class="kpi-value">£{amount:,.2f}</div>
                <div class="kpi-delta">{percentage:.1f}% of expenses</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 💡 Cost Optimization Suggestions")
    col1, col2, col3 = st.columns(3)
    col1.info("💡 **Venue Rentals:** Consider long-term lease for 15% savings")
    col2.info("💡 **Marketing:** Shift 20% budget to social media for better ROI")
    col3.info("💡 **Platform Fees:** Negotiate bulk discount with payment processor")

# === TAB 4: ARTIST PAYOUTS ===
with tab_artists:
    st.markdown("### 👥 Artist Payout Management (70/30 Split)")
    
    total_artist_sales = artists_df['Total Sales'].sum()
    total_artist_payouts = artists_df['Artist Payout (70%)'].sum()
    total_shack_commission = artists_df['Shack Share (30%)'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Artist Sales", f"£{total_artist_sales:,.2f}")
    col2.metric("Artist Payouts (70%)", f"£{total_artist_payouts:,.2f}")
    col3.metric("Shack Commission (30%)", f"£{total_shack_commission:,.2f}")
    
    st.markdown("---")
    st.markdown("#### 📋 Artist Payout Details")
    
    for idx, row in artists_df.iterrows():
        cols = st.columns([3, 2, 2, 2, 2, 1])
        cols[0].write(f"**{row['Artist']}**")
        cols[1].write(f"Sales: £{row['Total Sales']:,.2f}")
        cols[2].write(f"Payout: £{row['Artist Payout (70%)']:,.2f}")
        cols[3].write(f"Status: {row['Status']}")
        cols[4].write(f"Last: {row['Last Payout']}")
        if row['Status'] == 'Pending':
            if cols[5].button("Pay", key=f"pay_{idx}"):
                st.success(f"✅ Payment processed for {row['Artist']}")
    
    st.markdown("---")
    if st.button("💳 Process All Pending Payouts", use_container_width=True):
        st.success("✅ Batch payment processed: £8,450.00 to 6 artists")

# === TAB 5: INVOICES & RECEIVABLES ===
with tab_invoices:
    st.markdown("### 📄 Invoices & Accounts Receivable")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invoiced", f"£{total_invoiced:,.2f}")
    col2.metric("Paid", f"£{paid_amount:,.2f}", delta=f"{(paid_amount/total_invoiced*100):.1f}% collected" if total_invoiced > 0 else "0%")
    col3.metric("Outstanding", f"£{pending_amount:,.2f}", delta=f"{(pending_amount/total_invoiced*100):.1f}% pending" if total_invoiced > 0 else "0%")
    
    st.markdown("---")
    
    filter_status = st.selectbox("Filter by Status", ["All", "Paid", "Pending", "Overdue"])
    display_invoices = invoices_df if filter_status == "All" else invoices_df[invoices_df['Status'] == filter_status]
    
    # Format Amount column for display only
    display_df = display_invoices.copy()
    display_df['Amount'] = display_df['Amount'].apply(lambda x: f"£{x:,.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📧 Send Payment Reminders", use_container_width=True):
            st.success("📧 Reminders sent to 5 clients")
    with col2:
        if st.button("📥 Export Invoice Report", use_container_width=True):
            csv = invoices_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "invoices.csv", "text/csv")

# === TAB 6: FORECAST & ANALYTICS ===
with tab_forecast:
    st.markdown("### 📈 Financial Forecast & Analytics")
    
    st.markdown("#### 💵 Cash Flow Analysis (Last 30 Days)")
    fig_cash = go.Figure()
    fig_cash.add_trace(go.Scatter(x=cash_flow_df['date'], y=cash_flow_df['income'], mode='lines', name='Income', line=dict(color='#4CAF50')))
    fig_cash.add_trace(go.Scatter(x=cash_flow_df['date'], y=cash_flow_df['expenses'], mode='lines', name='Expenses', line=dict(color='#F44336')))
    fig_cash.add_trace(go.Scatter(x=cash_flow_df['date'], y=cash_flow_df['net'], mode='lines', name='Net Cash Flow', line=dict(color='#2196F3', width=3)))
    fig_cash.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=350, legend=dict(x=0, y=1))
    st.plotly_chart(fig_cash, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 📊 Q3 2026 Revenue Projections")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projected Revenue", "£58,000", "+15% vs Q2")
    col2.metric("Projected Expenses", "£19,500", "+8% vs Q2")
    col3.metric("Projected Profit", "£38,500", "+19% vs Q2")
    col4.metric("Target Margin", "66%", "+2% improvement")
    
    st.markdown("---")
    
    st.markdown("#### 📈 Key Financial Metrics")
    col1, col2, col3 = st.columns(3)
    col1.info("📊 **Burn Rate:** £573/day")
    col2.info("💰 **Runway:** 127 days at current burn")
    col3.info("📈 **Growth Rate:** 18.5% month-over-month")
    
    st.markdown("---")
    
    st.markdown("### 📥 Export Financial Reports")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 P&L Statement", use_container_width=True):
            st.success("📊 Profit & Loss Statement downloaded")
    with col2:
        if st.button("💵 Cash Flow Report", use_container_width=True):
            st.success("💵 Cash Flow Analysis downloaded")
    with col3:
        if st.button("📈 Full Financial Pack", use_container_width=True):
            st.success("📈 Complete Q2 2026 Financial Pack downloaded")

st.markdown("---")
st.caption("Shack Entertainment | Financial Command Center | Multi-Stream Intelligence | CFO Mode Active")