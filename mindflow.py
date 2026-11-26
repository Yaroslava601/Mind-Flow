from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import datetime
import sqlite3
import pandas as pd
import random
from sklearn.ensemble import RandomForestRegressor
import os
from gigachat import GigaChat

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
    html, body, p, div, label {
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

# ID участника
if "participant_id" not in st.session_state:
    st.session_state["participant_id"] = ""

raw_pid = st.sidebar.text_input(
    "Ваш код / ID участника",
    value=st.session_state["participant_id"],
    max_chars=30,
    placeholder="Например, уч_1",
    help=(
        "Придумайте короткий код (например, уч_Я). Не вводите ФИО, пароли и "
        "личные контакты."
    ),
)
participant_id = raw_pid.strip()
st.session_state["participant_id"] = participant_id

st.sidebar.caption(
    "Не указывайте фамилии, пароли и личные данные — заметки могут"
    " анализироваться ИИ."
)

#создаем таблицу и файл базы
def init_db():
    conn = sqlite3.connect('mindflow_test.db')
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT DEFAULT 'участник_1',
        date TEXT,
        sleep REAL,
        mood INTEGER,
        energy INTEGER,
        note TEXT
        )
    """)
    cur.execute("PRAGMA table_info(checkins)")
    existing_cols = {row[1] for row in cur.fetchall()}
    if "participant_id" not in existing_cols:
        cur.execute(
            "ALTER TABLE checkins ADD COLUMN participant_id TEXT DEFAULT" 'участник_1'
        )
    conn.commit()
    conn.close()

init_db()

# 3. Шапка сайта
st.title("🌸 MindFlow")
if participant_id:
    st.markdown(f"### 👤 Привет, {participant_id}!")
else:
    st.info("Сначала введите свой ID участника в боковой панели слева.")

# 4. Три крупные кнопки-вкладки
tab_journal, tab_forecast, tab_charts = st.tabs(
    ["📖 Дневник", "🔮 Прогноз", "📊 Графики"]
)

# Функция предсказания энергии
def predict_next_energy(df, next_sleep: float, next_mood: int):
  if df is None or len(df) < 5:
    return None

  clean_df = df.dropna(subset=["sleep", "mood", "energy"])
  if len(clean_df) < 5:
    return None

  X = clean_df[["sleep", "mood"]]
  y = clean_df["energy"]

  model = RandomForestRegressor(n_estimators=100, random_state=42)
  model.fit(X, y)

  pred = model.predict([[next_sleep, next_mood]])[0]
  return round(float(max(1.0, min(5.0, pred))), 1)

# Совет от ИИ
def _local_fallback_advise(note_text: str, pred_energy=None):
    text = (note_text or "").lower().strip()

    stress_markers = [
        "устал", "устала", "стресс", "не успел", "не успела",
        "контрольн", "сложн", "сон", "клонит в сон", "выгоран",
        "тревог", "перегруз", "тяжел", "мало спал", "мало спала",
    ]
    positive_markers = [
        "хорош", "отличн", "продуктив", "выспал", "отдохн",
        "спокойн", "успел", "успела", "легк", "рад", "рада", "бодр",
    ]

    stress_hits = sum(1 for word in stress_markers if word in text)
    pos_hits = sum(1 for word in positive_markers if word in text)

    if not text:
        tone_label = "Заметка не заполнена"
        stress_level = "Не оценён"
    elif stress_hits > pos_hits:
        tone_label = "Есть признаки усталости или напряжения"
        stress_level = "Повышенный"
    elif pos_hits > stress_hits:
        tone_label = "Преобладает позитивный настрой"
        stress_level = "Низкий"
    else:
        tone_label = "Нейтральный или смешанный фон"
        stress_level = "Умеренный"

    if pred_energy is not None and pred_energy < 2.8:
        advice = (
            "Завтра ожидается пониженный уровень энергии. Оставь на вечер только "
            "самое важное, убери лишние задачи и постарайся лечь пораньше."
        )
    elif stress_level == "Повышенный":
        advice = (
            "В заметке чувствуется напряжение. Сделай короткую паузу, переключи "
            "внимание и не накручивай себя — завтра начнёшь со свежей головой."
        )
    elif pred_energy is not None and pred_energy >= 3.8 and stress_level != "Повышенный":
        advice = (
            "Ресурсов хватает: хороший момент, чтобы закрыть сложную задачу или "
            "спокойно продвинуться по плану, но без перебора по времени."
        )
    else:
        advice = (
            "Ровный режим: держи баланс между делами и отдыхом и не забывай про "
            "полноценный сон."
        )

    return tone_label, stress_level, advice, "Локальный режим"


def analyze_note_and_advise(note_text: str, pred_energy=None):
    cleaned_note = (note_text or "").strip()
    auth_key = os.getenv("GIGACHAT_AUTH_KEY", "").strip()

    if not cleaned_note or not auth_key:
        return _local_fallback_advise(cleaned_note, pred_energy)

    pred_info = (
        f"Прогноз энергии на завтра: {pred_energy} из 5."
        if pred_energy is not None
        else "Прогноз энергии пока не рассчитан."
    )

    prompt = (
        "Проанализируй дневниковую заметку пользователя за день.\n"
        f"{pred_info}\n"
        f"Заметка: \"{cleaned_note}\"\n\n"
        "Ответь строго в таком формате (3 короткие строки, без лишнего текста):\n"
        "ТОНАЛЬНОСТЬ: <кратко, 2-4 слова>\n"
        "НАПРЯЖЕНИЕ: <Низкий / Умеренный / Повышенный>\n"
        "СОВЕТ: <один практичный и бережный совет на 1-2 предложения на русском>"
    )

    try:
        with GigaChat(
            credentials=auth_key,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
        ) as giga:
            models_resp = giga.get_models()
            model_ids = [
                m.id_ for m in models_resp.data if getattr(m, "id_", None)
            ]
            chosen_model = next(
                (m for m in model_ids if "GigaChat" in m),
                model_ids[0] if model_ids else "GigaChat-2",
            )

            response = giga.chat({"model": chosen_model, "messages": [{"role": "user", "content": prompt}]})
            raw_answer = response.choices[0].message.content.strip()

        tone_label = ""
        stress_level = ""
        advice = ""

        for line in raw_answer.splitlines():
            line_clean = line.strip()
            upper = line_clean.upper()
            if upper.startswith("ТОНАЛЬНОСТЬ:"):
                tone_label = line_clean.split(":", 1)[1].strip()
            elif upper.startswith("НАПРЯЖЕНИЕ:"):
                stress_level = line_clean.split(":", 1)[1].strip()
            elif upper.startswith("СОВЕТ:"):
                advice = line_clean.split(":", 1)[1].strip()

        if tone_label and stress_level and advice:
            return tone_label, stress_level, advice, "GigaChat API"

        return _local_fallback_advise(cleaned_note, pred_energy)

    except Exception as e:
        st.caption(f"Fallback причина: {e}")
        return _local_fallback_advise(cleaned_note, pred_energy)



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
    note = st.text_area("Как прошел твой день? (Заметки / стресс)\n " \
    "ВНИМАНИЕ! Не указывай в заметке пароли, фамилии и личные данные других людей.")

    # 4) Большая розовая кнопка «ОТМЕТИТЬ ДЕНЬ»
    st.markdown('<div class="main-submit">', unsafe_allow_html=True)
    if st.button("ОТМЕТИТЬ ДЕНЬ", type="primary", key="submit_day"):
        
        pid = st.session_state["participant_id"]

        
        conn = sqlite3.connect('mindflow_test.db')
        cur = conn.cursor()
        today_str = datetime.date.today().isoformat()
        cur.execute(
            "INSERT INTO checkins (participant_id, date, sleep, mood, energy, note) VALUES (?,?,?,?,?,?)", (pid, today_str, sleep_hours, mood, st.session_state.energy, note),
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

  conn = sqlite3.connect("mindflow_test.db")
  df_forecast = pd.read_sql_query(
      "SELECT * FROM checkins ORDER BY id ASC", conn
  )
  conn.close()
  pid = st.session_state["participant_id"]
  if not df_forecast.empty and "participant_id" in df_forecast.columns:
     df_forecast = df_forecast[df_forecast["participant_id"] == pid].copy()

  if len(df_forecast) < 5:
    st.info(
        "Нужно хотя бы 5 записей в базе (или заполни 30 тестовых дней во"
        " вкладке «Графики»), чтобы обучить модель Случайного леса."
    )
  else:
    avg_sleep = round(float(df_forecast["sleep"].tail(7).mean()), 1)
    avg_mood = int(round(float(df_forecast["mood"].tail(7).mean())))

    pred_energy = predict_next_energy(df_forecast, avg_sleep, avg_mood)
    st.metric(
        label="Прогноз уровня энергии на завтра (Random Forest)",
        value=f"{pred_energy} / 5",
        delta=f"При ориентире ~{avg_sleep} ч сна и настроении {avg_mood}/5",
    )

    if pred_energy < 2.8:
      st.warning(
          "Внимание: модель прогнозирует сниженный уровень энергии. Лучше не"
          " планировать перегрузку и пораньше лечь спать."
      )
    else:
      st.success(
          "Прогноз благоприятный: уровень энергии должен быть стабильным."
      )

    last_note = ""
    if "note" in df_forecast.columns and not df_forecast["note"].empty:
      last_note = str(df_forecast["note"].iloc[-1] or "").strip()

    tone_label, stress_level, advice_text, mode_used = analyze_note_and_advise(
        last_note, pred_energy
    )

    st.divider()
    st.subheader("Анализ заметки и персональный совет")

    if last_note:
      st.markdown(f"**Последняя заметка:** «{last_note}»")
    else:
      st.markdown("**Последняя заметка:** *пока не заполнена*")

    st.markdown(f"**Тональность:** {tone_label}")
    st.markdown(f"**Уровень напряжения по тексту:** {stress_level}")
    st.info(f"**Совет на завтра:** {advice_text}")
    st.caption(f"Источник ответа: {mode_used}")

# Вкладка 3: ГРАФИКИ
with tab_charts:
  conn = sqlite3.connect("mindflow_test.db")
  df_charts = pd.read_sql_query(
      "SELECT * FROM checkins ORDER BY id DESC", conn
  )
  conn.close()

  pid = st.session_state["participant_id"]
  if not df_charts.empty and "participant_id" in df_charts.columns:
       df_charts = df_charts[df_charts["participant_id"] == pid].copy()

  st.subheader("Графики и динамика показателей")

  if df_charts.empty:
    st.info(
        "Пока записей нет — заполни форму во вкладке «Дневник»"
    )
  else:
    df_sorted = df_charts.sort_values("id", ascending=True).copy()

    metric_map = {
        "Энергия": "energy",
        "Сон (ч)": "sleep",
        "Настроение": "mood",
    }
    available_metrics = [
        label for label, col in metric_map.items() if col in df_sorted.columns
    ]

    c_metric, c_window = st.columns(2)
    selected_label = c_metric.selectbox(
        "Показатель на графике", available_metrics
    )
    window_options = ["Все записи", "Последние 7 записей", "Последние 14 записей"]
    selected_window = c_window.selectbox("Период", window_options)

    plot_df = df_sorted.copy()
    if selected_window == "Последние 7 записей":
      plot_df = plot_df.tail(7)
    elif selected_window == "Последние 14 записей":
      plot_df = plot_df.tail(14)

    col_name = metric_map[selected_label]
    x_col = "date" if "date" in plot_df.columns else "id"
    chart_df = plot_df.set_index(x_col)[[col_name]].rename(
        columns={col_name: selected_label}
    )
    st.line_chart(chart_df, width="stretch")

    st.divider()
    st.subheader("Таблица записей")

    display_cols = [
        c
        for c in ["date", "sleep", "mood", "energy", "note"]
        if c in df_charts.columns
    ]
    table_df = df_charts[display_cols].rename(columns={
        "date": "Дата",
        "sleep": "Сон (ч)",
        "mood": "Настроение",
        "energy": "Энергия",
        "note": "Заметка",
    })

    col_cfg = {}
    if "Сон (ч)" in table_df.columns:
      col_cfg["Сон (ч)"] = st.column_config.NumberColumn(format="%.1f ч")
    if "Настроение" in table_df.columns:
      col_cfg["Настроение"] = st.column_config.NumberColumn(format="%d / 5")
    if "Энергия" in table_df.columns:
      col_cfg["Энергия"] = st.column_config.NumberColumn(format="%d / 5")
    if "Заметка" in table_df.columns:
      col_cfg["Заметка"] = st.column_config.TextColumn(width="large")

    st.dataframe(
        table_df,
        hide_index=True,
        width="stretch",
        column_config=col_cfg,
    )

    if len(df_charts) >= 3:
      st.divider()
      st.subheader("Математический анализ связей (коэффициент Пирсона)")

      corr_sleep_energy = df_charts["sleep"].corr(
          df_charts["energy"], method="pearson"
      )
      corr_sleep_mood = df_charts["sleep"].corr(
          df_charts["mood"], method="pearson"
      )
      corr_mood_energy = df_charts["mood"].corr(
          df_charts["energy"], method="pearson"
      )

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
          "Связь между продолжительностью сна и уровнем энергии:"
          f" **{strength} {direction}** ($r = {corr_sleep_energy:.2f}$)."
      )
    else:
      st.caption(
          "Добавь хотя бы 3 записи, чтобы рассчитать коэффициент Пирсона."
      )
