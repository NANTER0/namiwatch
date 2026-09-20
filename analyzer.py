from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

CRISIS_KEYWORDS = {
    "critical": ["crisis", "emergency", "outbreak", "protest", "strike", "collapse", "severe shortage"],
    "moderate": ["delay", "concern", "disruption", "shortage", "complaint", "struggle", "overcrowded"],
    "positive": ["progress", "launch", "restored", "success", "jobs", "growth", "approved", "boost"]
}

MINISTRIES = {
    "MICT (ICT & Media)": ["mict", "information", "telecom", "broadcasting", "digital", "internet"],
    "MoHSS (Health & Social Services)": ["mohss", "health", "hospital", "clinic", "medicine", "doctor", "nurse", "patient"],
    "MoEAC (Education & Arts)": ["moeac", "education", "school", "classroom", "teacher", "student", "curriculum"],
    "MWT (Works & Transport)": ["mwt", "transport", "road", "railway", "bridge", "port", "highway"],
    "MAWLR (Agriculture & Water)": ["mawlr", "water", "agriculture", "farmer", "drought", "canal", "harvest", "livestock"],
    "MME (Mines & Energy)": ["mme", "energy", "fuel", "electricity", "mining", "oil", "solar", "nampower"],
    "MHAISS (Home Affairs & Security)": ["mhaiss", "home affairs", "police", "security", "passport", "immigration"]
}

TOPICS = {
    "Employment & Youth": ["jobs", "employment", "unemployment", "youth", "workforce", "hiring"],
    "Public Health": ["health", "hospital", "medicine", "disease", "clinic", "treatment"],
    "Infrastructure & Utilities": ["water", "electricity", "road", "bridge", "canal", "port", "power"],
    "Education & Training": ["education", "school", "university", "classroom", "training", "students"],
    "Economy & Agriculture": ["economy", "business", "investment", "drought", "harvest", "farmers", "fuel"],
    "Governance & Public Service": ["policy", "ministry", "government", "passport", "services", "parliament"]
}


def analyse_article(title: str, content: str, default_ministry: str = "Unassigned"):
    text = f"{title} {content}"
    lower_text = text.lower()

    # 1. Sentiment Calculation
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.15:
        sentiment = "Positive"
    elif compound <= -0.15:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # 2. Topic Detection
    topic_scores = {
        topic: sum(lower_text.count(kw) for kw in kws)
        for topic, kws in TOPICS.items()
    }
    top_topic = max(topic_scores, key=topic_scores.get)
    topic = top_topic if topic_scores[top_topic] > 0 else "General Public Affairs"

    # 3. Ministry Attribution
    ministry_scores = {
        min_name: sum(lower_text.count(kw) for kw in kws)
        for min_name, kws in MINISTRIES.items()
    }
    top_ministry = max(ministry_scores, key=ministry_scores.get)
    detected_ministry = top_ministry if ministry_scores[top_ministry] > 0 else default_ministry

    # 4. Crisis Risk Score (0-100)
    crit_hits = sum(1 for w in CRISIS_KEYWORDS["critical"] if w in lower_text)
    mod_hits = sum(1 for w in CRISIS_KEYWORDS["moderate"] if w in lower_text)
    pos_hits = sum(1 for w in CRISIS_KEYWORDS["positive"] if w in lower_text)

    risk_score = (crit_hits * 30) + (mod_hits * 15) - (pos_hits * 10)
    if sentiment == "Negative":
        risk_score += 25
    elif sentiment == "Positive":
        risk_score -= 15

    risk_score = max(5, min(100, risk_score))

    if risk_score >= 70:
        risk_level = "Critical Action Required"
        badge_color = "red"
    elif risk_score >= 45:
        risk_level = "High Watch"
        badge_color = "orange"
    elif risk_score >= 25:
        risk_level = "Moderate"
        badge_color = "yellow"
    else:
        risk_level = "Low / Informational"
        badge_color = "green"

    return {
        "sentiment": sentiment,
        "sentiment_score": round(compound, 3),
        "topic": topic,
        "ministry_detected": detected_ministry,
        "risk_score": int(risk_score),
        "risk_level": risk_level,
        "badge_color": badge_color
    }
