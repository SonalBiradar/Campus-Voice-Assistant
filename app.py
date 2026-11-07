
from pathlib import Path
import sqlite3
import io

import streamlit as st
import speech_recognition as sr
from gtts import gTTS

st.set_page_config(
    page_title="Campus Voice Assistant",
    page_icon="🎓",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DB_NAME = BASE_DIR / "campus.db"
CSS_PATH = BASE_DIR / "style.css"

if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

LANGUAGES = {
    "English": {"speech": "en-IN", "tts": "en"},
    "Hindi": {"speech": "hi-IN", "tts": "hi"},
    "Marathi": {"speech": "mr-IN", "tts": "mr"},
}

SAMPLE_DATA = [
    (
        "library",
        "library|लाइब्रेरी|ग्रंथालय|पुस्तकालय",
        "The library is in Block A, Ground Floor.",
        "लाइब्रेरी ब्लॉक A में, ग्राउंड फ्लोर पर है।",
        "ग्रंथालय ब्लॉक A मध्ये, तळमजल्यावर आहे।"
    ),
    (
        "office",
        "office|admin|कार्यालय|ऑफिस|प्रशासन",
        "The administrative office is in Block A, First Floor.",
        "प्रशासनिक कार्यालय ब्लॉक A की पहली मंजिल पर है।",
        "प्रशासकीय कार्यालय ब्लॉक A च्या पहिल्या मजल्यावर आहे."
    ),
    (
        "lab",
        "computer lab|computer laboratory|कंप्यूटर लैब|संगणक प्रयोगशाळा",
        "The computer lab is in Block B, Second Floor.",
        "कंप्यूटर लैब ब्लॉक B की दूसरी मंजिल पर है।",
        "संगणक प्रयोगशाळा ब्लॉक B च्या दुसऱ्या मजल्यावर आहे."
    ),
    (
        "timetable",
        "timetable|schedule|समय सारणी|टाइमटेबल|वेळापत्रक",
        "The sample first lecture starts at 9 AM. Check the official timetable for your class.",
        "नमूना समय-सारणी के अनुसार पहला व्याख्यान सुबह 9 बजे शुरू होता है। अपनी कक्षा की आधिकारिक समय-सारणी देखें।",
        "नमुना वेळापत्रकानुसार पहिले व्याख्यान सकाळी ९ वाजता सुरू होते. तुमच्या वर्गाचे अधिकृत वेळापत्रक तपासा."
    ),
    (
        "canteen",
        "canteen|food|कैंटीन|खाना|उपहारगृह|जेवण",
        "The canteen is beside Block B.",
        "कैंटीन ब्लॉक B के पास है।",
        "उपहारगृह ब्लॉक B च्या बाजूला आहे."
    ),
    (
        "fees",
        "fees|fee payment|फीस|शुल्क|फी",
        "For fee details, contact the accounts office in Block A.",
        "फीस की जानकारी के लिए ब्लॉक A के लेखा कार्यालय से संपर्क करें।",
        "फीच्या माहितीसाठी ब्लॉक A मधील लेखा कार्यालयाशी संपर्क साधा."
    ),
    (
        "id_card",
        "id card|identity card|आईडी कार्ड|ओळखपत्र",
        "For a student ID card, contact the student section.",
        "स्टूडेंट आईडी कार्ड के लिए छात्र विभाग से संपर्क करें।",
        "विद्यार्थी ओळखपत्रासाठी विद्यार्थी विभागाशी संपर्क साधा."
    ),
    (
        "help",
        "help|contact|staff|मदद|सहायता|मदत|कर्मचारी",
        "Please contact the college help desk or reception for assistance.",
        "सहायता के लिए कॉलेज हेल्प डेस्क या रिसेप्शन से संपर्क करें।",
        "मदतीसाठी कॉलेज हेल्प डेस्क किंवा रिसेप्शनशी संपर्क साधा."
    ),
]


FALLBACK = {
    "English": (
        "Sorry, I could not find that information. "
        "Please contact the college help desk."
    ),
    "Hindi": (
        "क्षमा करें, यह जानकारी नहीं मिली। "
        "कृपया कॉलेज हेल्प डेस्क से संपर्क करें।"
    ),
    "Marathi": (
        "माफ करा, ही माहिती मिळाली नाही. "
        "कृपया कॉलेज हेल्प डेस्कशी संपर्क साधा."
    ),
}

def setup_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS campus_faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                keywords TEXT,
                answer_en TEXT,
                answer_hi TEXT,
                answer_mr TEXT
            )
        """)

        for item in SAMPLE_DATA:
            conn.execute("""
                INSERT OR IGNORE INTO campus_faq
                (topic, keywords, answer_en, answer_hi, answer_mr)
                VALUES (?, ?, ?, ?, ?)
            """, item)

def get_answer(question, language):
    question = question.strip().casefold()

    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
            SELECT keywords, answer_en, answer_hi, answer_mr
            FROM campus_faq
        """).fetchall()

    for keywords, answer_en, answer_hi, answer_mr in rows:
        terms = [
            term.strip().casefold()
            for term in keywords.split("|")
            if term.strip()
        ]

        if any(term in question for term in terms):
            return {
                "English": answer_en,
                "Hindi": answer_hi,
                "Marathi": answer_mr,
            }[language]

    return FALLBACK[language]


