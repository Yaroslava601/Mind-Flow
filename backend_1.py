import streamlit as st
import datetime
import sqlite3
import pandas as pd
import random

# 1. Настройка страницы
st.set_page_config(page_title="MindFlow", page_icon="🌸", layout="centered")

# 2. Настройка дизайна (Розово-персиковый фон с полупрозрачными цветами, шрифт Arial, кнопки)
st.markdown(
    """
    <style>
    /* Устанавливаем нежный розово-персиковый фон с полупрозрачными цветами */
    .stApp {
        background-color: #ffe8e5 !important;
        background-image:
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cg fill='%23ffffff' fill-opacity='0.2'%3E%3Ccircle cx='60' cy='38' r='14'/%3E%3Ccircle cx='82' cy='52' r='14'/%3E%3Ccircle cx='74' cy='78' r='14'/%3E%3Ccircle cx='46' cy='78' r='14'/%3E%3Ccircle cx='38' cy='52' r='14'/%3E%3Ccircle cx='60' cy='60' r='10' fill='%23ffb6c1' fill-opacity='0.25'/%3E%3C/g%3E%3C/svg%3E"),
            linear-gradient(135deg, #ffe5ec 0%, #ffdfba 100%) !important;
        background-repeat: repeat, no-repeat !important;
        background-attachment: fixed !important;
    }

    /* Делаем верхнюю полоску браузера прозрачной, чтобы не мешала фону */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Устанавливаем шрифт Arial, делаем текст крупнее и жирнее везде */
    html, body, [class*="css"], p, div, span, label {
        font-family: 'Arial', sans-serif !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #4a353b !important; /* Мягкий темно-сливовый цвет текста для читаемости */
    }

    /* Крупные заголовки */
    h1, h1 span {
        font-family: 'Arial', sans-serif !important;
        font-size: 52px !important;
        font-weight: 900 !important;
        color: #d81b60 !important;
        text-align: center !important;
        margin-bottom: 10 px !important;
    }
    h2, h2 span, h3, h3 span {
        font-family: 'Arial', sans-serif !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #5c3c44 !important;
    }

    /* Кнопки-вкладки (Дневник, Прогноз, Графики) */
    button[data-baseweb="tab"] {
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 15px 25px !important;
        margin-right: 10px !important;
        border-radius: 15px !important;
        background-color: rgba(255, 255, 255, 0.75) !important;
        border: 2px solid #ffc1d3 !important;
    }
    button[data-baseweb="tab"] p {
        font-size: 20px !important;
        font-weight: bold !important;
    }

    /* Обычные кнопки (для цифр энергии 1, 2, 3, 4, 5 — когда они НЕ выбраны) */
    div.stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        color: #5c3c44 !important;
        font-size: 22px !important;
        font-weight: bold !important;
        height: 60px !important;
        width: 100% !important;
        border-radius: 15px !important;
        border: 2px solid #ffb6c1 !important;
    }

    /* Выбранная кнопка энергии (ЗАГОРАЕТСЯ РОЗОВЫМ) и главная кнопка "ОТМЕТИТЬ ДЕНЬ" */
    div.stButton > button[kind="primary"] {
        background-color: #ff69b4 !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        height: 60px !important;
        width: 100% !important;
        border-radius: 15px !important;
        border: 2px solid #ff1493 !important;
        box-shadow: 0px 4px 12px rgba(255, 105, 180, 0.5) !important;
    }
    div.stButton > button[kind="primary"] * {
        color: white !important;
    }

    /* Поле ввода текста (Заметки о дне) делаем белым и полупрозрачным */
    textarea {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 15px !important;
        border: 2px solid #ffb6c1 !important;
    }

    /* Делаем самую нижнюю кнопку "ОТМЕТИТЬ ДЕНЬ" еще крупнее и овальной */
    div.main-submit > div.stButton > button {
        height: 65px !important;
        font-size: 24px !important;
        border-radius: 30px !important;
        margin-top: 20px !important;
    }
        /* Делаем белую карточку под центральным блоком с текстом */
    .block-container {
        background-color: rgba(255, 255, 255, 0.92) !important; /* Белый фон (чуть-чуть прозрачный) */
        border-radius: 30px !important;                         /* Закругляем углы карточки */
        padding: 40px !important;                               /* Отступы внутри карточки, чтобы текст не лип к краям */
        margin-top: 30px !important;                            /* Отступ сверху */
        margin-bottom: 30px !important;                         /* Отступ снизу */
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.08) !important; /* Мягкая тень вокруг белой карточки */
        max-width: 720px !important;                            /* Ширина белой карточки */
    }
    </style>
""",
    unsafe_allow_html=True,
)

