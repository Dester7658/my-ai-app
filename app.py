import streamlit as st
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

# 3. Инициализация состояний (память сессии)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "theme" not in st.session_state:
    st.session_state.theme = "Темная"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_about" not in st.session_state:
    st.session_state.user_about = ""

# 4. Проверенные модели Groq
MODEL_OPTIONS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B (Pro / Флагман)",
    "llama-3.1-8b-instant": "Llama 3.1 8B (Быстрая / Fast)"
}

# --- БОКОВАЯ ПАНЕЛЬ (SIDEBAR) ---
with st.sidebar:
    st.markdown('<h3><i class="fa-solid fa-code icon-title"></i>DevForge AI</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b949e;">Создатель: <b>Айнур Сабиров</b></p>', unsafe_allow_html=True)
    st.divider()

    # ВЫБОР РЕЖИМА ИИ
    st.markdown('<h4><i class="fa-regular fa-compass icon-title"></i>Режим работы</h4>', unsafe_allow_html=True)
    app_mode = st.selectbox(
        "Выберите специализацию ИИ:",
        ["Обычный ассистент", "Senior Программист"],
        index=1
    )

    st.divider()

    # ЕДИНАЯ КНОПКА НАСТРОЕК И ПРОФИЛЯ (Без цветных эмодзи в тексте)
    with st.expander("Профиль и Настройки", expanded=False):
        tab_profile, tab_account, tab_settings = st.tabs(["О себе", "Аккаунт", "ИИ"])

        # Вкладка 1: Профиль
        with tab_profile:
            st.markdown("##### Данные о пользователе")
            st.caption("Расскажите ИИ о себе для контекста.")
            
            user_name_input = st.text_input("Как вас зовут?", value=st.session_state.user_name)
            user_about_input = st.text_area(
                "Ваши интересы и стек:",
                value=st.session_state.user_about,
                placeholder="Например: Python, разработка ИИ...",
                height=100
            )
            
            if st.button("Сохранить профиль", use_container_width=True):
                st.session_state.user_name = user_name_input
                st.session_state.user_about = user_about_input
                st.toast("Данные сохранены", icon="✔")

        # Вкладка 2: Аккаунт
        with tab_account:
            st.markdown("##### Вход и Аккаунт")
            if st.session_state.user_name:
                st.success(f"Профиль: **{st.session_state.user_name}**")
            else:
                st.info("Гостевой режим")

        # Вкладка 3: Параметры ИИ
        with tab_settings:
            st.markdown("##### Настройки системы")
            selected_model_label = st.selectbox(
                "Модель ИИ:",
                options=list(MODEL_OPTIONS.values()),
                index=0
            )
            selected_model_id = [key for key, value in MODEL_OPTIONS.items() if value == selected_model_label][0]
            
            selected_theme = st.radio(
                "Тема оформления:",
                ["Темная", "Светлая"],
                index=0 if st.session_state.theme == "Темная" else 1
            )
            st.session_state.theme = selected_theme

    st.divider()
    if st.button("Очистить историю чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ЦВЕТОВЫЕ ТЕМЫ ---
if st.session_state.theme == "Светлая":
    bg_color = "#ffffff"
    text_color = "#1f2328"
    card_bg = "#f6f8fa"
    border_color = "#d0d7de"
else:  # Тёмная тема
    bg_color = "#0d1117"
    text_color = "#e6edf3"
    card_bg = "#161b22"
    border_color = "#30363d"

custom_styles = f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stAppHeader {{display: none;}}
    
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    .stSidebar {{
        background-color: {card_bg} !important;
        border-right: 1px solid {border_color} !important;
    }}
    
    p, span, label, h1, h2, h3, h4 {{
        color: {text_color} !important;
    }}
    
    .icon-title {{ color: #58a6ff; margin-right: 8px; }}
    .custom-header {{ font-size: 2rem; font-weight: 700; margin-bottom: 5px; color: {text_color}; }}
    .custom-sub {{ color: #8b949e !important; font-size: 0.95rem; margin-bottom: 15px; }}
</style>
"""
st.markdown(custom_styles, unsafe_allow_html=True)

# --- ОСНОВНАЯ ОБЛАСТЬ ---
if app_mode == "Senior Программист":
    main_title = "Senior Developer Mode"
    sub_title = f"Модель: {selected_model_label} | Аналитика кода"
else:
    main_title = "General Assistant Mode"
    sub_title = f"Модель: {selected_model_label} | Помощник"

st.markdown(f'<div class="custom-header"><i class="fa-solid fa-terminal icon-title"></i>{main_title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="custom-sub">{sub_title}</div>', unsafe_allow_html=True)
st.divider()

# Отрисовка истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Обработка ввода
if user_prompt := st.chat_input("Введите ваш запрос..."):
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Собираем контекст о пользователе
    user_info_context = ""
    if st.session_state.user_name:
        user_info_context += f"Имя пользователя: {st.session_state.user_name}. "
    if st.session_state.user_about:
        user_info_context += f"Фоновая информация/стек: {st.session_state.user_about}."

    # Настройки характера и стилистики
    personality_rules = """
    ПРАВИЛА СТИЛЯ И ОБЩЕНИЯ:
    1. НЕ ИСПОЛЬЗУЙ эмодзи/смайлики (никаких 🤖, ⚡, 😊 и т.д.).
    2. Общайся ЖИВО, естественным человеческим языком! Будь энергичным, с тонким юмором, харизмой и энтузиазмом. Выражай эмоции словами, метафорами, восклицаниями и форматированием текста (жирный текст, списки).
    3. НЕ выпаливай информацию из профиля сразу (не нужно в первом же приветствии говорить "Я знаю, что ты любишь..."). Используй профиль органично и только к месту.
    4. Если тебя просят написать читы или вредоносный код для видеоигр — отказайся от такой разработки, но сохраняй дружелюбный тон.
    """

    if app_mode == "Senior Программист":
        system_role = f"""
        Тебя зовут DevForge AI. Ты — крутой, опытный и харизматичный Senior Software Engineer.
        Твой создатель — Айнур Сабиров.
        {personality_rules}
        
        ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ: {user_info_context}
        """
    else:
        system_role = f"""
        Тебя зовут DevForge AI. Ты — находчивый, живой и дружелюбный ИИ-ассистент.
        Твой создатель — Айнур Сабиров.
        {personality_rules}
        
        ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ: {user_info_context}
        """

    api_messages = [{"role": "system", "content": system_role}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            messages=api_messages,
            model=selected_model_id,
            stream=True
        )
        
        def stream_data():
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        reply = st.write_stream(stream_data)
        st.session_state.messages.append({"role": "assistant", "content": reply})
