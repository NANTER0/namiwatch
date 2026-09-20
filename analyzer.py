from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

CRISIS_KEYWORDS = [
    "crisis", "protest", "strike", "shortage",
    "corruption", "emergency", "outbreak",
    "violence", "flood", "drought", "failure"
]

TOPICS = {
    "Economy": [
        "economy", "inflation", "business",
        "investment", "budget"
    ],
    "Employment": [
        "jobs", "employment", "unemployment",
        "workers"
    ],
    "Health": [
        "health", "hospital", "clinic",
        "doctor", "medicine"
    ],
    "Education": [
        "education", "school", "teacher",
        "student", "university"
    ],
    "Infrastructure": [
        "water", "electricity", "road",
        "housing", "infrastructure"
    ],
    "Governance": [
        "government", "ministry", "minister",
        "parliament", "policy"
    ]
}


def analyse_article(title, content):
    text = f"{title} {content}"
    lower_text = text.lower()

    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        sentiment = "Positive"
    elif score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    topic_scores = {}

    for topic, keywords in TOPICS.items():
        topic_scores[topic] = sum(
            lower_text.count(word)
            for word in keywords
        )

    topic = max(topic_scores, key=topic_scores.get)

    if topic_scores[topic] == 0:
        topic = "Other"

    crisis_hits = sum(
        1 for word in CRISIS_KEYWORDS
        if word in lower_text
    )

    risk_score = crisis_hits * 15

    if sentiment == "Negative":
        risk_score += 30

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "Critical"
    elif risk_score >= 45:
        risk_level = "High"
    elif risk_score >= 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "sentiment": sentiment,
        "sentiment_score": round(score, 3),
        "topic": topic,
        "risk_score": risk_score,
        "risk_level": risk_level
  }
