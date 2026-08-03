import streamlit as st
import os
from groq import Groq

# 1. API-ключ Groq
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 2. Настройка страницы
st.set_page_config(
    page_title="DevAssistant AI | Aynur Sabirov", 
    page_icon="⚡",
    layout="wide"
)

# 3. Подключаем векторные иконки Font Awesome и CSS-стили
icon_styles = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
    /* Стилизация шрифтов и элементов */
    .icon-title {
        color: #58a6ff;
        margin-right: 8px;
    }
    .custom-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .custom-sub {
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 15px;
    }
</style>
"""
st.markdown(icon_styles, unsafe_allow_html=True)

# 4. Загрузка Базы Знаний
@st.cache_data
def load_knowledge_base():
    if os.path.exists("knowledge.txt"):
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Мои личные заметки и шпаргалки по коду."

knowledge_data = load_knowledge_base()

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.markdown('<h3><i class="fa-solid fa-code icon-title"></i>DevAssistant AI</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b949e;"><i class="fa-regular fa-user"></i> Создатель: <b>Айнур Сабиров</b></p>', unsafe_allow_html=True)
    st.divider()
    
    st.markdown('<h4><i class="fa-regular fa-folder-open icon-title"></i>База знаний</h4>', unsafe_allow_html=True)
    st.text_area("", knowledge_data, height=200, disabled=True)
    
    st.divider()
    if st.button("🧹 Очистить историю", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ОСНОВНАЯ ОБЛАСТЬ ---
st.markdown('<div class="custom-header"><i class="fa-solid fa-terminal icon-title"></i>Персональный ИИ-Senior Developer</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-sub">Умный ассистент по программированию • Версия 2.0</div>', unsafe_allow_html=True)
st.divider()

# 5. Инициализация памяти диалога
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отрисовка сообщений
for message in st.session_state.messages:
    avatar = "👨‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. Обработка запроса
if user_prompt := st.chat_input("Напиши код, спроси о баге или архитектуре..."):
    st.chat_message("user", avatar="👨‍💻").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    system_instruction = f"""
    Ты — опытный Senior Software Engineer и терпеливый ментор по программированию. 
    Твой создатель — Айнур Сабиров.
    
    Твои задачи:
    1. Помогать с кодом на любых языках (Python, C#, C++, JS, SQL и т.д.).
    2. Оформлять весь код в красивых Markdown-блоках с подсветкой синтаксиса.
    3. Отвечать подробно, профессионально и понятно.
    
    БАЗА ЗНАНИЙ СОЗДАТЕЛЯ:
    {knowledge_data}
    """

    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant", avatar="🤖"):
        completion = client.chat.completions.create(
            messages=api_messages,
            model="llama-3.3-70b-versatile",
            stream=True
        )
        
        def stream_data():
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        reply = st.write_stream(stream_data)
        st.session_state.messages.append({"role": "assistant", "content": reply})