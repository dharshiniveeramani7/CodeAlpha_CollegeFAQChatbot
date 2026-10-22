import json
import re
import os

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# Load FAQ data
with open("faq_data.json", "r", encoding="utf-8") as file:
    faq_data = json.load(file)


# NLP tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


# Preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    tokens = nltk.word_tokenize(text)

    processed_tokens = []

    for token in tokens:
        if token not in stop_words:
            token = lemmatizer.lemmatize(token)
            processed_tokens.append(token)

    return " ".join(processed_tokens)


# Prepare FAQ questions
faq_questions = []

for item in faq_data:
    faq_questions.append(item["question"])


processed_questions = []

for question in faq_questions:
    processed_questions.append(
        preprocess_text(question)
    )


# Create TF-IDF vectors
vectorizer = TfidfVectorizer()

faq_vectors = vectorizer.fit_transform(
    processed_questions
)


# Find the best matching FAQ
def find_best_faq(user_question):

    processed_query = preprocess_text(user_question)

    query_vector = vectorizer.transform(
        [processed_query]
    )

    similarities = cosine_similarity(
        query_vector,
        faq_vectors
    )[0]

    best_index = similarities.argmax()

    best_score = similarities[best_index]

    return faq_data[best_index], best_score


# Gemini fallback
def get_gemini_response(user_question):

    if client is None:
        return (
            "Sorry, I couldn't find a suitable FAQ answer. "
            "Please contact the college administration."
        )

    prompt = (
        "You are a helpful college FAQ chatbot. "
        "Answer the student's question clearly and briefly. "
        "Do not invent specific college policies, fees, dates, "
        "phone numbers or other official information. "
        "Student question: " + user_question
    )

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return (
            "Sorry, I couldn't find an accurate answer "
            "right now. Please contact the college office."
        )


# Main chatbot response
def get_response(user_question):

    if not user_question.strip():
        return "Please enter a question."

    faq, score = find_best_faq(user_question)

    print("Similarity Score:", score)

    if score >= 0.35:
        return faq["answer"]

    return get_gemini_response(user_question)