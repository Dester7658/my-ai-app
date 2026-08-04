import streamlit as st
import os
from groq import Groq

# 1. Настройка страницы
st.set_page_config(
    page_title="DevForge AI | Aynur Sabirov", 
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Безопасное получение API-ключа из Secrets
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# 3. Инициализация состояний
if "messages" not in st.session_state:
    st.session_state.messages = []
if "theme" not in st.session_state:
    st.session_state.theme = "Темная"

# --- БОКОВАЯ ПАНЕЛЬ (SIDEBAR) ---
with st.sidebar:
    st.markdown('<h3><i class="fa-solid fa-hammer icon-title"></i>DevForge AI</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b949e;">Создатель: <b>Айнур Сабиров</b></p>', unsafe_allow_html=True)
    st.divider()

    # ВЫБОР РЕЖИМА ИИ
    st.markdown('<h4><i class="fa-solid fa-robot icon-title"></i>Выбор раздела</h4>', unsafe_allow_html=True)
    app_mode = st.selectbox(
        "Выберите специализацию ИИ:",
        ["Обычный ассистент", "Senior Программист"],
        index=1
    )

    st.divider()

    # НАСТРОЙКИ
    with st.expander("⚙️ Настройки приложения", expanded=True):
        # 1. Выбор языковой модели
        model_choice = st.selectbox(
            "Модель ИИ:",
            [
                "llama-3.3-70b-versatile",
                "llama3-8b-8192",
                "mixtral-8x7b-32768"
            ],
            index=0
        )
        
        # 2. Выбор темы
        selected_theme = st.radio(
            "Тема оформления:",
            ["Темная", "Светлая"],
            index=0 if st.session_state.theme == "Темная" else 1
        )
        st.session_state.theme = selected_theme

        st.divider()
        if st.button("🧹 Очистить историю чата", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.divider()
    
    # БАЗА ЗНАНИЙ
    st.markdown('<h4><i class="fa-regular fa-folder-open icon-title"></i>База знаний</h4>', unsafe_allow_html=True)
    if os.path.exists("knowledge.txt"):
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            knowledge_data = f.read()
    else:
        knowledge_data = "База знаний пуста."
    st.text_area("", knowledge_data, height=120, disabled=True)

# --- ПРИМЕНЕНИЕ ДИНАМИЧЕСКИХ СТИЛЕЙ И ТЕМЫ ---
if st.session_state.theme == "Светлая":
    bg_color = "#ffffff"
    text_color = "#1f2328"
    card_bg = "#f6f8fa"
    border_color = "#d0d7de"
else: # Темная тема
    bg_color = "#0d1117"
    text_color = "#c9d1d9"
    card_bg = "#161b22"
    border_color = "#30363d"

custom_styles = f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stAppHeader {{display: none;}}
    
    /* Применение темы */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stSidebar {{
        background-color: {card_bg};
        border-right: 1px solid {border_color};
    }}
    
    .icon-title {{ color: #58a6ff; margin-right: 8px; }}
    .custom-header {{ font-size: 2rem; font-weight: 700; margin-bottom: 5px; color: {text_color}; }}
    .custom-sub {{ color: #8b949e; font-size: 0.95rem; margin-bottom: 15px; }}
</style>
"""
st.markdown(custom_styles, unsafe_allow_html=True)

# --- ОСНОВНАЯ ОБЛАСТЬ ---
if app_mode == "Senior Программист":
    main_title = "Senior Developer Mode"
    sub_title = f"Модель: {model_choice} | Глубокая аналитика кода"
    avatar_icon = "⚡"
else:
    main_title = "General Assistant Mode"
    sub_title = f"Модель: {model_choice} | Универсальный помощник"
    avatar_icon = "🤖"

st.markdown(f'<div class="custom-header"><i class="fa-solid fa-terminal icon-title"></i>{main_title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="custom-sub">{sub_title}</div>', unsafe_allow_html=True)
st.divider()

# Отрисовка истории сообщений
for message in st.session_state.messages:
    avatar = "👨‍💻" if message["role"] == "user" else avatar_icon
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Обработка ввода
if user_prompt := st.chat_input("Введите ваш запрос..."):
    st.chat_message("user", avatar="👨‍💻").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    if app_mode == "Senior Программист":
        system_role = f"""
        Тебя зовут DevForge AI. Ты — Senior Software Engineer. 
        Твоя специализация: написание идеального кода, отладка, архитектура систем.
        Отвечай как опытный разработчик. Весь код пиши в блоках с подсветкой.
        Твой создатель — Айнур Сабиров.
        БАЗА ЗНАНИЙ: {knowledge_data}
        """
    else:
        system_role = f"""
        Тебя зовут DevForge AI. Ты — универсальный ИИ-помощник. 
        Помогай с любыми текстами, идеями и вопросами. Будь вежливым и полезным.
        Твой создатель — Айнур Сабиров.
        """

    api_messages = [{"role": "system", "content": system_role}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant", avatar=avatar_icon):
        # Используем выбранную модель из настроек!
        completion = client.chat.completions.create(
            messages=api_messages,
            model=model_choice,
            stream=True
        )
        
        def stream_data():
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        reply = st.write_stream(stream_data)
        st.session_state.messages.append({"role": "assistant", "content": reply})
