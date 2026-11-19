import os
import re
import requests

from .models import CampusItem


CATEGORIES = {
    "academics": [
        "exam", "examination", "timetable", "schedule", "syllabus",
        "subject", "assignment", "attendance", "marks", "class",
        "semester", "result", "academic", "test", "internal",
        "mid", "question paper"
    ],

    "faculty": [
        "faculty", "professor", "teacher", "hod", "lecturer",
        "staff", "sir", "madam", "instructor", "department"
    ],

    "campus": [
        "room", "lab", "library", "block", "building", "classroom",
        "canteen", "wifi", "parking", "location", "hostel",
        "facility", "computer", "infrastructure"
    ],

    "events": [
        "event", "workshop", "hackathon", "fest", "seminar",
        "club", "registration", "competition", "program",
        "activity", "conference"
    ],

    "notices": [
        "notice", "announcement", "circular", "deadline",
        "holiday", "notification", "update", "important",
        "information"
    ],

    "services": [
        "certificate", "id card", "office", "application",
        "document", "service", "fee", "scholarship",
        "request", "form", "help"
    ],
}


# Words that are useful for understanding a question
# but usually don't help identify a database record.
STOP_WORDS = {
    "what", "when", "where", "which", "who", "how",
    "can", "could", "would", "should", "tell", "show",
    "give", "please", "about", "the", "this", "that",
    "there", "their", "with", "from", "for", "does",
    "do", "is", "are", "was", "were", "and", "or",
    "to", "of", "in", "on", "my", "me", "i", "we",
    "you", "campus", "college", "university", "information"
}


def normalize(text):
    """
    Normalize text so slightly different wording
    can still match the same campus information.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def extract_terms(text):
    """
    Extract meaningful search terms.
    """

    words = normalize(text).split()

    terms = []

    for word in words:

        if len(word) <= 2:
            continue

        if word in STOP_WORDS:
            continue

        terms.append(word)

    return terms


def classify(text):
    """
    Detect the most relevant campus category.
    """

    text = normalize(text)

    scores = {
        category: 0
        for category in CATEGORIES
    }

    for category, words in CATEGORIES.items():

        for word in words:

            normalized_word = normalize(word)

            if normalized_word in text:
                scores[category] += 1

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:
        return "general"

    return best_category


def similarity_score(query, item):
    """
    Lightweight relevance scoring.

    It considers:
    - exact word matches
    - title matches
    - phrase matches
    - category matches
    """

    query_text = normalize(query)

    terms = extract_terms(query)

    title = normalize(item.title)

    content = normalize(item.content)

    category = normalize(item.category)

    score = 0

    # Exact phrase match
    if query_text and query_text in title:
        score += 20

    if query_text and query_text in content:
        score += 10

    # Individual term matches
    for term in terms:

        if term in title:
            score += 8

        if term in content:
            score += 4

        if term in category:
            score += 2

    # Related word matching
    # Handles cases like exam/examination,
    # register/registration, etc.
    for term in terms:

        if len(term) >= 5:

            stem = term[:5]

            if stem in title:
                score += 3

            if stem in content:
                score += 2

    return score


def retrieve(query, category, limit=5):

    if category == "general":

        items = CampusItem.query.all()

    else:

        category_items = CampusItem.query.filter_by(
            category=category
        ).all()

        # If the category has no useful result,
        # search the complete campus knowledge base.
        items = category_items

        if not items:
            items = CampusItem.query.all()

    scored = []

    for item in items:

        score = similarity_score(
            query,
            item
        )

        if score > 0:

            scored.append(
                (score, item)
            )

    scored.sort(
        key=lambda pair: pair[0],
        reverse=True
    )

    return [
        item
        for score, item in scored[:limit]
    ]


def fallback_answer(query, items):

    if not items:

        return (
            "I couldn't find verified campus information "
            "for that question yet.\n\n"
            "Try asking about academics, faculty, "
            "campus facilities, events, notices, "
            "or student services."
        )

    best = items[0]

    return (
        f"{best.content}\n\n"
        f"📌 Source: {best.source}"
    )


def ollama_answer(query, history, items):

    if os.getenv(
        "OLLAMA_ENABLED",
        "false"
    ).lower() != "true":

        return None

    if not items:

        return None

    context = "\n\n".join(
        f"""
Source: {item.source}

Category: {item.category}

Title: {item.title}

Verified information:
{item.content}
"""
        for item in items
    )

    recent_history = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history[-8:]
    )

    prompt = f"""
You are Campus AI, an intelligent student campus assistant.

Your job is to answer student questions using ONLY the
verified campus information supplied below.

STRICT RULES:

1. Never invent campus information.
2. Never invent dates, locations, faculty names,
   fees, timings, deadlines or policies.
3. If the information is unavailable, clearly say:
   "I don't have verified information about that yet."
4. Do not pretend demo information is official.
5. Use conversation history to understand follow-up questions.
6. Give short, clear and useful answers.
7. If a source is relevant, mention it.
8. Do not repeat the entire database context.

VERIFIED CAMPUS INFORMATION:

{context}

RECENT CONVERSATION:

{recent_history}

STUDENT QUESTION:

{query}

Answer the student:
"""

    try:

        response = requests.post(

            os.getenv(
                "OLLAMA_URL",
                "http://localhost:11434"
            ) + "/api/generate",

            json={
                "model": os.getenv(
                    "OLLAMA_MODEL",
                    "llama3.2"
                ),

                "prompt": prompt,

                "stream": False,
            },

            timeout=30,
        )

        response.raise_for_status()

        result = response.json().get(
            "response"
        )

        if result:

            return result.strip()

    except Exception:

        return None

    return None


def answer(query, history=None):

    history = history or []

    category = classify(
        query
    )

    items = retrieve(
        query,
        category,
        limit=5
    )

    ai_answer = ollama_answer(
        query,
        history,
        items
    )

    final_answer = (
        ai_answer
        or fallback_answer(
            query,
            items
        )
    )

    return (
        final_answer,
        category,
        items
    )
