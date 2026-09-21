import streamlit as st
import pandas as pd
import plotly.express as px
from analyzer import analyse_article
from news_fetcher import fetch_multiple_feeds
st.set_page_config(
    page_title="NamiWatch",
    page_icon="🇳🇦",
    layout="wide"
)

st.title("🇳🇦 NamiWatch")
st.subheader("National Media Monitoring & Analysis Platform")
st.caption("Sentiment • Trends • Emerging Issues • Crisis Detection")


@st.cache_data
def load_data():
    data = pd.read_csv("sample_news.csv")
    results = []

    for _, row in data.iterrows():
        result = analyse_article(
            str(row["title"]),
            str(row["content"])
        )
        results.append(result)

    results = pd.DataFrame(results)

    return pd.concat(
        [
            data.reset_index(drop=True),
            results.reset_index(drop=True)
        ],
        axis=1
    )


df = load_data()


# Add compatibility columns
if "media_type" not in df.columns:
    df["media_type"] = "Online News"

if "region" not in df.columns:
    df["region"] = "Namibia"

if "ministry_detected" not in df.columns:
    if "ministry" in df.columns:
        df["ministry_detected"] = df["ministry"]
    else:
        df["ministry_detected"] = "Government"

if "risk_score" not in df.columns:
    df["risk_score"] = 0

if "risk_level" not in df.columns:
    df["risk_level"] = "Low"

df["risk_score"] = pd.to_numeric(
    df["risk_score"],
    errors="coerce"
).fillna(0)


page = st.sidebar.radio(
    "Navigation",
    [
    "📊 Dashboard",
    "📰 Media Monitor",
    "🌐 Live News",
    "🚨 Crisis Alerts",
    "🔎 Analyse Story",
    "📄 Daily Report"
]
)


