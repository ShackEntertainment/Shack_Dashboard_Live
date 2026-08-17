import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────
st.set_page_config(page_title="Shack News Network | Analytics", layout="wide", page_icon="📰")

# ────────────────────────────────────────
# DUMMY DATA
# ────────────────────────────────────────
articles = [
    {"title": "Local Artist Sarah Chen Wins Poetry Slam at Edinburgh Fringe", "author": "Shack News Team", "date": datetime.now() - timedelta(days=7), "views": 3421, "shares": 234, "sales": 450.00, "platform": "Instagram"},
    {"title": "The Wandering Minstrels Sell Out Old Trout Gig in 48 Hours", "author": "Shack News Team", "date": datetime.now() - timedelta(days=13), "views": 2876, "shares": 189, "sales": 587.50, "platform": "Twitter"},
    {"title": "Behind the Scenes: How Shack Artists Create on a Budget", "author": "Bola A.", "date": datetime.now() - timedelta(days=20), "views": 1923, "shares": 97, "sales": 215.00, "platform": "Facebook"},
    {"title": "Paul Duncan's New Collection 'Ocean Dreams' Launches", "author": "Shack News Team", "date": datetime.now() - timedelta(days=3), "views": 1567, "shares": 145, "sales": 890.00, "platform": "Instagram"},
    {"title": "Top 5 Art Venues in Manchester You Need to Visit", "author": "Guest Writer", "date": datetime.now() - timedelta(days=25), "views": 4102, "shares": 312, "sales": 125.00, "platform": "Blog"}
]

df = pd.DataFrame(articles)
df["Date"] = df["date"].dt.strftime("%d %b %Y")
df["Engagement Rate"] = ((df["shares"] / df["views"]) * 100).round(2)

# ────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3612/3612569.png", width=60)
    st.header("⚡ Quick Actions")
    st.button("✍️ Write New Article", use_container_width=True)
    st.button("📊 View All Analytics", use_container_width=True)
    st.button("📤 Export Monthly Report", use_container_width=True)
    st.divider()
    st.info("💡 Tip: Articles with images get 2x more engagement!")

# ────────────────────────────────────────
# MAIN UI
# ────────────────────────────────────────
st.title("📰 Shack News Network Analytics")
st.caption("Amplify artist stories through content, interviews, reviews & social media")
st.divider()

# Metrics
col1, col2, col3, col4 = st.columns(4)
total_views = df["views"].sum()
total_shares = df["shares"].sum()
total_sales = df["sales"].sum()
avg_engagement = df["Engagement Rate"].mean()

col1.metric("Total Reach (This Month)", f"{total_views:,}")
col2.metric("Social Shares", f"{total_shares}")
col3.metric("Referral Sales", f"£{total_sales:,.2f}")
col4.metric("Avg Engagement Rate", f"{avg_engagement}%")

st.divider()

# Chart: Performance by Platform
st.subheader("📱 Performance by Platform")
platform_data = df.groupby("platform")[["views", "shares", "sales"]].sum()
st.bar_chart(platform_data["views"], color="#FF6B6B")

st.divider()

# Top Articles Table
st.subheader("🏆 Top Performing Articles")
st.dataframe(df[["title", "views", "shares", "sales", "Engagement Rate"]].sort_values("views", ascending=False), use_container_width=True, hide_index=True)

# Social Media Impact
st.divider()
st.subheader("🌐 Social Media Impact Breakdown")
social_df = df.groupby("platform").agg({
    "views": "sum",
    "shares": "sum",
    "sales": "sum"
}).reset_index()

st.dataframe(social_df, use_container_width=True, hide_index=True)

# Footer
st.caption("© 2026 Shack Entertainment | News Network Module")