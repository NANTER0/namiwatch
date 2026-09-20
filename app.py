import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from analyzer import analyse_article


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NamiWatch | Media Intelligence",
    page_icon="🇳🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div style="
        background:#0b2a6f;
        padding:25px;
        border-radius:15px;
        margin-bottom:20px;
    ">
        <h1 style="
            color:white;
            margin:0;
            font-size:42px;
        ">
            🇳🇦 NamiWatch
        </h1>

        <h3 style="
            color:#ffcc00;
            margin-bottom:5px;
        ">
            National Media Intelligence Platform
        </h3>

        <p style="
            color:white;
            margin:0;
        ">
            Media Monitoring • Sentiment Analysis •
            Emerging Issues • Crisis Detection
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("sample_news.csv")

    results = []

    for _, row in df.iterrows():

        result = analyse_article(
            str(row["title"]),
            str(row["content"])
        )

        results.append(result)

    analysis_df = pd.DataFrame(results)

    return pd.concat(
        [
            df.reset_index(drop=True),
            analysis_df.reset_index(drop=True)
        ],
        axis=1
    )


try:
    df = load_data()

except Exception as error:

    st.error(
        "NamiWatch could not process the media dataset."
    )

    st.exception(error)

    st.stop()


# ============================================================
# COMPATIBILITY HELPERS
# ============================================================

# This makes the dashboard work with both the original and
# upgraded versions of analyzer.py.

if "ministry_detected" not in df.columns:

    if "ministry" in df.columns:
        df["ministry_detected"] = df["ministry"]
    else:
        df["ministry_detected"] = "Government / Public Affairs"


if "media_type" not in df.columns:
    df["media_type"] = "Online News"


if "region" not in df.columns:
    df["region"] = "Namibia"


if "risk_score" not in df.columns:
    df["risk_score"] = 0


if "risk_level" not in df.columns:
    df["risk_level"] = "Low"


if "topic" not in df.columns:
    df["topic"] = "General"


if "sentiment" not in df.columns:
    df["sentiment"] = "Neutral"


# Convert risk score safely to numbers
df["risk_score"] = pd.to_numeric(
    df["risk_score"],
    errors="coerce"
).fillna(0)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🇳🇦 NamiWatch")

