import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cache_reader import load_artists_unlimited_data as load_sheet_data

# Set page config FIRST
st.set_page_config(
    page_title="Artists Unlimited | Shack Entertainment",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117 !important; }
    header { visibility: hidden; }
    [data-testid="stHeader"] { background-color: #0e1117; padding: 0; }
    [data-testid="stSidebar"] a, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #e2e8f0 !important; }
    h1 { color: #ffffff !important; font-weight: 800; }
    h2 { color: #ffffff !important; font-weight: 700; }
    h3 { color: #ffffff !important; font-weight: 600; }

    /* Sidebar Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #60a5fa 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- NAVIGATION BAR ---

current = "Artists"  # auto-detected from filename
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


# Page header
st.title("🎨 Artists Unlimited")
st.markdown("*Artist Management & Sales Tracking* |  " + datetime.now().strftime("%d %B %Y"))

# Load data — suppress internal gspread/Streamlit error banners
import contextlib
result = None
with contextlib.redirect_stdout(None):
    try:
        result = load_sheet_data()
    except Exception:
        result = (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), "Unknown error")

    if result is None:
        result = (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), "Unknown error")

    if len(result) == 6:
        artists_df, inventory_df, outlets_df, sales_df, partners_df, error_msg = result
    else:
        artists_df = pd.DataFrame()
        inventory_df = pd.DataFrame()
        outlets_df = pd.DataFrame()
        sales_df = pd.DataFrame()
        partners_df = pd.DataFrame()
        error_msg = "Unexpected result format from data sync."

# Demo data fallback — only when ALL sheets are empty
if error_msg and not error_msg.startswith("Google Sheets"):
    st.warning(error_msg)

all_empty = (
    (artists_df is None or len(artists_df) == 0) and
    (inventory_df is None or len(inventory_df) == 0) and
    (outlets_df is None or len(outlets_df) == 0) and
    (sales_df is None or len(sales_df) == 0) and
    (partners_df is None or len(partners_df) == 0)
)
if all_empty and error_msg is None:
    st.info("No Artists Unlimited data yet — add data to your Google Sheet.")
    artists_df = pd.DataFrame({
        'Artist Name': ['Paul Duncan', 'Maya Strings', 'Bass Collective'],
        'Art Type/Discipline': ['Visual Artist', 'Musician', 'DJ/Producer'],
        'Tier': ['Emerging', 'Established', 'Emerging'],
        'Status': ['Active', 'Active', 'Pending']
    })

# ── Column name mapping (real sheet columns) ──
_name_col      = 'Artist Name'          if 'Artist Name' in artists_df.columns else None
_discipline_col = 'Art Type/Discipline'   if 'Art Type/Discipline' in artists_df.columns else ('Discipline' if 'Discipline' in artists_df.columns else None)
_status_col    = 'Status'                if 'Status' in artists_df.columns else None
_tier_col      = 'Tier'                  if 'Tier' in artists_df.columns else None
_managed_col   = 'Managed by Shack'       if 'Managed by Shack' in artists_df.columns else None

# Inventory columns
_inv_name_col  = 'Product Name'           if 'Product Name' in inventory_df.columns else None
_inv_sku_col   = 'SKU'                    if 'SKU' in inventory_df.columns else None
_inv_stock_col = 'Current Stock'           if 'Current Stock' in inventory_df.columns else ('Initial Stock' if 'Initial Stock' in inventory_df.columns else None)
_inv_price_col = 'Retail Price (£)'       if 'Retail Price (£)' in inventory_df.columns else None
_inv_cost_col  = 'Cost Price (£)'         if 'Cost Price (£)' in inventory_df.columns else None
_inv_artist_col = 'Artist Name'            if 'Artist Name' in inventory_df.columns else None

# Sales columns
_sales_price_col = 'Sale Price (£)'       if 'Sale Price (£)' in sales_df.columns else None
_sales_artist_col = 'Artist'               if 'Artist' in sales_df.columns else None
_sales_shack_col = 'Shack_Share(£)'       if 'Shack_Share(£)' in sales_df.columns else None
_sales_date_col  = 'Sale Date'             if 'Sale Date' in sales_df.columns else None

# Outlets column
_outlet_name_col = 'Outlet Name'           if 'Outlet Name' in outlets_df.columns else None


# ════════════════════════════════════════
# METRICS — calculated from REAL data
# ════════════════════════════════════════

# Artist KPIs
total_artists     = len(artists_df) if artists_df is not None else 0
active_artists    = artists_df[artists_df[_status_col] == 'Active'][_name_col].nunique() if (artists_df is not None and _status_col and _name_col) else 0
managed_count     = artists_df[artists_df[_managed_col] == 'Yes'][_name_col].nunique() if (artists_df is not None and _managed_col and _name_col) else 0
emerging_count    = artists_df[artists_df[_tier_col] == 'Emerging'][_name_col].nunique() if (artists_df is not None and _tier_col and _name_col) else 0

# Inventory KPIs
total_products    = len(inventory_df) if inventory_df is not None else 0
total_stock_value = 0
if inventory_df is not None and _inv_price_col and _inv_stock_col:
    try:
        total_stock_value = sum(
            float(str(p).replace('£','').replace(',','').strip()) * int(s)
            for p, s in zip(inventory_df[_inv_price_col], inventory_df[_inv_stock_col])
            if pd.notna(p) and pd.notna(s) and str(p).strip() and str(s).strip() != ''
        )
    except (ValueError, TypeError):
        total_stock_value = 0

# Sales KPIs (from real transaction data)
total_transactions = len(sales_df) if sales_df is not None else 0
total_revenue = 0
total_shack_share = 0
if sales_df is not None and _sales_price_col:
    for val in sales_df[_sales_price_col]:
        try:
            clean = str(val).replace('£','').replace(',','').strip()
            if clean:
                total_revenue += float(clean)
        except (ValueError, TypeError):
            pass
if sales_df is not None and _sales_shack_col:
    for val in sales_df[_sales_shack_col]:
        try:
            clean = str(val).replace('£','').replace(',','').strip()
            if clean:
                total_shack_share += float(clean)
        except (ValueError, TypeError):
            pass

# Outlet KPIs
total_outlets = len(outlets_df) if outlets_df is not None else 0
active_outlets = outlets_df[outlets_df['Status'] == 'Active'][_outlet_name_col].nunique() if (outlets_df is not None and 'Status' in outlets_df.columns and _outlet_name_col) else 0


# Display top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎨 Total Artists", f"{total_artists}", f"{active_artists} active")
with col2:
    st.metric("💰 Total Revenue", f"£{total_revenue:,.2f}", f"Shack share: £{total_shack_share:,.2f}")
with col3:
    st.metric("📦 Products", f"{total_products}", f"Stock value: £{total_stock_value:,.0f}")
with col4:
    st.metric("🏪 Outlets", f"{total_outlets}", f"{active_outlets} active")

st.divider()


# ════════════════════════════════════════
# SIDEBAR — Quick Actions
# ════════════════════════════════════════

with st.sidebar:
    st.header("⚡ Quick Actions")
    st.divider()

    if st.button("🔄 Sync Data", use_container_width=True):
        st.cache_data.clear()
        with st.spinner('Syncing from Google Sheets...'):
            import time
            time.sleep(1.5)
        st.success("✅ Data synced from Google Sheets!")
        st.rerun()

    if st.button("📥 Export Data", use_container_width=True):
        export_df = artists_df if artists_df is not None and len(artists_df) > 0 else sales_df
        if export_df is not None and len(export_df) > 0:
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"artists_unlimited_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.error("❌ No data available to export")

    if st.button("🔔 Low Stock Alert", use_container_width=True):
        low_stock = []
        if inventory_df is not None and len(inventory_df) > 0 and _inv_stock_col and _inv_name_col:
            for _, row in inventory_df.iterrows():
                try:
                    qty = int(float(str(row[_inv_stock_col]).replace('£','').replace(',','').strip())) if pd.notna(row[_inv_stock_col]) else 999
                    if qty < 5:
                        low_stock.append(f"{row[_inv_name_col]}: {qty} left")
                except (ValueError, TypeError):
                    pass

        if low_stock:
            st.warning(f"⚠️ Low Stock Alert: {len(low_stock)} item(s) need restocking!")
            for item in low_stock:
                st.markdown(f"- **{item}**")
        elif inventory_df is not None and len(inventory_df) > 0:
            st.success("✅ All stock levels healthy — no low stock items.")
        else:
            st.info("ℹ️ No inventory data connected. Link your Products sheet to enable alerts.")

    if st.button("📷 Scan Barcode", use_container_width=True):
        st.markdown("### 📷 Barcode Scanner")
        cam = st.camera_input("Point camera at a barcode", key="barcode_cam")
        if cam:
            st.info("🖼️ Image captured. Integrate `pyzbar` for barcode OCR.")
            from PIL import Image
            img = Image.open(cam)
            st.image(img, caption="Captured image", width=300)


# ════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════

# ── Section 1: Revenue / Sales Trend ──
st.subheader("📈 Revenue Overview")

col_a, col_b = st.columns([2, 1])
with col_a:
    if sales_df is not None and len(sales_df) > 0 and _sales_price_col:
        # Build trend from actual sales data
        trend_records = []
        for _, row in sales_df.iterrows():
            try:
                price = float(str(row.get(_sales_price_col, '0')).replace('£','').replace(',','').strip())
                artist = row.get(_sales_artist_col, 'Unknown')
                date_val = row.get(_sales_date_col, datetime.now().strftime('%Y-%m-%d'))
                if price > 0:
                    trend_records.append({'Date': str(date_val), 'Revenue': price, 'Artist': artist})
            except (ValueError, TypeError):
                pass

        if trend_records:
            trend_df = pd.DataFrame(trend_records)
            fig = px.bar(trend_df, x='Date', y='Revenue', color='Artist',
                         title='Sales by Transaction', hover_data=['Revenue'])
            fig.update_layout(yaxis_title='Revenue (£)', height=350,
                              plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
                              font=dict(color='#e2e8f0'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid sales transactions to chart yet.")
    else:
        st.info("No sales data available. Add transactions to the Sales sheet to see the revenue chart.")

with col_b:
    st.markdown("**Quick Stats**")
    st.metric("Transactions", f"{total_transactions}")
    st.metric("Avg Sale Value", f"£{total_revenue/total_transactions:,.2f}" if total_transactions > 0 else "N/A")
    st.metric("Shack Commission", f"£{total_shack_share:,.2f}")

st.divider()

# ── Section 2: Recent Transactions ──
st.subheader("💳 Recent Transactions")

if sales_df is not None and len(sales_df) > 0:
    recent = sales_df.head(10).copy()
    recent.columns = [str(c).strip() for c in recent.columns]
    pick_cols = []
    for c in [_sales_artist_col, _sales_date_col, _sales_price_col, 'Product Name', 'SKU', 'Form Channel']:
        if c and c in recent.columns:
            pick_cols.append(c)
    if not pick_cols:
        pick_cols = list(recent.columns[:6])
    st.dataframe(recent[pick_cols], use_container_width=True, hide_index=True, height=250)
else:
    st.info("No transactions yet. Sales will appear here when added to the Sales sheet.")

st.divider()

# ── Section 3: All Artists Roster ──
st.subheader("🎨 Artist Roster")

if artists_df is not None and len(artists_df) > 0:
    col1, col2 = st.columns(2)
    with col1:
        disc_options = sorted(artists_df[_discipline_col].dropna().unique().tolist()) if _discipline_col else []
        discipline_filter = st.multiselect("Filter by Discipline", options=disc_options, default=[])

    with col2:
        status_options = sorted(artists_df[_status_col].dropna().unique().tolist()) if _status_col else []
        status_filter = st.multiselect("Filter by Status", options=status_options, default=[])

    filtered = artists_df.copy()
    if discipline_filter and _discipline_col:
        filtered = filtered[filtered[_discipline_col].isin(discipline_filter)]
    if status_filter and _status_col:
        filtered = filtered[filtered[_status_col].isin(status_filter)]

    # Show only meaningful display columns
    display_cols = []
    for c in [_name_col, _discipline_col, _tier_col, _status_col, _managed_col, 'Contact Email']:
        if c and c in filtered.columns:
            display_cols.append(c)
    if not display_cols:
        display_cols = list(filtered.columns[:8])

    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True, height=350)
else:
    st.info("No artist data available.")

st.divider()

# ── Section 4: Inventory & Products ──
st.subheader("📦 Product Inventory")

if inventory_df is not None and len(inventory_df) > 0:
    inv_display_cols = []
    for c in [_inv_sku_col, _inv_name_col, _inv_artist_col, 'Category', _inv_cost_col, _inv_price_col, _inv_stock_col, 'Location/Store']:
        if c and c in inventory_df.columns:
            inv_display_cols.append(c)
    if not inv_display_cols:
        inv_display_cols = list(inventory_df.columns[:8])

    st.dataframe(inventory_df[inv_display_cols], use_container_width=True, hide_index=True, height=250)
else:
    st.info("No product inventory data yet.")

st.divider()

# ── Section 5: Summary Statistics ──
st.subheader("📊 Summary")

sum1, sum2, sum3, sum4 = st.columns(4)
with sum1:
    st.metric("Total Artists", f"{total_artists}")
    if _tier_col and artists_df is not None:
        tiers = artists_df[_tier_col].value_counts().to_dict()
        st.caption(f"Tiers: {', '.join(f'{k}: {v}' for k, v in tiers.items())}")
with sum2:
    st.metric("Total Revenue", f"£{total_revenue:,.2f}")
    st.caption(f"From {total_transactions} transaction(s)")
with sum3:
    st.metric("Products in Stock", f"{total_products}")
    if _inv_stock_col is not None and inventory_df is not None:
        try:
            total_units = sum(int(float(str(x).replace('£','').replace(',','').strip())) for x in inventory_df[_inv_stock_col] if pd.notna(x) and str(x).strip())
            st.caption(f"Total units: {total_units}")
        except (ValueError, TypeError):
            pass
with sum4:
    managed_pct = round(managed_count / total_artists * 100) if total_artists > 0 else 0
    st.metric("Managed by Shack", f"{managed_count}/{total_artists} ({managed_pct}%)")
    st.caption(f"{emerging_count} emerging artists")

st.divider()
st.markdown("**Shack Entertainment** | Artists Unlimited — Creative Growth Engine")
