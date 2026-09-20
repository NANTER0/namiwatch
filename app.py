import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from analyzer import analyse_article

st.set_page_config(
    page_title="NamiWatch | Media Intelligence",
    page_icon="🇳🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Brand Header
st.markdown("""
<div style="background-color:#0b2265;padding:15px;border-radius:10px;margin-bottom:20px;">
    <h1 style="color:#ffffff;margin:0;">🇳🇦 NamiWatch Intelligence Platform</h1>
    <p style="color:#ffcc00;margin:0;font-weight:bold;">
        National Media Monitoring, Sentiment & Crisis Detection System | 9th National ICT Summit & Hackathon
    </p>
</div>
""", unsafe_allow_html=True)

# Load and Process Data
@st.cache_data
def load_data():
    df = pd.read_csv("sample_news.csv")
    results = []
    for _, row in df.iterrows():
        res = analyse_article(row["title"], row["content"], row.get("ministry", "MICT"))
        results.append(res)
    analysis_df = pd.DataFrame(results)
    return pd.concat([df.reset_index(drop=True), analysis_df], axis=1)

df = load_data()

# Navigation
sidebar_choice = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏛️ Executive Overview",
        "📰 Multi-Channel Feed",
        "🚨 Crisis & Threat Matrix",
        "📄 Daily Executive Report Generator",
        "🖨️ Print Media & OCR Ingestion",
        "🔎 Live Story Analyser"
    ]
)

