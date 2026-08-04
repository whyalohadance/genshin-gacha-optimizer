import numpy as np
import streamlit as st
import plotly.graph_objects as go
from simulator import run_monte_carlo, pulls_to_primogems

st.set_page_config(page_title="Genshin Gacha Optimizer", page_icon="🎲", layout="centered")

st.title("🎲 Genshin Gacha Optimizer")
st.caption("Сколько розыгрышей и примогемов реально понадобится на баннерного персонажа")

with st.expander("ℹ️ Как это работает — если не знаком с терминами"):
    st.markdown("""
    - **Pity** — счётчик розыгрышей без 5★ предмета. Чем он выше, тем больше шанс выбить 5★
      (после 74-го розыгрыша шанс резко растёт, на 90-м — 5★ гарантирован)
    - **50/50** — первый 5★ на баннере с вероятностью 50% окажется нужным персонажем,
      иначе — случайным стандартным, но тогда следующий 5★ уже гарантированно баннерный
    - Этот инструмент не "предсказывает" в смысле ML — правила гачи официально известны,
      здесь честно **симулируется 20 000 раз**, чтобы показать реальный разброс исходов
    """)

st.subheader("Твоя ситуация")
col1, col2 = st.columns(2)
with col1:
    current_pity = st.number_input("Текущий pity", 0, 89, 0, help="Сколько розыгрышей уже сделано без 5★")
with col2:
    target_copies = st.number_input("Нужно копий персонажа", 1, 7, 1)

guaranteed = st.checkbox("У меня гарантия на баннерного (проиграл прошлый 50/50)")

if st.button("Посчитать", type="primary", use_container_width=True):
    with st.spinner("Кручу 20 000 симуляций баннера..."):
        results = run_monte_carlo(target_copies, current_pity, guaranteed, n_simulations=20000)

    p50 = int(np.percentile(results, 50))
    p90 = int(np.percentile(results, 90))
    mean = int(results.mean())

    st.subheader("Результат")
    st.markdown(
        f"В **половине** случаев хватит **{p50} розыгрышей** "
        f"(≈ {pulls_to_primogems(p50):,} примогемов).".replace(",", " ")
    )
    st.markdown(
        f"Чтобы быть уверенным на **90%**, копи запас на **{p90} розыгрышей** "
        f"(≈ {pulls_to_primogems(p90):,} примогемов).".replace(",", " ")
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Медиана", p50, help="50% симуляций уложились в это число розыгрышей")
    col2.metric("Среднее", mean)
    col3.metric("90% гарантия", p90, help="90% симуляций уложились в это число розыгрышей")

    st.subheader("Распределение исходов")
    st.caption(
        "Два пика на графике — это две основные ветки удачи: "
        "левый горб — выиграл 50/50 с первой попытки, "
        "правый горб — сначала проиграл, но потом добрал гарантированного персонажа."
    )
    fig = go.Figure(data=[go.Histogram(
        x=results, nbinsx=50,
        marker_color="#7c9eff",
    )])
    fig.update_layout(
        xaxis_title="Количество розыгрышей",
        yaxis_title="Число симуляций",
        showlegend=False,
        margin=dict(t=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("А если у меня есть только N розыгрышей?")
    pull_options = st.slider("Сколько розыгрышей планируешь сделать?", 10, 300, p50)
    success_rate = (results <= pull_options).mean()
    st.markdown(f"Шанс набрать **{target_copies}** копий за **{pull_options}** розыгрышей:")
    st.markdown(f"### {success_rate:.0%}")