# DASHBOARD
if page == "📊 Dashboard":

    st.header("Executive Media Dashboard")

    total = len(df)

    positive = len(
        df[df["sentiment"] == "Positive"]
    )

    negative = len(
        df[df["sentiment"] == "Negative"]
    )

    alerts = len(
        df[df["risk_score"] >= 45]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Stories Monitored", total)
    c2.metric("Positive", positive)
    c3.metric("Negative", negative)
    c4.metric("Risk Alerts", alerts)

    st.divider()

    sentiment_data = (
        df["sentiment"]
        .value_counts()
        .reset_index()
    )

    sentiment_data.columns = [
        "Sentiment",
        "Stories"
    ]

    fig = px.pie(
        sentiment_data,
        names="Sentiment",
        values="Stories",
        title="Media Sentiment",
        color="Sentiment",
        color_discrete_map={
            "Positive": "green",
            "Neutral": "gold",
            "Negative": "red"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    topic_data = (
        df["topic"]
        .value_counts()
        .reset_index()
    )

    topic_data.columns = [
        "Topic",
        "Stories"
    ]

    fig2 = px.bar(
        topic_data,
        x="Topic",
        y="Stories",
        title="Trending Issues"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.subheader("Priority Issues")

    priority = df.sort_values(
        "risk_score",
        ascending=False
    )

    st.dataframe(
        priority[
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


# MEDIA MONITOR
elif page == "📰 Media Monitor":

    st.header("📰 Media Monitor")

    for _, row in df.iterrows():

        st.subheader(
            str(row["title"])
        )

        st.write(
            "Source: " +
            str(row["source"])
        )

        st.write(
            "Channel: " +
            str(row["media_type"])
        )

        st.write(
            str(row["content"])
        )

        st.write(
            "Sentiment: " +
            str(row["sentiment"])
        )

        st.write(
            "Topic: " +
            str(row["topic"])
        )

        st.write(
            "Risk Score: " +
            str(int(row["risk_score"])) +
            "/100"
        )

        st.divider()

# LIVE NEWS
elif page == "🌐 Live News":

    st.header("🌐 Live Media Monitoring")

    st.write(
        "Monitor public RSS news feeds and analyse "
        "stories as they are published."
    )

    feed_url = st.text_input(
        "RSS Feed URL",
        placeholder="https://example.com/feed"
    )

    source_name = st.text_input(
        "Source name",
        value="Public News Source"
    )

    if st.button("Fetch Live News"):

        if not feed_url:

            st.warning(
                "Enter an RSS feed URL."
            )

        else:

            with st.spinner(
                "Monitoring media feed..."
            ):

                feeds = {
                    source_name: feed_url
                }

                stories = fetch_multiple_feeds(
                    feeds
                )

            if len(stories) == 0:

                st.warning(
                    "No stories were found. "
                    "Check that the URL is a valid public RSS feed."
                )

            else:

                st.success(
                    "Retrieved " +
                    str(len(stories)) +
                    " stories."
                )

                for story in stories:

                    result = analyse_article(
                        story["title"],
                        story["content"]
                    )

                    st.subheader(
                        story["title"]
                    )

                    st.write(
                        "Source: " +
                        story["source"]
                    )

                    st.write(
                        "Sentiment: " +
                        str(result.get(
                            "sentiment",
                            "Unknown"
                        ))
                    )

                    st.write(
                        "Topic: " +
                        str(result.get(
                            "topic",
                            "Unknown"
                        ))
                    )

                    st.write(
                        "Risk Score: " +
                        str(result.get(
                            "risk_score",
                            0
                        )) +
                        "/100"
                    )

                    if story["link"]:

                        st.link_button(
                            "Open original article",
                            story["link"]
                        )

                    st.divider()
# CRISIS ALERTS
elif page == "🚨 Crisis Alerts":

    st.header("🚨 Crisis & Emerging Issues")

    alerts_df = df.sort_values(
        "risk_score",
        ascending=False
    )

    for _, row in alerts_df.iterrows():

        score = int(
            row["risk_score"]
        )

        title = str(
            row["title"]
        )

        if score >= 70:
            st.error(
                "🔴 CRITICAL: " + title
            )

        elif score >= 45:
            st.warning(
                "🟠 HIGH RISK: " + title
            )

        elif score >= 20:
            st.warning(
                "🟡 MONITOR: " + title
            )

        else:
            st.success(
                "🟢 LOW RISK: " + title
            )

        st.write(
            "Government Entity: " +
            str(row["ministry_detected"])
        )

        st.write(
            "Sentiment: " +
            str(row["sentiment"])
        )

        st.write(
            "Risk Score: " +
            str(score) +
            "/100"
        )

        st.progress(
            min(score, 100) / 100
        )

        st.divider()


# ANALYSE STORY
elif page == "🔎 Analyse Story":

    st.header("🔎 Live Story Analyser")

    st.write(
        "Paste a news article, radio transcript "
        "or social media report."
    )

    title = st.text_input(
        "Headline"
    )

    content = st.text_area(
        "Story",
        height=250
    )

    if st.button("Analyse"):

        if title or content:

            result = analyse_article(
                title,
                content
            )

            st.success(
                "Analysis completed"
            )

            st.write(
                "Sentiment:",
                result.get(
                    "sentiment",
                    "Unknown"
                )
            )

            st.write(
                "Topic:",
                result.get(
                    "topic",
                    "Unknown"
                )
            )

            st.write(
                "Risk Score:",
                result.get(
                    "risk_score",
                    0
                )
            )

            st.write(
                "Risk Level:",
                result.get(
                    "risk_level",
                    "Unknown"
                )
            )

        else:
            st.warning(
                "Enter a story first."
            )


# DAILY REPORT
elif page == "📄 Daily Report":

    st.header(
        "📄 Daily Media Intelligence Report"
    )

    report = "NAMIWATCH DAILY MEDIA BRIEFING\n\n"

    report += "Stories monitored: "
    report += str(len(df))
    report += "\n"

    report += "Positive stories: "
    report += str(
        len(
            df[
                df["sentiment"] ==
                "Positive"
            ]
        )
    )
    report += "\n"

    report += "Negative stories: "
    report += str(
        len(
            df[
                df["sentiment"] ==
                "Negative"
            ]
        )
    )
    report += "\n\n"

    report += "PRIORITY STORIES\n"

    priority = df.sort_values(
        "risk_score",
        ascending=False
    ).head(5)

    for _, row in priority.iterrows():

        report += "\n"
        report += str(
            row["title"]
        )

        report += "\nSource: "
        report += str(
            row["source"]
        )

        report += "\nRisk: "
        report += str(
            int(row["risk_score"])
        )

        report += "/100\n"

    st.text_area(
        "Report Preview",
        report,
        height=400
    )

    st.download_button(
        "📥 Download Report",
        report,
        "NamiWatch_Daily_Report.txt",
        "text/plain"
    )


st.divider()

st.caption(
    "🇳🇦 NamiWatch • Hackathon Prototype 2026"
)
