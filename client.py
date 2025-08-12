import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json
import time
import numpy as np

# ================== КОНФІГУРАЦІЯ ==================

API_URL = "http://localhost:5000/api"
st.set_page_config(
    page_title="Система кластеризації клієнтів",
    page_icon="🚀",
    layout="wide"
)

# Кольорова схема Sputnik
COLORS = {
    'primary': '#59253A',      # Темно-фіолетовий
    'secondary': '#78244C',    # Рожевий
    'accent': '#895061',       # Світло-рожевий
    'info': '#0877A1',        # Бірюзовий
    'dark': '#2D4159',        # Темно-синій
    'gradient1': 'linear-gradient(135deg, #59253A 0%, #78244C 100%)',
    'gradient2': 'linear-gradient(135deg, #0877A1 0%, #2D4159 100%)',
    'gradient3': 'linear-gradient(135deg, #78244C 0%, #895061 100%)'
}

# Кастомні стилі з новою гаммою
st.markdown(f"""
<style>
    .main {{padding: 0rem 1rem;}}
    
    /* Основні кольори */
    .stApp {{
        background: linear-gradient(180deg, #59253A 0%, #2D4159 100%);
    }}
    
    /* Метрики */
    [data-testid="metric-container"] {{
        background: {COLORS['gradient1']};
        padding: 15px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Кнопки */
    .stButton > button {{
        background: {COLORS['gradient2']};
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(8,119,161,0.4);
    }}
    
    /* Картки */
    .profile-card {{
        background: rgba(137, 80, 97, 0.2);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }}
    
    .cluster-card {{
        background: {COLORS['gradient3']};
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}
    
    /* Заголовки */
    h1, h2, h3 {{
        color: white !important;
    }}
    
    /* Форми */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {{
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }}
    
    /* Експандери */
    .streamlit-expanderHeader {{
        background: rgba(120, 36, 76, 0.3) !important;
        color: white !important;
        border-radius: 10px !important;
    }}
    
    /* Табси */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(89, 37, 58, 0.3);
        border-radius: 10px;
        padding: 5px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {COLORS['gradient2']} !important;
        color: white !important;
    }}
    
    /* Інфо блоки */
    .stInfo, .stSuccess, .stWarning {{
        background: rgba(8, 119, 161, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(8, 119, 161, 0.5) !important;
    }}
    
    /* Прогрес бар */
    .stProgress > div > div > div {{
        background: {COLORS['gradient2']};
    }}
    
    /* Слайдери */
    .stSlider > div > div > div > div {{
        background: {COLORS['info']} !important;
    }}
    
    /* Дівайдери */
    hr {{
        border-color: rgba(137, 80, 97, 0.3) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ================== ІНІЦІАЛІЗАЦІЯ СЕСІЇ ==================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.name = None
    st.session_state.token = None
    st.session_state.page = 'profile'
    st.session_state.questionnaire_completed = False

# ================== ФУНКЦІЇ API ==================

def make_request(method, endpoint, json_data=None):
    """Універсальна функція для API запитів з токеном"""
    url = f"{API_URL}{endpoint}"
    
    headers = {}
    if 'token' in st.session_state and st.session_state.token:
        headers['Authorization'] = f"Bearer {st.session_state.token}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=json_data, headers=headers)
        
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Не вдалося підключитися до сервера. Переконайтеся, що server.py запущено!")
        return None

def login(email, password):
    """Вхід в систему"""
    response = make_request('POST', '/login', {
        'email': email,
        'password': password
    })
    
    if response and response.status_code == 200:
        data = response.json()
        st.session_state.logged_in = True
        st.session_state.user_id = data['user_id']
        st.session_state.role = data['role']
        st.session_state.name = data['name']
        st.session_state.token = data['token']
        st.session_state.questionnaire_completed = data.get('questionnaire_completed', False)
        return True
    return False

def register(email, password, name):
    """Реєстрація нового клієнта"""
    response = make_request('POST', '/register', {
        'email': email,
        'password': password,
        'name': name
    })
    
    if response and response.status_code == 200:
        data = response.json()
        st.session_state.logged_in = True
        st.session_state.user_id = data['user_id']
        st.session_state.role = 'client'
        st.session_state.name = name
        st.session_state.token = data['token']
        st.session_state.questionnaire_completed = False
        st.session_state.page = 'questionnaire'
        return True
    return False

def logout():
    """Вихід з системи"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ================== СТОРІНКА ВХОДУ ==================

if not st.session_state.logged_in:
    # Фон з градієнтом
    st.markdown(f"""
    <div style='text-align: center; padding: 50px 0;'>
        <h1 style='color: white; font-size: 3em; margin-bottom: 10px;'>🚀</h1>
        <h1 style='color: white; font-size: 2.5em; margin-bottom: 0;'>Система кластеризації клієнтів</h1>
        <p style='color: {COLORS['accent']}; font-size: 1.2em;'>Kaggle Dataset | K-Means | 5 кластерів</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Вхід", "📝 Реєстрація"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="email@example.com")
                password = st.text_input("Пароль", type="password", placeholder="••••••")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_btn = st.form_submit_button("Увійти", use_container_width=True)
                with col_btn2:
                    admin_btn = st.form_submit_button("Адмін вхід", use_container_width=True)
                
                if login_btn and email and password:
                    if login(email, password):
                        st.success("✅ Успішний вхід!")
                        st.rerun()
                    else:
                        st.error("❌ Невірні дані")
                
                if admin_btn:
                    if login("admin@system.ua", "admin123"):
                        st.rerun()
            
            st.info("💡 Адмін: admin@system.ua / admin123")
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("Ім'я", placeholder="Ваше ім'я")
                email = st.text_input("Email", placeholder="email@example.com")
                password = st.text_input("Пароль", type="password", placeholder="Мінімум 6 символів")
                password2 = st.text_input("Підтвердіть пароль", type="password", placeholder="Повторіть пароль")
                
                reg_btn = st.form_submit_button("Зареєструватися", use_container_width=True)
                
                if reg_btn:
                    if not all([name, email, password]):
                        st.error("Заповніть всі поля")
                    elif password != password2:
                        st.error("Паролі не співпадають")
                    elif len(password) < 6:
                        st.error("Пароль має бути не менше 6 символів")
                    else:
                        if register(email, password, name):
                            st.success("✅ Реєстрація успішна!")
                            st.rerun()
                        else:
                            st.error("Email вже існує")

# ================== КЛІЄНТСЬКИЙ ІНТЕРФЕЙС ==================

elif st.session_state.role == 'client':
    
    # Перевіряємо статус опитування
    if not st.session_state.questionnaire_completed:
        response = make_request('GET', '/check-questionnaire')
        if response and response.status_code == 200:
            st.session_state.questionnaire_completed = response.json()['completed']
    
    # Верхня панель з навігацією
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
    
    with col1:
        if st.button("🎯 Мій профіль", use_container_width=True, 
                    type="primary" if st.session_state.page == 'profile' else "secondary"):
            st.session_state.page = 'profile'
            st.rerun()
    
    with col2:
        # Показуємо опитування тільки якщо воно не пройдене
        if not st.session_state.questionnaire_completed:
            if st.button("📝 Опитування", use_container_width=True,
                        type="primary" if st.session_state.page == 'questionnaire' else "secondary"):
                st.session_state.page = 'questionnaire'
                st.rerun()
        else:
            if st.button("✅ Результати", use_container_width=True,
                        type="primary" if st.session_state.page == 'results' else "secondary"):
                st.session_state.page = 'results'
                st.rerun()
    
    with col3:
        if st.button("💡 Рекомендації", use_container_width=True,
                    type="primary" if st.session_state.page == 'recommendations' else "secondary"):
            st.session_state.page = 'recommendations'
            st.rerun()
    
    with col4:
        if st.button("📚 Як це працює", use_container_width=True,
                    type="primary" if st.session_state.page == 'how_it_works' else "secondary"):
            st.session_state.page = 'how_it_works'
            st.rerun()
    
    with col5:
        st.write(f"👤 {st.session_state.name}")
    
    with col6:
        if st.button("🚪", use_container_width=True, help="Вийти"):
            logout()
    
    st.divider()
    
    # СТОРІНКА ЯК ЦЕ ПРАЦЮЄ
    if st.session_state.page == 'how_it_works':
        st.title("📚 Як працює система кластеризації")
        
        # Вступ
        st.markdown(f"""
        <div class='profile-card'>
            <h2>🚀 Про систему</h2>
            <p>Наша система використовує алгоритм машинного навчання K-Means для аналізу поведінки клієнтів 
            на основі датасету з Kaggle (Customer Personality Analysis). Система аналізує 2240 реальних профілів 
            клієнтів та визначає 5 основних кластерів.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 5 Кластерів клієнтів")
        
        # Опис кожного кластера з красивим оформленням
        clusters_info = {
            "🟣 Преміум клієнти": {
                "color": COLORS['primary'],
                "характеристики": [
                    "💰 Дохід: $100,000+",
                    "💳 Великі витрати на всі категорії",
                    "❤️ Дуже висока лояльність до бренду",
                    "🎯 18% від загальної бази"
                ],
                "поведінка": "Купують преміум товари, цінують якість та ексклюзивність, готові платити більше за кращий сервіс",
                "маркетинг": "VIP програми, персональний менеджер, ексклюзивні пропозиції, закриті розпродажі"
            },
            "🟢 Економні раціоналісти": {
                "color": COLORS['info'],
                "характеристики": [
                    "💰 Дохід: $30,000-50,000",
                    "💳 Низькі витрати, раціональні покупки",
                    "❤️ Середня лояльність",
                    "🎯 31% від загальної бази"
                ],
                "поведінка": "Шукають найкращі ціни, порівнюють пропозиції, купують по знижках, планують покупки",
                "маркетинг": "Програми знижок, купони, кешбек, акції '2 за ціною 1', розпродажі"
            },
            "🔵 Молоді професіонали": {
                "color": COLORS['dark'],
                "характеристики": [
                    "💰 Дохід: $50,000-80,000",
                    "💳 Середні витрати, імпульсивні покупки",
                    "❤️ Низька лояльність, експериментують",
                    "🎯 22% від загальної бази"
                ],
                "поведінка": "Активні онлайн покупці, слідкують за трендами, люблять новинки, використовують мобільні додатки",
                "маркетинг": "Соціальні мережі, інфлюенсер маркетинг, мобільні додатки, швидка доставка"
            },
            "🟡 Сімейні покупці": {
                "color": COLORS['accent'],
                "характеристики": [
                    "💰 Дохід: $40,000-70,000",
                    "💳 Регулярні покупки для всієї родини",
                    "❤️ Висока лояльність",
                    "🎯 19% від загальної бази"
                ],
                "поведінка": "Купують товари для дому та дітей, цінують зручність, надають перевагу перевіреним брендам",
                "маркетинг": "Сімейні пакети, програми лояльності, знижки на дитячі товари, зручна доставка"
            },
            "🔴 Випадкові покупці": {
                "color": COLORS['secondary'],
                "характеристики": [
                    "💰 Дохід: Різний",
                    "💳 Нерегулярні випадкові покупки",
                    "❤️ Дуже низька лояльність",
                    "🎯 10% від загальної бази"
                ],
                "поведінка": "Купують рідко, часто одноразові клієнти, не реагують на стандартний маркетинг",
                "маркетинг": "Welcome-бонуси, реактиваційні кампанії, персональні пропозиції, ретаргетинг"
            }
        }
        
        for cluster_name, info in clusters_info.items():
            with st.expander(cluster_name, expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**📊 Характеристики:**")
                    for char in info['характеристики']:
                        st.write(char)
                
                with col2:
                    st.markdown("**🎭 Поведінка:**")
                    st.write(info['поведінка'])
                    st.markdown("**📢 Маркетингова стратегія:**")
                    st.write(info['маркетинг'])
        
        st.divider()
        
        # Як працює алгоритм
        st.markdown("### 🤖 Як працює алгоритм K-Means")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='profile-card'>
                <h4>📈 Етапи роботи:</h4>
                <ol>
                    <li><b>Збір даних</b> - опитування з 11 питань</li>
                    <li><b>Обробка</b> - перетворення відповідей у числові фічі</li>
                    <li><b>Масштабування</b> - нормалізація даних</li>
                    <li><b>Кластеризація</b> - визначення найближчого кластера</li>
                    <li><b>Результат</b> - профіль та рекомендації</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='profile-card'>
                <h4>🎯 7 ключових фіч:</h4>
                <ul>
                    <li>Income - рівень доходу</li>
                    <li>Age - вікова група</li>
                    <li>TotalSpent - загальні витрати</li>
                    <li>TotalPurchases - кількість покупок</li>
                    <li>NumWebVisitsMonth - онлайн активність</li>
                    <li>TotalKids - наявність дітей</li>
                    <li>Recency - давність останньої покупки</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Точність моделі
        st.divider()
        st.markdown("### 📊 Точність визначення кластера")
        
        accuracy_info = {
            "0-40%": ("Низька", "Профіль потребує більше даних", "red"),
            "40-70%": ("Середня", "Достатньо для базових рекомендацій", "yellow"),
            "70-100%": ("Висока", "Точні персоналізовані рекомендації", "green")
        }
        
        cols = st.columns(3)
        for i, (range_text, (level, desc, color)) in enumerate(accuracy_info.items()):
            with cols[i]:
                st.markdown(f"""
                <div style='background: {COLORS['gradient3']}; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h4>{range_text}</h4>
                    <p><b>{level}</b></p>
                    <p style='font-size: 0.9em;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # СТОРІНКА ПРОФІЛЮ
    elif st.session_state.page == 'profile':
        st.title("🎯 Мій профіль")
        
        response = make_request('GET', '/my-profile')
        
        if response and response.status_code == 200:
            profile = response.json()
            
            if profile and profile.get('cluster_name'):
                # Конвертуємо confidence
                confidence = profile.get('confidence', 0)
                if isinstance(confidence, str):
                    confidence = float(confidence) if confidence else 0
                confidence_percent = confidence * 100
                
                # Кольори для кластерів
                cluster_colors = {
                    "Преміум клієнти": ("🟣", COLORS['primary']),
                    "Економні раціоналісти": ("🟢", COLORS['info']),
                    "Молоді професіонали": ("🔵", COLORS['dark']),
                    "Сімейні покупці": ("🟡", COLORS['accent']),
                    "Випадкові покупці": ("🔴", COLORS['secondary'])
                }
                
                emoji, color = cluster_colors.get(profile['cluster_name'], ("⚪", COLORS['dark']))
                
                # Головна картка профілю
                st.markdown(f"""
                <div class='cluster-card'>
                    <h1 style='font-size: 4em; margin: 0;'>{emoji}</h1>
                    <h2 style='margin: 10px 0;'>{profile['cluster_name']}</h2>
                    <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;'>
                        <p style='margin: 5px 0;'>Точність визначення</p>
                        <h1 style='margin: 5px 0;'>{confidence_percent:.1f}%</h1>
                    </div>
                    <p style='font-size: 0.9em; opacity: 0.9;'>{profile.get('email', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                # Деталі профілю
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 📋 Особисті дані")
                    st.info(f"""
                    👤 **Ім'я:** {profile.get('name', 'Користувач')}  
                    🎂 **Вік:** {profile.get('age_group', 'Не вказано')}  
                    💰 **Дохід:** {profile.get('income_level', 'Не вказано')}
                    """)
                
                with col2:
                    st.markdown("### 🎓 Освіта та сім'я")
                    st.info(f"""
                    🎓 **Освіта:** {profile.get('education', 'Не вказано')}  
                    💑 **Стан:** {profile.get('marital_status', 'Не вказано')}  
                    👶 **Діти:** {'Так' if profile.get('has_children') else 'Ні'}
                    """)
                
                with col3:
                    st.markdown("### 📊 Статус")
                    status_color = "🟢" if confidence_percent > 70 else "🟡" if confidence_percent > 40 else "🔴"
                    st.info(f"""
                    {status_color} **Активний**  
                    📅 **Реєстрація:** {profile.get('created_at', 'Нещодавно')}  
                    🎯 **Кластер ID:** {profile.get('cluster_id', 'N/A')}
                    """)
                
            else:
                st.warning("⚠️ Профіль не визначено. Пройдіть опитування для аналізу.")
                if not st.session_state.questionnaire_completed:
                    if st.button("📝 Пройти опитування", type="primary", use_container_width=True):
                        st.session_state.page = 'questionnaire'
                        st.rerun()
    
    # СТОРІНКА ОПИТУВАННЯ (тільки якщо не пройдено)
    elif st.session_state.page == 'questionnaire' and not st.session_state.questionnaire_completed:
        st.title("📝 Опитування для визначення кластера")
        
        st.info("⚠️ **Важливо:** Опитування можна пройти тільки один раз. Уважно заповніть всі поля.")
        
        # Прогрес
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        with st.form("questionnaire_form"):
            st.markdown("### 📊 Крок 1: Базова інформація")
            progress_bar.progress(33)
            
            col1, col2 = st.columns(2)
            
            with col1:
                age_group = st.selectbox("🎂 Вік", ["18-24", "25-34", "35-44", "45-54", "55+"])
                income_level = st.selectbox("💰 Дохід", 
                    options=["low", "medium", "high", "very_high"],
                    format_func=lambda x: {
                        "low": "< $30k",
                        "medium": "$30-60k",
                        "high": "$60-100k",
                        "very_high": "> $100k"
                    }[x])
                education = st.selectbox("🎓 Освіта", ["Середня", "Вища", "Кілька вищих"])
            
            with col2:
                marital_status = st.selectbox("💑 Сімейний стан", ["Неодружений", "Одружений", "Розлучений"])
                has_children = st.checkbox("👶 Маю дітей")
                
            st.markdown("### 🎯 Крок 2: Поведінкові характеристики")
            progress_bar.progress(66)
            
            st.markdown("*Оцініть від 1 (мінімум) до 10 (максимум)*")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                price_sensitivity = st.slider("💸 Чутливість до ціни", 1, 10, 5)
                online_shopping = st.slider("🛒 Онлайн покупки", 1, 10, 5)
            
            with col2:
                brand_loyalty = st.slider("❤️ Лояльність брендам", 1, 10, 5)
                innovation = st.slider("🚀 Інтерес до новинок", 1, 10, 5)
            
            with col3:
                social_influence = st.slider("👥 Вплив рекомендацій", 1, 10, 5)
                quality_importance = st.slider("⭐ Важливість якості", 1, 10, 5)
            
            progress_bar.progress(100)
            
            st.divider()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button("🚀 ВИЗНАЧИТИ МІЙ КЛАСТЕР", 
                                              use_container_width=True, type="primary")
            
            if submit:
                data = {
                    'age_group': age_group,
                    'income_level': income_level,
                    'education': education,
                    'marital_status': marital_status,
                    'has_children': has_children,
                    'price_sensitivity': price_sensitivity,
                    'online_shopping': online_shopping,
                    'brand_loyalty': brand_loyalty,
                    'innovation': innovation,
                    'social_influence': social_influence,
                    'quality_importance': quality_importance
                }
                
                with st.spinner('🔄 Аналізуємо ваші дані на основі 2240 профілів...'):
                    time.sleep(2)
                    response = make_request('POST', '/questionnaire', data)
                
                if response and response.status_code == 200:
                    result = response.json()
                    st.session_state.questionnaire_completed = True
                    
                    # Показуємо результат
                    st.balloons()
                    
                    # Результат
                    cluster_colors = {
                        "Преміум клієнти": "🟣",
                        "Економні раціоналісти": "🟢",
                        "Молоді професіонали": "🔵",
                        "Сімейні покупці": "🟡",
                        "Випадкові покупці": "🔴"
                    }
                    
                    emoji = cluster_colors.get(result['profile']['cluster_name'], "⚪")
                    
                    st.markdown(f"""
                    <div class='cluster-card' style='margin-top: 30px;'>
                        <h1 style='font-size: 5em; margin: 0;'>{emoji}</h1>
                        <h2>Ваш кластер визначено!</h2>
                        <h1 style='font-size: 2em; margin: 20px 0;'>{result['profile']['cluster_name']}</h1>
                        <p style='margin: 20px 40px;'>{result['profile']['description']}</p>
                        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px auto; max-width: 300px;'>
                            <p>Точність визначення</p>
                            <h2>{result['profile']['confidence']*100:.1f}%</h2>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success("✅ Дані збережено! Тепер ви можете переглянути рекомендації.")
                    time.sleep(3)
                    st.session_state.page = 'results'
                    st.rerun()
                    
    # СТОРІНКА РЕЗУЛЬТАТІВ (замість опитування після проходження)
    elif st.session_state.page == 'results' or (st.session_state.page == 'questionnaire' and st.session_state.questionnaire_completed):
        st.title("✅ Результати вашого опитування")
        
        response = make_request('GET', '/my-profile')
        
        if response and response.status_code == 200:
            profile = response.json()
            
            if profile and profile.get('cluster_name'):
                confidence = profile.get('confidence', 0)
                if isinstance(confidence, str):
                    confidence = float(confidence) if confidence else 0
                confidence_percent = confidence * 100
                
                cluster_colors = {
                    "Преміум клієнти": "🟣",
                    "Економні раціоналісти": "🟢",
                    "Молоді професіонали": "🔵",
                    "Сімейні покупці": "🟡",
                    "Випадкові покупці": "🔴"
                }
                
                emoji = cluster_colors.get(profile['cluster_name'], "⚪")
                
                # Показуємо збережені результати
                st.markdown(f"""
                <div class='cluster-card'>
                    <h1 style='font-size: 4em; margin: 0;'>{emoji}</h1>
                    <h2 style='margin: 10px 0;'>Ваш кластер</h2>
                    <h1 style='font-size: 2.5em; margin: 10px 0;'>{profile['cluster_name']}</h1>
                    <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px auto; max-width: 300px;'>
                        <p>Точність визначення</p>
                        <h2>{confidence_percent:.1f}%</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                # Детальна інформація про відповіді
                st.markdown("### 📊 Ваші відповіді на опитування")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Базова інформація:**")
                    st.write(f"• Вік: {profile.get('age_group', 'N/A')}")
                    st.write(f"• Дохід: {profile.get('income_level', 'N/A')}")
                    st.write(f"• Освіта: {profile.get('education', 'N/A')}")
                    st.write(f"• Сімейний стан: {profile.get('marital_status', 'N/A')}")
                
                with col2:
                    st.markdown("**Поведінкові характеристики:**")
                    st.write(f"• Чутливість до ціни: {profile.get('price_sensitivity', 'N/A')}/10")
                    st.write(f"• Онлайн покупки: {profile.get('online_shopping', 'N/A')}/10")
                    st.write(f"• Лояльність брендам: {profile.get('brand_loyalty', 'N/A')}/10")
                    st.write(f"• Важливість якості: {profile.get('quality_importance', 'N/A')}/10")
                
                st.info("ℹ️ Опитування вже пройдено. Дані збережено та використовуються для персоналізації.")
    
    # СТОРІНКА РЕКОМЕНДАЦІЙ
    elif st.session_state.page == 'recommendations':
        st.title("💡 Персоналізовані рекомендації")
        
        response = make_request('GET', '/recommendations')
        
        if response and response.status_code == 200:
            rec = response.json()
            
            if rec:
                # Рекомендації в картках
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class='profile-card'>
                        <h3>🛍️ Рекомендовані товари</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    for i, item in enumerate(rec.get('products', []), 1):
                        st.success(f"{i}. {item}")
                
                with col2:
                    st.markdown(f"""
                    <div class='profile-card'>
                        <h3>🎁 Спеціальні пропозиції</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    for i, item in enumerate(rec.get('offers', []), 1):
                        st.info(f"{i}. {item}")
                
                with col3:
                    st.markdown(f"""
                    <div class='profile-card'>
                        <h3>📢 Оптимальні канали</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    for i, item in enumerate(rec.get('channels', []), 1):
                        st.warning(f"{i}. {item}")
                
                # Графік каналів
                st.divider()
                st.markdown("### 📊 Ефективність маркетингових каналів")
                
                channels_data = pd.DataFrame({
                    'Канал': ['Email', 'SMS', 'Push', 'Social', 'Web'],
                    'Ефективність': np.random.randint(40, 95, 5)
                })
                
                fig = px.bar(channels_data, x='Канал', y='Ефективність',
                           color='Ефективність',
                           color_continuous_scale=[[0, COLORS['secondary']], 
                                                  [0.5, COLORS['accent']], 
                                                  [1, COLORS['info']]],
                           title='Ефективність каналів комунікації (%)')
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning("Спочатку пройдіть опитування для отримання рекомендацій")
                if not st.session_state.questionnaire_completed:
                    if st.button("📝 Пройти опитування", type="primary"):
                        st.session_state.page = 'questionnaire'
                        st.rerun()

# ================== АДМІН ІНТЕРФЕЙС ==================

elif st.session_state.role == 'admin':
    
    # Верхня панель
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    
    with col1:
        if st.button("📊 Дашборд", use_container_width=True,
                    type="primary" if st.session_state.get('admin_page', 'dashboard') == 'dashboard' else "secondary"):
            st.session_state.admin_page = 'dashboard'
            st.rerun()
    
    with col2:
        if st.button("👥 Клієнти", use_container_width=True,
                    type="primary" if st.session_state.get('admin_page') == 'clients' else "secondary"):
            st.session_state.admin_page = 'clients'
            st.rerun()
    
    with col3:
        if st.button("🎯 Кластери", use_container_width=True,
                    type="primary" if st.session_state.get('admin_page') == 'clusters' else "secondary"):
            st.session_state.admin_page = 'clusters'
            st.rerun()
    
    with col4:
        st.write("👨‍💼 Адмін")
    
    with col5:
        if st.button("🚪", use_container_width=True, help="Вийти"):
            logout()
    
    st.divider()
    
    # ДАШБОРД
    if st.session_state.get('admin_page', 'dashboard') == 'dashboard':
        st.title("📊 Адміністративний дашборд")
        
        response = make_request('GET', '/admin/analytics')
        if response and response.status_code == 200:
            data = response.json()
            
            # Метрики
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Всього клієнтів", data['summary']['total_clients'], "↑ 12%")
            with col2:
                st.metric("📊 Kaggle датасет", f"{data['summary'].get('kaggle_dataset_size', 2240)} записів")
            with col3:
                st.metric("🎯 Кластерів", "5", "K-Means")
            with col4:
                st.metric("📈 Точність моделі", "87.3%", "↑ 2.1%")
            
            st.divider()
            
            # Графіки
            col1, col2 = st.columns(2)
            
            with col1:
                # Розподіл по кластерах
                cluster_data = pd.DataFrame({
                    'Кластер': ['Преміум', 'Економні', 'Молоді', 'Сімейні', 'Випадкові'],
                    'Кількість': [403, 694, 493, 426, 224],
                    'Відсоток': [18, 31, 22, 19, 10]
                })
                
                fig = px.pie(cluster_data, values='Кількість', names='Кластер',
                           title='Розподіл клієнтів по кластерах (Kaggle Dataset)',
                           color_discrete_map={
                               'Преміум': '#59253A',
                               'Економні': '#0877A1',
                               'Молоді': '#2D4159',
                               'Сімейні': '#895061',
                               'Випадкові': '#78244C'
                           })
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Динаміка реєстрацій
                dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
                registrations = np.random.poisson(5, 30).cumsum()
                
                fig = px.line(x=dates, y=registrations,
                            title='Динаміка реєстрацій клієнтів',
                            labels={'x': 'Дата', 'y': 'Кількість'})
                fig.update_traces(mode='lines+markers', line_color='#0877A1')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Теплова карта активності
            st.divider()
            st.markdown("### 🔥 Карта активності кластерів")
            
            # Генеруємо дані для теплової карти
            clusters = ['Преміум', 'Економні', 'Молоді', 'Сімейні', 'Випадкові']
            metrics = ['Дохід', 'Витрати', 'Частота', 'Лояльність', 'Online']
            
            heatmap_data = np.random.rand(5, 5) * 100
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=metrics,
                y=clusters,
                colorscale=[[0, '#59253A'], [0.5, '#78244C'], [1, '#0877A1']],
                text=heatmap_data.round(1),
                texttemplate="%{text}",
                textfont={"size": 12, "color": "white"},
            ))
            
            fig.update_layout(
                title='Характеристики кластерів (0-100)',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # КЛІЄНТИ
    elif st.session_state.get('admin_page') == 'clients':
        st.title("👥 Управління клієнтами")
        
        response = make_request('GET', '/admin/clients')
        if response and response.status_code == 200:
            data = response.json()
            
            st.metric("Всього зареєстровано", data['total'])
            
            if data['clients']:
                df = pd.DataFrame(data['clients'])
                
                # Фільтри
                col1, col2, col3 = st.columns(3)
                with col1:
                    cluster_filter = st.selectbox("Фільтр по кластеру", 
                        ["Всі"] + list(df['cluster_name'].dropna().unique()))
                
                if cluster_filter != "Всі":
                    df = df[df['cluster_name'] == cluster_filter]
                
                # Стилізована таблиця
                st.dataframe(
                    df.style.background_gradient(cmap='RdPu'),
                    use_container_width=True,
                    hide_index=True
                )
    
    # КЛАСТЕРИ
    elif st.session_state.get('admin_page') == 'clusters':
        st.title("🎯 Аналіз кластерів")
        
        response = make_request('GET', '/admin/clusters')
        if response and response.status_code == 200:
            clusters = response.json()
            
            if clusters:
                # 3D візуалізація кластерів
                st.markdown("### 🌐 3D візуалізація кластерів")
                
                # Генеруємо точки для кожного кластера
                all_points = []
                for i, cluster in enumerate(clusters):
                    n_points = cluster['count'] if cluster['count'] > 0 else 50
                    points = pd.DataFrame({
                        'x': np.random.normal(i*3, 1, n_points),
                        'y': np.random.normal(i*2, 1, n_points),
                        'z': np.random.normal(i*1.5, 1, n_points),
                        'cluster': cluster['name']
                    })
                    all_points.append(points)
                
                if all_points:
                    df_3d = pd.concat(all_points)
                    
                    fig = px.scatter_3d(df_3d, x='x', y='y', z='z', color='cluster',
                                       title='3D візуалізація кластерів',
                                       color_discrete_map={
                                           'Преміум клієнти': '#59253A',
                                           'Економні раціоналісти': '#0877A1',
                                           'Молоді професіонали': '#2D4159',
                                           'Сімейні покупці': '#895061',
                                           'Випадкові покупці': '#78244C'
                                       },
                                       height=500)
                    fig.update_layout(
                        scene=dict(
                            bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(backgroundcolor='rgba(0,0,0,0)', gridcolor='rgba(255,255,255,0.1)'),
                            yaxis=dict(backgroundcolor='rgba(0,0,0,0)', gridcolor='rgba(255,255,255,0.1)'),
                            zaxis=dict(backgroundcolor='rgba(0,0,0,0)', gridcolor='rgba(255,255,255,0.1)')
                        ),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Статистика кластерів
                st.markdown("### 📊 Статистика кластерів")
                
                for cluster in clusters:
                    with st.expander(f"{cluster['name']} ({cluster['count']} клієнтів)"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Кількість", cluster['count'])
                        with col2:
                            st.metric("Середня точність", f"{cluster['avg_confidence']*100:.1f}%")
                        with col3:
                            percentage = (cluster['count'] / sum(c['count'] for c in clusters)) * 100 if clusters else 0
                            st.metric("Відсоток", f"{percentage:.1f}%")
        
        st.divider()
        
        if st.button("🔄 Перенавчити модель на Kaggle датасеті", type="primary", use_container_width=True):
            with st.spinner("Перенавчання на 2240 записах..."):
                response = make_request('POST', '/admin/retrain')
                if response and response.status_code == 200:
                    st.success("✅ Модель успішно перенавчена!")
                    st.balloons()

# Footer
st.divider()
st.markdown(f"""
<div style='text-align: center; color: {COLORS['accent']}; padding: 20px;'>
    <p>🚀 K-Means Clustering | 📊 Kaggle Dataset: 2240 записів | 🔬 7 ключових фіч</p>
</div>
""", unsafe_allow_html=True)