setup_database()


st.markdown("""
<div class="hero">
    <h1>🎓 Welcome to JSPM University Campus Voice Assistant .</h1>
    <p>
        Your smart campus companion.
        Ask about college facilities, fees, timetables,
        and student services in English, Hindi, or Marathi.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🎙️ Voice Assistant</h3>
        <p>Speak your question naturally.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>🌍 Multilingual</h3>
        <p>English, Hindi, and Marathi.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>⚡ Quick Answers</h3>
        <p>Find common campus information.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

language = st.selectbox(
    "Choose your language / भाषा चुनें / भाषा निवडा",
    ["English", "Hindi", "Marathi"]
)

st.subheader("🎙️ Ask by voice")

audio = st.audio_input("Record your question")

if st.button("Convert speech to text"):
    if audio is None:
        st.warning("Please record a question first.")
    else:
        try:
            recognizer = sr.Recognizer()
            audio_bytes = audio.getvalue()

            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                recorded_audio = recognizer.record(source)

            recognized_text = recognizer.recognize_google(
                recorded_audio,
                language=LANGUAGES[language]["speech"]
            )

            st.session_state["voice_question"] = recognized_text
            st.success(f"Recognized: {recognized_text}")

        except sr.UnknownValueError:
            st.error(
                "Speech was not clear. Please try again "
                "or type your question."
            )
        except sr.RequestError:
            st.error(
                "Speech recognition service is unavailable. "
                "Please check your internet connection."
            )
        except Exception as error:
            st.error(f"Could not process audio: {error}")

st.subheader("⌨️ Or type your question")

question = st.text_input(
    "Your question",
    key="campus_question",
    placeholder="Example: Where is the library?"
)

if (
    "voice_question" in st.session_state
    and st.session_state.get("campus_question", "") == ""
):
    st.session_state["campus_question"] = st.session_state.pop(
        "voice_question"
    )

if st.button("Get answer", type="primary"):
    question = st.session_state.get("campus_question", "").strip()

    if not question:
        st.warning("Please speak or type a question.")
    else:
        answer = get_answer(question, language)

        st.subheader("💬 Assistant's answer")
        st.write(answer)

        try:
            speech = gTTS(
                text=answer,
                lang=LANGUAGES[language]["tts"]
            )

            audio_buffer = io.BytesIO()
            speech.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.audio(
                audio_buffer.getvalue(),
                format="audio/mp3"
            )

        except Exception:
            st.info(
                "The text answer is available, but audio "
                "could not be generated. Check your internet connection."
            )

st.divider()

st.caption(
    "Prototype demo: locations and timetable are sample data. "
    "Replace them with verified college information before real use."
)