st.sidebar.caption(
    "Media Monitoring & Analysis"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Executive Dashboard",
        "📰 Media Monitor",
        "🚨 Crisis Alerts",
        "📈 Trends & Sentiment",
        "🏛️ Government Monitoring",
        "🔎 Analyse Story",
        "📄 Daily Report"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Hackathon Prototype 2026"
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "📊 Executive Dashboard":

    st.header("National Media Intelligence")

    total = len(df)

    positive = len(
        df[df["sentiment"] == "Positive"]
    )

    neutral = len(
        df[df["sentiment"] == "Neutral"]
    )

    negative = len(
        df[df["sentiment"] == "Negative"]
    )

    alerts = len(
        df[df["risk_score"] >= 45]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Stories",
        total
    )

    col2.metric(
        "Positive",
        positive
    )

    col3.metric(
        "Neutral",
        neutral
    )

    col4.metric(
        "Negative",
        negative
    )

    col5.metric(
        "Risk Alerts",
        alerts
    )

    st.divider()

    # Charts

    chart1, chart2 = st.columns(2)

    with chart1:

        sentiment_counts = (
            df["sentiment"]
            .value_counts()
            .reset_index()
        )

        sentiment_counts.columns = [
            "Sentiment",
            "Stories"
        ]

        fig = px.pie(
            sentiment_counts,
            names="Sentiment",
            values="Stories",
            title="Media Sentiment",
            color="Sentiment",
            color_discrete_map={
                "Positive": "#009543",
                "Neutral": "#F4C430",
                "Negative": "#D21034"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with chart2:

        topic_counts = (
            df["topic"]
            .value_counts()
            .reset_index()
        )

        topic_counts.columns = [
            "Topic",
            "Stories"
        ]

        fig = px.bar(
            topic_counts,
            x="Stories",
            y="Topic",
            orientation="h",
            title="Most Discussed Topics",
            color="Stories"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("🚨 Priority Issues")

    priority = df.sort_values(
        "risk_score",
        ascending=False
    ).head(5)

    display_columns = [
        "title",
        "source",
        "topic",
        "sentiment",
        "risk_score",
        "risk_level"
    ]

    st.dataframe(
        priority[display_columns],
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# MEDIA MONITOR
# ============================================================

elif page == "📰 Media Monitor":

    st.header("📰 Multi-Channel Media Monitor")

    col1, col2 = st.columns(2)

    with col1:

        media_filter = st.multiselect(
            "Media channel",
            options=list(
                df["media_type"].dropna().unique()
            ),
            default=list(
                df["media_type"].dropna().unique()
            )
        )

    with col2:

        sentiment_filter = st.multiselect(
            "Sentiment",
            [
                "Positive",
                "Neutral",
                "Negative"
            ],
            default=[
                "Positive",
                "Neutral",
                "Negative"
            ]
        )

    filtered = df[
        df["media_type"].isin(media_filter)
        &
        df["sentiment"].isin(sentiment_filter)
    ]

    st.write(
        f"Monitoring **{len(filtered)} media stories**"
    )

    for _, story in filtered.iterrows():

        st.subheader(
            story["title"]
        )

        st.caption(
            f"{story['source']} • "
            f"{story['media_type']} • "
            f"{story['region']}"
        )

        st.write(
            story["content"]
        )

        c1, c2, c3 = st.columns(3)

        c1.write(
            f"**Sentiment:** {story['sentiment']}"
        )

        c2.write(
            f"**Topic:** {story['topic']}"
        )

        c3.write(
            f"**Risk:** {int(story['risk_score'])}/100"
        )

        st.divider()


# ============================================================
# CRISIS ALERTS
# ============================================================

elif page == "🚨 Crisis Alerts":

    st.header(
        "🚨 Emerging Issues & Crisis Detection"
    )

    st.info(
        "NamiWatch ranks monitored stories using "
        "sentiment and crisis-related indicators."
    )

    crisis_df = df.sort_values(
        "risk_score",
        ascending=False
    )

    for _, story in crisis_df.iterrows():

        score = int(
            story["risk_score"]
        )

        if score >= 70:

            st.error(
                f"🔴 CRITICAL: {story['title']}"
            )

        elif score >= 45:

            st.warning(
                f"🟠 HIGH WATCH: {story['title']}"
            )

        elif score >= 20:

            st.warning(
                f"🟡 MONITOR: {story['title']}"
            )

        else:

            st.success(
                f"🟢 LOW RISK: {story['title']}"
            )

        st.write(
            f"**Source:** {story['source']}"
        )

        st.write(
            f"**Topic:** {story['topic']}"
        )

        st.write(
            f"**Government Entity:** "
            f"{story['ministry_detected']}"
        )

        st.write(
            f"**Sentiment:** {story['sentiment']}"
        )

        st.write(
            f"**Risk Level:** "
            f"{story['risk_level']}"
        )

        st.progress(
            min(score, 100) / 100
        )

        st.caption(
            f"Risk score: {score}/100"
        )

        st.divider()


# ============================================================
# TRENDS
# ============================================================

elif page == "📈 Trends & Sentiment":

    st.header(
        "📈 Media Trends & Sentiment"
    )

    topic_counts = (
        df["topic"]
        .value_counts()
        .reset_index()
    )

    topic_counts.columns = [
        "Topic",
        "Mentions"
    ]

    fig = px.bar(
        topic_counts,
        x="Topic",
        y="Mentions",
        color="Mentions",
        title="Emerging Topics"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    sentiment_topic = (
        df.groupby(
            ["topic", "sentiment"]
        )
        .size()
        .reset_index(
            name="Stories"
        )
    )

    fig2 = px.bar(
        sentiment_topic,
        x="topic",
        y="Stories",
        color="sentiment",
        title="Sentiment by Topic",
        barmode="group",
        color_discrete_map={
            "Positive": "#009543",
            "Neutral": "#F4C430",
            "Negative": "#D21034"
        }
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# GOVERNMENT MONITORING
# ============================================================

elif page == "🏛️ Government Monitoring":

    st.header(
        "🏛️ Government Entity Monitoring"
    )

    ministry_counts = (
        df["ministry_detected"]
        .value_counts()
        .reset_index()
    )

    ministry_counts.columns = [
        "Government Entity",
        "Mentions"
    ]

    fig = px.bar(
        ministry_counts,
        x="Mentions",
        y="Government Entity",
        orientation="h",
        title="Government Entities in Media Coverage"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    ministry = st.selectbox(
        "Select government entity",
        list(
            df["ministry_detected"]
            .dropna()
            .unique()
        )
    )

    government_df = df[
        df["ministry_detected"] == ministry
    ]

    st.dataframe(
        government_df[
            [
                "title",
                "source",
                "sentiment",
                "topic",
                "risk_score"
            ]
        ],
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# LIVE STORY ANALYSER
# ============================================================

elif page == "🔎 Analyse Story":

    st.header(
        "🔎 Live Media Story Analyser"
    )

    st.write(
        "Paste a newspaper article, online story, "
        "radio transcript or social-media report."
    )

    title = st.text_input(
        "Headline"
    )

    content = st.text_area(
        "Story / transcript",
        height=250
    )

    if st.button(
        "Analyse Media Story",
        type="primary"
    ):

        if title or content:

            result = analyse_article(
                title,
                content
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Sentiment",
                result.get(
                    "sentiment",
                    "Unknown"
                )
            )

            c2.metric(
                "Topic",
                result.get(
                    "topic",
                    "General"
                )
            )

            c3.metric(
                "Risk Score",
                f"{result.get('risk_score', 0)}/100"
            )

            st.write(
                "**Risk classification:**",
                result.get(
                    "risk_level",
                    "Unknown"
                )
            )

            if "ministry_detected" in result:

                st.write(
                    "**Government entity:**",
                    result[
                        "ministry_detected"
                    ]
                )

            score = int(
                result.get(
                    "risk_score",
                    0
                )
            )

            if score >= 45:

                st.error(
                    "⚠️ This story may require "
                    "priority monitoring."
                )

            else:

                st.success(
                    "No high-risk alert detected."
                )

        else:

            st.warning(
                "Enter a headline or story first."
            )


# ============================================================
# DAILY EXECUTIVE REPORT
# ============================================================

elif page == "📄 Daily Report":

    st.header(
        "📄 Daily Executive Media Briefing"
    )

    today = datetime.now().strftime(
        "%d %B %Y"
    )

    high_risk = df[
        df["risk_score"] >= 45
    ].sort_values(
        "risk_score",
        ascending=False
    )

    report = f"""
NAMIWATCH DAILY MEDIA INTELLIGENCE BRIEFING

Date: {today}

EXECUTIVE SUMMARY

Stories monitored: {len(df)}
Positive stories: {len(df[df["sentiment"] == "Positive"])}
Neutral stories: {len(df[df["sentiment"] == "Neutral"])}
Negative stories: {len(df[df["sentiment"] == "Negative"])}
Priority alerts: {len(high_risk)}

PRIORITY ISSUES

"""

    if len(high_risk) == 0:

        report += (
            "No high-risk issues detected "
            "in the current monitoring period.\n"
        )

    else:

        for _, story in high_risk.iterrows():

            report += (
                f"\n- {story['title']}\n"
                f"  Source: {story['source']}\n"
                f"  Topic: 
