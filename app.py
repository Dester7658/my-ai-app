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
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
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

    # ЕДИНАЯ КНОПКА НАСТРОЕК И ПРОФИЛЯ
    with st.expander("Профиль и Настройки", expanded=False):
        tab_account, tab_profile, tab_settings = st.tabs(["Аккаунт", "О себе", "ИИ"])

        # Вкладка 1: Авторизация (Вход и Выход)
        with tab_account:
            st.markdown("##### Авторизация")
            
            if st.session_state.is_logged_in:
                st.success(f"Вы вошли как:\n**{st.session_state.user_name or st.session_state.user_email}**")
                if st.session_state.user_email:
                    st.caption(f"Email: {st.session_state.user_email}")
                
                if st.button("Выйти из аккаунта", use_container_width=True):
                    st.session_state.is_logged_in = False
                    st.session_state.user_email = ""
                    st.session_state.user_name = ""
                    st.toast("Вы успешно вышли из системы")
                    st.rerun()
            else:
                auth_method = st.radio("Способ входа:", ["По почте", "Через Google"], key="auth_method_choice")
                
                if auth_method == "По почте":
                    login_email = st.text_input("Электронная почта", placeholder="example@mail.com")
                    login_password = st.text_input("Пароль", type="password")
                    
                    if st.button("Войти", use_container_width=True):
                        if login_email and login_password:
                            st.session_state.is_logged_in = True
                            st.session_state.user_email = login_email
                            # Извлекаем имя из почты до знака @
                            st.session_state.user_name = login_email.split("@")[0].capitalize()
                            st.toast("Вход выполнен успешно!", icon="✔")
                            st.rerun()
                        else:
                            st.error("Заполните почту и пароль!")
                            
                elif auth_method == "Через Google":
                    st.caption("Быстрый вход через аккаунт Google")
                    if st.button("Войти через Google", use_container_width=True):
                        # Имитация входа через Google OAuth
                        st.session_state.is_logged_in = True
                        st.session_state.user_email = "user.google@gmail.com"
                        st.session_state.user_name = "Пользователь Google"
                        st.toast("Авторизация через Google прошла успешно!", icon="✔")
                        st.rerun()

        # Вкладка 2: Данные о себе
        with tab_profile:
            st.markdown("##### Данные о пользователе")
            st.caption("Расскажите ИИ о себе для более точных ответов.")
            
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

        # Вкладка 3: Параметры ИИ
        with tab_settings:
            st.markdown("##### Настройки системы")
            selected_model_label = st.selectbox(
                "Модель ИИ:",
                options=list(MODEL_OPTIONS.values()),
                index=0
            )
            selected_model_id = [key for key, value in MODEL_OPTIONS.items() if value == selected_model_label][0]

    st.divider()
    if st.button("Очистить историю чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- СТАНДАРТНЫЙ СВЕТЛЫЙ СТИЛЬ (Без переключения тем) ---
custom_styles = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}
    
    .icon-title { color: #58a6ff; margin-right: 8px; }
    .custom-header { font-size: 2rem; font-weight: 700; margin-bottom: 5px; }
    .custom-sub { color: #8b949e !important; font-size: 0.95rem; margin-bottom: 15px; }
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
    if st.session_state.user_email:
        user_info_context += f"Email пользователя: {st.session_state.user_email}. "
    if st.session_state.user_about:
        user_info_context += f"Фоновая информация/стек: {st.session_state.user_about}."

    # Настройки характера и стилистики
    personality_rules = """
    ПРАВИЛА СТИЛЯ И ОБЩЕНИЯ:
    1. НЕ ИСПОЛЬЗУЙ эмодзи/смайлики (никаких 🤖, ⚡, 😊 и т.д.).
    2. Общайся ЖИВО, естественным человеческим языком! Выражай эмоции словами, метафорами, восклицаниями и форматированием текста (жирный текст, списки).
    3. НЕ выпаливай информацию из профиля сразу при первом приветствии. Используй профиль органично и только к месту.
    4. Если тебя просят написать читы или вредоносный код для видеоигр — отказывайся от такой разработки, но сохраняй дружелюбный тон.
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