# -------------------------------------------------------------
# 1. EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if sidebar_choice == "🏛️ Executive Overview":
    st.subheader("📊 National Media Landscape at a Glance")

    total_stories = len(df)
    pos_count = len(df[df["sentiment"] == "Positive"])
    neg_count = len(df[df["sentiment"] == "Negative"])
    neu_count = len(df[df["sentiment"] == "Neutral"])
    crit_count = len(df[df["risk_score"] >= 45])

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Stories Monitored", total_stories)
    kpi2.metric("Positive Coverage", f"{pos_count} ({int(pos_count/total_stories*100)}%)")
    kpi3.metric("Neutral Coverage", f"{neu_count} ({int(neu_count/total_stories*100)}%)")
    kpi4.metric("Negative Coverage", f"{neg_count} ({int(neg_count/total_stories*100)}%)", delta_color="inverse")
    kpi5.metric("Active Crisis Alerts", crit_count, delta_color="inverse")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        fig_sent = px.pie(
            df,
            names="sentiment",
            title="<b>Sentiment Distribution Across All Media</b>",
            color="sentiment",
            color_discrete_map={"Positive": "#009543", "Neutral": "#F5C400", "Negative": "#D21034"}
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    with c2:
        fig_media = px.bar(
            df.groupby("media_type").size().reset_index(name="count"),
            x="media_type",
            y="count",
            color="media_type",
            title="<b>Coverage by Media Channel (Print, Radio, TV, Social)</b>",
            labels={"count": "Stories", "media_type": "Channel"}
        )
        st.plotly_chart(fig_media, use_container_width=True)

    st.divider()

    c3, c4 = st.columns(2)
    with c3:
        fig_ministry = px.bar(
            df.groupby("ministry_detected").size().reset_index(name="count").sort_values("count", ascending=True),
            x="count",
            y="ministry_detected",
            orientation='h',
            title="<b>Government Ministries Most Mentioned</b>",
            color_discrete_sequence=["#0b2265"]
        )
        st.plotly_chart(fig_ministry, use_container_width=True)

    with c4:
        fig_topics = px.pie(
            df,
            names="topic",
            title="<b>Emerging Issues & Priority Topics</b>",
            hole=0.4
        )
        st.plotly_chart(fig_topics, use_container_width=True)

# -------------------------------------------------------------
# 2. MULTI-CHANNEL FEED
# -------------------------------------------------------------
elif sidebar_choice == "📰 Multi-Channel Feed":
    st.subheader("📰 Live Monitored Media Feed")

    f1, f2, f3 = st.columns(3)
    channel_filt = f1.multiselect("Filter Media Type", options=df["media_type"].unique(), default=df["media_type"].unique())
    sent_filt = f2.multiselect("Filter Sentiment", options=["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"])
    min_filt = f3.selectbox("Filter Ministry", options=["All"] + list(df["ministry_detected"].unique()))

    filtered = df[
        (df["media_type"].isin(channel_filt)) &
        (df["sentiment"].isin(sent_filt))
    ]
    if min_filt != "All":
        filtered = filtered[filtered["ministry_detected"] == min_filt]

    st.write(f"Showing **{len(filtered)}** verified media records:")

    for _, row in filtered.iterrows():
        sent_color = {"Positive": "green", "Neutral": "gray", "Negative": "red"}.get(row["sentiment"], "blue")
        with st.container():
            st.markdown(f"""
            ### {row['title']}
            **Source:** `{row['source']}` | **Channel:** `{row['media_type']}` | **Region:** `{row['region']}` | **Ministry:** `{row['ministry_detected']}`  
            *Sentiment:* **:{sent_color}[{row['sentiment']}]** | *Risk Score:* `{row['risk_score']}/100` (`{row['risk_level']}`)  
            >{row['content']}
            """)
            st.divider()

# -------------------------------------------------------------
# 3. CRISIS MATRIX
# -------------------------------------------------------------
elif sidebar_choice == "🚨 Crisis & Threat Matrix":
    st.subheader("🚨 Early Warning Crisis Detection & Action Matrix")
    st.info("The system highlights fast-escalating negative stories and community protests requiring government intervention.")

    crisis_df = df.sort_values("risk_score", ascending=False)

    for _, r in crisis_df.iterrows():
        score = r["risk_score"]
        if score >= 45:
            st.error(f"⚠️ **CRITICAL ISSUE:** {r['title']}")
        elif score >= 25:
            st.warning(f"⚡ **MODERATE WATCH:** {r['title']}")
        else:
            st.success(f"✅ **STABLE:** {r['title']}")

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.write(f"**Ministry Responsible:** {r['ministry_detected']} | **Region:** {r['region']} | **Channel:** {r['media_type']}")
            st.write(f"**Summary:** {r['content']}")
        with col_b:
            st.metric("Risk Score", f"{score}/100")
            st.progress(score / 100)
        st.divider()

# -------------------------------------------------------------
# 4. DAILY EXECUTIVE REPORT GENERATOR
# -------------------------------------------------------------
elif sidebar_choice == "📄 Daily Executive Report Generator":
    st.subheader("📄 Automated Executive Daily Media Briefing")
    st.write("Generates an instant intelligence briefing ready for submission to Permanent Secretaries and Ministers.")

    today_str = datetime.now().strftime("%d %B %Y")
    top_alerts = df[df["risk_score"] >= 45]
    top_pos = df[df["sentiment"] == "Positive"]

    report_text = f"""
================================================================================
NAMIBIA MEDIA INTELLIGENCE BRIEFING
Generated by NamiWatch for: Ministry of Information & Communication Technology (MICT)
Date: {today_str}
================================================================================

1. EXECUTIVE SUMMARY:
- Total Monitored Stories: {len(df)} across Print, Radio, TV, and Social Media.
- Overall Sentiment Ratio: {len(top_pos)} Positive | {len(df[df['sentiment']=='Neutral'])} Neutral | {len(df[df['sentiment']=='Negative'])} Negative.
- Active Issues of Public Concern: {len(top_alerts)} stories flagged for immediate attention.

2. TOP ISSUES REQUIRING GOVERNMENT ATTENTION (HIGH RISK):
"""
    for idx, row in top_alerts.iterrows():
        report_text += f" • [{row['ministry_detected']} - {row['region']}] {row['title']} (Risk: {row['risk_score']}/100)\n   Summary: {row['content']}\n\n"

    report_text += """3. POSITIVE DEVELOPMENTS & POLICY WINS:\n"""
    for idx, row in top_pos.iterrows():
        report_text += f" • [{row['ministry_detected']}] {row['title']} ({row['source']})\n"

    report_text += f"""
================================================================================
End of Daily Intelligence Briefing • System: NamiWatch 2026
================================================================================
"""

    st.text_area("Generated Executive Briefing Preview", report_text, height=350)
    st.download_button(
        label="📥 Download Daily Executive Briefing (.txt)",
        data=report_text,
        file_name=f"NamiWatch_Daily_Briefing_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

# -------------------------------------------------------------
# 5. PRINT MEDIA & OCR INGESTION
# -------------------------------------------------------------
elif sidebar_choice == "🖨️ Print Media & OCR Ingestion":
    st.subheader("🖨️ Daily Print Media (Newspaper) Digitiser")
    st.write("Meets the requirement to analyse daily print newspapers (The Namibian, New Era, Kundana, Namibian Sun).")

    newspaper_choice = st.selectbox("Select Print Newspaper Source", ["The Namibian", "New Era", "Namibian Sun", "Kundana", "Windhoek Observer"])
    page_number = st.number_input("Newspaper Page Number", min_value=1, max_value=64, value=1)
    uploaded_file = st.file_uploader("Upload Scanned Newspaper Clipping / PDF (Simulated OCR)", type=["png", "jpg", "jpeg", "pdf", "txt"])

    raw_article_text = st.text_area(
        "Or Paste OCR Extracted Text from Print Edition",
        height=180,
        placeholder="Paste article text extracted from today's physical print edition..."
    )

    if st.button("Digitise & Run Print Intelligence"):
        if raw_article_text:
            res = analyse_article(f"[{newspaper_choice} P.{page_number}]", raw_article_text)
            st.success("✅ Print article processed and integrated into national database!")
            st.json(res)
        else:
            st.warning("Please paste or upload text from the print edition.")

# -------------------------------------------------------------
# 6. LIVE STORY ANALYSER
# -------------------------------------------------------------
elif sidebar_choice == "🔎 Live Story Analyser":
    st.subheader("🔎 Ad-Hoc Media Analyser")
    st.write("Test any unlisted news report, social media post, or radio transcript in real time.")

    user_title = st.text_input("Story Headline / Subject")
    user_content = st.text_area("Story Body Text", height=200)

    if st.button("Run AI Intelligence Analysis", type="primary"):
        if user_title or user_content:
            res = analyse_article(user_title, user_content)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Sentiment", res["sentiment"])
            m2.metric("Detected Ministry", res["ministry_detected"])
            m3.metric("Topic", res["topic"])
            m4.metric("Risk Score", f"{res['risk_score']}/100")
            
            if res["risk_score"] >= 45:
                st.error(f"Alert Level: {res['risk_level']}")
            else:
                st.success(f"Alert Level: {res['risk_level']}")
        else:
            st.warning("Please provide a headline or article text.")

st.divider()
st.caption("🇳🇦 NamiWatch • Built for the 9th National ICT Summit & Hackathon • Ministry of ICT & NUST")
