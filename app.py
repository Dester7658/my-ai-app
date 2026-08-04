import streamlit as st
from groq import Groq
from supabase import create_client, Client

# 1. Настройка страницы
st.set_page_config(
    page_title="DevForge AI | Aynur Sabirov", 
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Инициализация сервисов
API_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=API_KEY) if API_KEY else None

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        pass

# 3. Инициализация состояний сессии
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

# --- АВТОМАТИЧЕСКАЯ ПРОВЕРКА И СОХРАНЕНИЕ СЕССИИ СУПАБЕЙС (ПРИ ПЕРЕЗАГРУЗКЕ) ---
if supabase and not st.session_state.is_logged_in:
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.is_logged_in = True
            st.session_state.user_email = session.user.email
            if not st.session_state.user_name:
                st.session_state.user_name = session.user.email.split("@")[0].capitalize()
    except Exception:
        pass

# 4. Проверенные модели Groq
MODEL_OPTIONS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B (Pro / Флагман)",
    "llama-3.1-8b-instant": "Llama 3.1 8B (Быстрая / Fast)"
}

# --- ИСПРАВЛЕННЫЕ СТИЛИ (Сохраняем кнопку открытия шторки) ---
custom_styles = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* Скрываем только лишнее меню, оставляем кнопку открывания боковой панели */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .icon-title { color: #58a6ff; margin-right: 8px; }
    .custom-header { font-size: 2rem; font-weight: 700; margin-bottom: 5px; }
    .custom-sub { color: #8b949e !important; font-size: 0.95rem; margin-bottom: 15px; }
</style>
"""
st.markdown(custom_styles, unsafe_allow_html=True)

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

    # НАСТРОЙКИ И АВТОРИЗАЦИЯ
    with st.expander("Профиль и Настройки", expanded=False):
        tab_account, tab_profile, tab_settings = st.tabs(["Аккаунт", "О себе", "ИИ"])

        # Вкладка 1: Авторизация через Supabase
        with tab_account:
            st.markdown("##### Авторизация")
            
            if st.session_state.is_logged_in:
                st.success(f"Вы вошли как:\n**{st.session_state.user_name or st.session_state.user_email}**")
                if st.session_state.user_email:
                    st.caption(f"Email: {st.session_state.user_email}")
                
                if st.button("Выйти из аккаунта", use_container_width=True):
                    if supabase:
                        try:
                            supabase.auth.sign_out()
                        except Exception:
                            pass
                    st.session_state.is_logged_in = False
                    st.session_state.user_email = ""
                    st.session_state.user_name = ""
                    st.toast("Вы успешно вышли из системы")
                    st.rerun()
            else:
                auth_mode = st.radio("Действие:", ["Вход", "Регистрация"], key="auth_mode")
                auth_method = st.radio("Способ:", ["По почте", "Через Google"], key="auth_method")
                
                if auth_method == "По почте":
                    login_email = st.text_input("Электронная почта", placeholder="example@mail.com")
                    login_password = st.text_input("Пароль", type="password")
                    
                    if auth_mode == "Вход":
                        if st.button("Войти", use_container_width=True):
                            if login_email and login_password:
                                if supabase:
                                    try:
                                        res = supabase.auth.sign_in_with_password({
                                            "email": login_email,
                                            "password": login_password
                                        })
                                        st.session_state.is_logged_in = True
                                        st.session_state.user_email = res.user.email
                                        st.session_state.user_name = login_email.split("@")[0].capitalize()
                                        st.toast("Успешная авторизация!", icon="✔")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Ошибка входа: {e}")
                                else:
                                    st.warning("Supabase не подключен. Проверьте Secrets.")
                            else:
                                st.error("Заполните почту и пароль!")
                    else: # Регистрация
                        if st.button("Зарегистрироваться", use_container_width=True):
                            if login_email and login_password:
                                if supabase:
                                    try:
                                        res = supabase.auth.sign_up({
                                            "email": login_email,
                                            "password": login_password
                                        })
                                        st.success("Регистрация успешна! Проверьте почту для подтверждения.")
                                    except Exception as e:
                                        st.error(f"Ошибка регистрации: {e}")
                                else:
                                    st.error("Подключите Supabase в Secrets!")

                elif auth_method == "Через Google":
                    st.caption("Вход через защищённый сервис Google OAuth 2.0")
                    if st.button("Войти через Google", use_container_width=True):
                        if supabase:
                            try:
                                res = supabase.auth.sign_in_with_oauth({
                                    "provider": "google"
                                })
                                if res.url:
                                    st.markdown(f"[Перейти к авторизации Google]({res.url})")
                            except Exception as e:
                                st.error(f"Ошибка Google Auth: {e}")
                        else:
                            st.warning("Вход через Google доступен при настроенном Supabase.")

        # Вкладка 2: Данные о себе
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

    # Контекст пользователя
    user_info_context = ""
    if st.session_state.user_name:
        user_info_context += f"Имя пользователя: {st.session_state.user_name}. "
    if st.session_state.user_email:
        user_info_context += f"Email пользователя: {st.session_state.user_email}. "
    if st.session_state.user_about:
        user_info_context += f"Фоновая информация/стек: {st.session_state.user_about}."

    # Настройки поведения
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
        if client:
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
        else:
            st.error("Ключ GROQ_API_KEY не найден в Secrets!")
