import streamlit as st
import pandas as pd
import plotly.express as px

from analyzer import analyse_article

st.set_page_config(
    page_title="NamiWatch",
    page_icon="🇳🇦",
    layout="wide"
)

st.title("🇳🇦 NamiWatch")
st.subheader("Media Monitoring & Analysis Platform")
st.caption("Turning media coverage into actionable intelligence")

# Load demonstration data
df = pd.read_csv("sample_news.csv")

# Analyse every story
results = []

for _, row in df.iterrows():
    result = analyse_article(
        row["title"],
        row["content"]
    )
    results.append(result)

analysis_df = pd.DataFrame(results)

df = pd.concat(
    [df.reset_index(drop=True), analysis_df],
    axis=1
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📰 Media Monitor",
        "🚨 Crisis Alerts",
        "🔎 Analyse Article"
    ]
)

if page == "📊 Dashboard":

    st.header("National Media Intelligence")

    total = len(df)

    positive = len(
        df[df["sentiment"] == "Positive"]
    )

    negative = len(
        df[df["sentiment"] == "Negative"]
    )

    alerts = len(
        df[df["risk_level"].isin(
            ["High", "Critical"]
        )]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Stories Monitored", total)
    c2.metric("Positive", positive)
    c3.metric("Negative", negative)
    c4.metric("High-Risk Alerts", alerts)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

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
                "Positive": "#009543",
                "Neutral": "#F5C400",
                "Negative": "#D21034"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        topic_data = (
            df["topic"]
            .value_counts()
            .reset_index()
        )

        topic_data.columns = [
            "Topic",
            "Stories"
        ]

        fig = px.bar(
            topic_data,
            x="Topic",
            y="Stories",
            title="Trending Topics",
            color="Stories"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("🚨 Emerging Issues")

    risk_df = df.sort_values(
        "risk_score",
        ascending=False
    )

    st.dataframe(
        risk_df[
            [
                "title",
                "source",
                "topic",
                "sentiment",
                "risk_score",
                "risk_level"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


elif page == "📰 Media Monitor":

    st.header("📰 Media Monitor")

    sentiment = st.selectbox(
        "Filter by sentiment",
        [
            "All",
            "Positive",
            "Neutral",
            "Negative"
        ]
    )

    filtered = df.copy()

    if sentiment != "All":
        filtered = filtered[
            filtered["sentiment"] == sentiment
        ]

    for _, article in filtered.iterrows():

        st.subheader(article["title"])

        st.caption(
            f"{article['source']} • "
            f"{article['date']}"
        )

        st.write(article["content"])

        st.write(
            f"**Topic:** {article['topic']} | "
            f"**Sentiment:** {article['sentiment']} | "
            f"**Risk:** {article['risk_level']}"
        )

        st.divider()


elif page == "🚨 Crisis Alerts":

    st.header("🚨 Crisis & Emerging Issue Monitor")

    st.write(
        "Potential issues are ranked using "
        "sentiment and crisis indicators."
    )

    alerts_df = df.sort_values(
        "risk_score",
        ascending=False
    )

    for _, article in alerts_df.iterrows():

        score = int(article["risk_score"])

        if score >= 45:
            st.error(
                f"⚠️ {article['title']}"
            )
        elif score >= 20:
            st.warning(
                f"⚡ {article['title']}"
            )
        else:
            st.info(
                f"ℹ️ {article['title']}"
            )

        st.write(
            f"Source: {article['source']}"
        )

        st.write(
            f"Topic: {article['topic']} | "
            f"Sentiment: {article['sentiment']}"
        )

        st.write(
            f"Risk score: {score}/100 "
            f"({article['risk_level']})"
        )

        st.progress(score / 100)

        st.divider()


elif page == "🔎 Analyse Article":

    st.header("🔎 Media Analysis Engine")

    st.write(
        "Paste a media story below to analyse "
        "its sentiment, topic and potential risk."
    )

    title = st.text_input(
        "Headline"
    )

    content = st.text_area(
        "Article content",
        height=220
    )

    if st.button(
        "Analyse Story",
        type="primary"
    ):

        if not title and not content:

            st.warning(
                "Please enter a headline or article."
            )

        else:

            result = analyse_article(
                title,
                content
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Sentiment",
                result["sentiment"]
            )

            c2.metric(
                "Topic",
                result["topic"]
            )

            c3.metric(
                "Risk",
                f"{result['risk_score']}/100"
            )

            if result["risk_level"] in [
                "High",
                "Critical"
            ]:
                st.error(
                    "⚠️ Potential issue detected: "
                    + result["risk_level"]
                )
            else:
                st.success(
                    "Risk classification: "
                    + result["risk_level"]
                )

            st.write(
                "Sentiment confidence score:",
                result["sentiment_score"]
            )


st.divider()

st.caption(
    "NamiWatch • Media Intelligence for Namibia • "
    "Hackathon Prototype 2026"
)
