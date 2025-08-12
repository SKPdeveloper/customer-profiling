import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

# Подключение к базе данных
conn = sqlite3.connect('profiling.db')
cursor = conn.cursor()

# Очистка существующих данных (кроме админа)
cursor.execute("DELETE FROM users WHERE role = 'client'")
cursor.execute("DELETE FROM client_profiles")

# Список имен для генерации
first_names = ["Іван", "Олексій", "Марія", "Анна", "Петро", "Наталія", "Андрій", "Ольга", "Віктор", "Юлія"]
last_names = ["Коваленко", "Петренко", "Іваненко", "Сидоренко", "Павленко", "Шевченко", "Бондаренко", "Ткаченко", "Мельник", "Кравченко"]

# Параметры для каждого кластера
cluster_profiles = {
    0: {  # Преміум клієнти
        'income_level': 'very_high',
        'age_group': random.choice(['35-44', '45-54']),
        'education': random.choice(['Вища', 'Кілька вищих']),
        'marital_status': random.choice(['Одружений', 'Розлучений']),
        'has_children': random.choice([True, False]),
        'price_sensitivity': random.randint(1, 3),
        'online_shopping': random.randint(7, 10),
        'brand_loyalty': random.randint(8, 10),
        'innovation': random.randint(6, 9),
        'social_influence': random.randint(5, 8),
        'quality_importance': random.randint(9, 10)
    },
    1: {  # Економні раціоналісти
        'income_level': 'medium',
        'age_group': random.choice(['45-54', '55+']),
        'education': random.choice(['Середня', 'Вища']),
        'marital_status': random.choice(['Одружений', 'Розлучений']),
        'has_children': True,
        'price_sensitivity': random.randint(8, 10),
        'online_shopping': random.randint(4, 7),
        'brand_loyalty': random.randint(4, 6),
        'innovation': random.randint(3, 5),
        'social_influence': random.randint(5, 7),
        'quality_importance': random.randint(6, 8)
    },
    2: {  # Молоді професіонали
        'income_level': random.choice(['high', 'medium']),
        'age_group': random.choice(['25-34', '35-44']),
        'education': random.choice(['Вища', 'Кілька вищих']),
        'marital_status': random.choice(['Неодружений', 'Одружений']),
        'has_children': random.choice([True, False]),
        'price_sensitivity': random.randint(4, 6),
        'online_shopping': random.randint(8, 10),
        'brand_loyalty': random.randint(5, 7),
        'innovation': random.randint(7, 9),
        'social_influence': random.randint(7, 9),
        'quality_importance': random.randint(7, 9)
    },
    3: {  # Сімейні покупці
        'income_level': 'medium',
        'age_group': random.choice(['35-44', '45-54']),
        'education': random.choice(['Вища', 'Середня']),
        'marital_status': 'Одружений',
        'has_children': True,
        'price_sensitivity': random.randint(5, 7),
        'online_shopping': random.randint(5, 8),
        'brand_loyalty': random.randint(6, 8),
        'innovation': random.randint(4, 6),
        'social_influence': random.randint(6, 8),
        'quality_importance': random.randint(7, 9)
    },
    4: {  # Випадкові покупці
        'income_level': random.choice(['low', 'medium']),
        'age_group': random.choice(['18-24', '25-34', '35-44']),
        'education': random.choice(['Середня', 'Вища']),
        'marital_status': random.choice(['Неодружений', 'Розлучений']),
        'has_children': random.choice([True, False]),
        'price_sensitivity': random.randint(6, 9),
        'online_shopping': random.randint(2, 5),
        'brand_loyalty': random.randint(2, 5),
        'innovation': random.randint(3, 6),
        'social_influence': random.randint(4, 7),
        'quality_importance': random.randint(5, 7)
    }
}

# Список назв кластерів для використання в запросі
cluster_names = [
    'Преміум клієнти',
    'Економні раціоналісти',
    'Молоді професіонали',
    'Сімейні покупці',
    'Випадкові покупці'
]

# Генерация 30 клиентов
for i in range(1, 31):
    # Выбираем кластер (равномерно распределяем)
    cluster_id = (i-1) % 5
    profile = cluster_profiles[cluster_id]
    
    # Генерируем данные пользователя
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = f"client{i}@example.com"
    password_hash = hashlib.sha256(f"password{i}".encode()).hexdigest()
    created_at = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d %H:%M:%S')
    
    # Вставляем пользователя
    cursor.execute('''
        INSERT INTO users (email, password_hash, name, role, created_at)
        VALUES (?, ?, ?, 'client', ?)
    ''', (email, password_hash, name, created_at))
    
    user_id = cursor.lastrowid
    
    # Вставляем профиль
    cursor.execute('''
        INSERT INTO client_profiles (
            user_id, age_group, income_level, education, marital_status,
            has_children, price_sensitivity, online_shopping, brand_loyalty,
            innovation, social_influence, quality_importance, cluster_id,
            cluster_name, cluster_confidence, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        profile['age_group'],
        profile['income_level'],
        profile['education'],
        profile['marital_status'],
        int(profile['has_children']),
        profile['price_sensitivity'],
        profile['online_shopping'],
        profile['brand_loyalty'],
        profile['innovation'],
        profile['social_influence'],
        profile['quality_importance'],
        cluster_id,
        cluster_names[cluster_id],
        round(random.uniform(0.75, 0.95), 2),  # Высокая точность для тестовых данных
        created_at
    ))
    
    print(f"Додано клієнта {name} ({email}) до кластера {cluster_id} ({cluster_names[cluster_id]})")

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("\n✅ Базу даних успішно заповнено 30 тестовими клієнтами!")
print("Розподіл по кластерам:")
for i, name in enumerate(cluster_names):
    print(f"{i} - {name}: 6 клієнтів")