#создаем таблицу и файл базы
def init_db():
    conn = sqlite3.connect('mindflow.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            sleep REAL,
            mood INTEGER,
            energy INTEGER,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def seed_demo_data(days: int = 30):
    conn = sqlite3.connect("mindflow.db")
    cur = conn.cursor()

    sample_notes = [
        "обычный учебный день, много домашних заданий",
        "спала мало, к вечеру сильно устала и клонило в сон",
        "хорошо выспалась, продуктивно позанималась",
        "контрольная и пара сложных задач , был небольшой стресс",
        "спокойный день, успела отдохнуть и погулять",
        "поздний подъем и нехватка времени на повторение",
    ]

    for offset in range(days, 0, -1):
        day_date = (
            datetime.date.today() - datetime. timedelta(days=offset)
        ).isoformat()
        sleep_val = round (random.uniform(5.0, 9.5), 1)
        #энерния и настроение зависят от сна + немного случайности
        base_energy = (
            4.5 if sleep_val >= 8 else (3.0 if sleep_val >= 6.5 else 2.0)
        )
        energy_val = int(max(1, min (5, round(base_energy + random.uniform(-1, 1)))))
        mood_val = int(
            max(1, min(5, round(energy_val + random.uniform(-0.8, 0.8))))
        )
        note_val = random.choice(sample_notes)

        cur.execute(
            ''' INSERT INTO checkins (date, sleep, mood, energy, note)
            VALUES (?,?,?,?,?) ''',
            (day_date, sleep_val, mood_val, energy_val, note_val),
        )

    conn.commit()
    conn.close()
# 3. Шапка сайта
st.title("🌸 MindFlow")
st.markdown("### 👤 Привет, Ярослава")
st.markdown("## Ноябрь")

# Индикатор дня цикла
st.info("📅 **ДЕНЬ ЦИКЛА: 15**")

# 4. Три крупные кнопки-вкладки
tab_journal, tab_forecast, tab_charts = st.tabs(
    ["📖 Дневник", "🔮 Прогноз", "📊 Графики"]
)

# Вкладка 1: ДНЕВНИК (анкета)
with tab_journal:
    st.subheader("Заполнить данные за сегодня")

    # 1) Ползунок для сна: целые числа
    sleep_hours = st.slider("Сколько часов ты спала?", 0, 12, 7, 1)

    st.write("")  # Небольшой отступ

    mood = st.slider("А как оценишь настроение?", 1, 5, 3, 1)

    st.write("")  # Небольшой отступ

    # 2) Кнопки 1, 2, 3, 4, 5 для уровня энергии, которые загораются при нажатии
    st.write("Уровень энергии:")

    if "energy" not in st.session_state:
        st.session_state.energy = 3

    cols = st.columns(5)
    for i in range(1, 6):
        with cols[i - 1]:
            btn_type = "primary" if st.session_state.energy == i else "secondary"
            if st.button(str(i), key=f"energy_btn_{i}", type=btn_type):
                st.session_state.energy = i
                st.rerun()

    st.write("")  # Небольшой отступ

    # 3) Текстовая заметка о дне
    note = st.text_area("Как прошел твой день? (Заметки / стресс)")

    # 4) Большая розовая кнопка «ОТМЕТИТЬ ДЕНЬ»
    st.markdown('<div class="main-submit">', unsafe_allow_html=True)
    if st.button("ОТМЕТИТЬ ДЕНЬ", type="primary", key="submit_day"):
        conn = sqlite3.connect('mindflow.db')
        cur = conn.cursor()
        today_str = datetime.date.today().isoformat()
        cur.execute(
            "INSERT INTO checkins (date, sleep, mood, energy, note) VALUES (?,?,?,?,?)", (today_str, sleep_hours, mood, st.session_state.energy, note),
            )
        conn.commit()
        conn.close()

        st.success(
            f"✨ День отмечен! Сон: {sleep_hours} ч, Энергия: {st.session_state.energy}/5, Настроение: {mood}/5"
        )
    st.markdown("</div>", unsafe_allow_html=True)


# Вкладка 2: ПРОГНОЗ
with tab_forecast:
    st.subheader("Интеллектуальный прогноз от ИИ")
    st.write(
        "Здесь появится анализ от Gemini API и предупреждение о спаде энергии за 24–48 часов."
    )
    st.warning(
        "⚠️ Внимание: На основе твоих биоритмов завтра возможен спад концентрации на 30%. Рекомендуем перенести сложные задачи!"
    )

# Вкладка 3: ГРАФИКИ
with tab_charts:
    st.subheader("Твоя статистика и биоритмы")
    st.write("Динамика твоего сна и энергии за неделю:")
    chart_data = [5, 6, 7, 4, 8, 6, 7]
    st.line_chart(chart_data)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Заполнить 30 тестовых дней", key="seed_30_days"):
            seed_demo_data(30)
            st.success("Добавлено 30 тестовых записей за прошлый месяц!")
            st.rerun()
    with col_b:
        if st.button("Очистить базу", key="clear_db"):
            conn = sqlite3.connect("mindflow.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM checkins")
            conn.commit()
            conn.close()
            st.warning("База очищена.")
            st.rerun()

    conn = sqlite3.connect("mindflow.db")
    df = pd.read_sql_query("SELECT * FROM checkins ORDER  BY id DESC", conn)
    conn.close()

    if df.empty:
        st.info(
            "Пока записей нет - заполни форму во вкладке «Дневник» и нажми " "«ОТМЕТИТЬ ДЕНЬ»."
        )
    else:
        st.dataframe(df, use_container_width=True)
        if len(df) >= 3:
            st.subheader("Математический анализ связей (коэффициент Пирсона)")

            corr_sleep_energy = df["sleep"].corr(df["energy"], method="pearson")
            corr_sleep_mood = df["sleep"].corr(df["mood"], method="pearson")
            corr_mood_energy = df["mood"].corr(df["energy"], method="pearson")

            m1, m2, m3 = st.columns(3)
            m1.metric("Сон ↔ Энергия", f"{corr_sleep_energy:.2f}")
            m2.metric("Сон ↔ Настроение", f"{corr_sleep_mood:.2f}")
            m3.metric("Настроение ↔ Энергия", f"{corr_mood_energy:.2f}")

            abs_r = abs(corr_sleep_energy)
            if abs_r >= 0.7:
                strength = "сильная"
            elif abs_r >= 0.4:
                strength = "умеренная"
            else:
                strength = "слабая"

            direction = "прямая" if corr_sleep_energy >= 0 else "обратная"
            st.info(
                f"Связь между продолжительностью сна и уровнем энергии: **{strength}"
                f" {direction}** ($r = {corr_sleep_energy:.2f}$)."
            )
        else:
            st.caption(
                "Добавь хотя бы 3 записи (или нажми «Заполнить 30 тестовых дней»),"
                " чтобы рассчитать коэффициент Пирсона."
            )