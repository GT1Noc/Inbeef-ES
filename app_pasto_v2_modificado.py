import base64
import streamlit as st
from pathlib import Path

# Renomear imports para V2
from calculations_pasto_v2 import (
    calcular_custo_diario,
    calcular_diferenca_investimento,
    calcular_investimento_total,
    calcular_ponto_equilibrio,
    calcular_ganho_liquido_por_animal,
    calcular_custo_total_padrao,
    calcular_retorno_inbeef
)
from pdf_generator_pasto_v2 import render_pdf
from config_pasto_v2 import CSS_PATH, LOGO_PATH

# Função auxiliar para formatar valores monetários no padrão brasileiro
def formatar_reais(valor, casas_decimais=2):
    try:
        valor_float = float(valor)
        if casas_decimais == 0:
            resultado = f"US$ {valor_float:,.0f}"
        else:
            resultado = f"US$ {valor_float:,.{casas_decimais}f}"
        return resultado.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "US$ 0,00"

# ----------------------------
# Injeção de CSS e logo
if CSS_PATH.exists():
    css = CSS_PATH.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

if LOGO_PATH.exists():
    logo = LOGO_PATH.read_bytes()
    b64 = base64.b64encode(logo).decode()
    st.markdown(
        "<div style='text-align:center; margin-bottom:10px;'>"
        f"<img src='data:image/png;base64,{b64}' width='200' />"
        "</div>",
        unsafe_allow_html=True
    )

# Cabeçalho em duas linhas, sem hífen, centrado
st.markdown(
    "<div style='text-align:center;'>"
    "<h1 style='margin:0;'>Simulador Comparativo Inbra</h1>"
    "<h2 style='margin:0;'>Inbeef</h2>"
    "</div>",
    unsafe_allow_html=True
)
# ----------------------------

with st.form("sim_form_pasto_v2"):
    # Entradas com tooltips
    dias = st.number_input(
        label="Período – Número de días (días)",
        min_value=1,
        value=30,
        help="Indique la duración del tratamiento, en número entero de días."
    )
    valor_kg_recria = st.number_input(
        label="Valor del kg de peso vivo",
        format="%.2f",
        min_value=0.01,
        help="Indique el valor del kilogramo de peso vivo utilizado para recría."
    )
    num_animais = st.number_input(
        label="Número total de animales",
        min_value=1,
        step=1,
        help="Número total de animales en el lote."
    )

    st.markdown("---")
    # Preço e consumo do produto padrão
    col1, col2 = st.columns(2)
    with col1:
        preco_padrao = st.number_input(
            label="Preço do produto padrão (US$/kg)",
            format="%.2f",
            min_value=0.01,
            help="Precio del suplemento estándar por kilogramo."
        )
    with col2:
        consumo_padrao_g = st.number_input(
            label="Consumo del producto estándar (g/día)",
            format="%.2f",
            min_value=0.0,
            help="Consumo diario en gramos del suplemento estándar."
        )

    # Preço e consumo do produto com Inbeef
    col3, col4 = st.columns(2)
    with col3:
        preco_inbeef = st.number_input(
            label="Preço do produto com Inbeef (US$/kg)",
            format="%.2f",
            min_value=0.01,
            help="Precio del suplemento con Inbeef por kilogramo."
        )
    with col4:
        consumo_inbeef_g = st.number_input(
            label="Consumo del producto con Inbeef (g/día)",
            format="%.2f",
            min_value=0.0,
            help="Consumo diario en gramos del suplemento con Inbeef."
        )

    # GMD padrão e Expectativa GMD adicional
    col5, col6 = st.columns(2)
    with col5:
        gmd_padrao = st.number_input(
            label="GMD Estándar (g/día)",
            format="%.2f",
            min_value=0.0,
            help="Ganancia media diaria de peso estándar."
        )
    with col6:
        expectativa_gmd = st.number_input(
            label="Expectativa de GMD adicional (g/día)",
            format="%.2f",
            min_value=0.0,
            help="Ganancia media diaria adicional esperada."
        )

    submitted = st.form_submit_button("Calcular")

if submitted:
    # Cálculo dos parâmetros básicos
    custo_padrao_diario = calcular_custo_diario(consumo_padrao_g, preco_padrao)
    custo_inbeef_diario = calcular_custo_diario(consumo_inbeef_g, preco_inbeef)
    diferenca_investimento = calcular_diferenca_investimento(
        custo_inbeef_diario, custo_padrao_diario
    )
    ponto_equilibrio = calcular_ponto_equilibrio(
        diferenca_investimento, valor_kg_recria
    )
    ganho_liq_por_animal = calcular_ganho_liquido_por_animal(
        expectativa_gmd, ponto_equilibrio, valor_kg_recria, dias
    )
    custo_total_padrao = calcular_custo_total_padrao(
        num_animais, custo_padrao_diario, dias
    )
    custo_total_inbeef = calcular_investimento_total(
        num_animais, custo_inbeef_diario, dias
    )
    # Cálculo de arrobas produzidas
    qtde_arrobas_padrao = ((gmd_padrao / 1000) * dias) / 30
    valor_arrobas_padrao = qtde_arrobas_padrao * (valor_kg_recria * 30) * num_animais
    qtde_arrobas_inbeef = (((gmd_padrao + expectativa_gmd) / 1000) * dias) / 30
    valor_arrobas_inbeef = qtde_arrobas_inbeef * (valor_kg_recria * 30) * num_animais
    # Retorno sobre investimento
    retorno_inbeef = calcular_retorno_inbeef(
        expectativa_gmd, valor_kg_recria, diferenca_investimento, dias
    )

    # Monta dicionário de resultados
    r = {
        'dias': dias,
        'valor_kg_recria': valor_kg_recria,
        'num_animais': num_animais,
        'preco_padrao': preco_padrao,
        'consumo_padrao_g': consumo_padrao_g,
        'preco_inbeef': preco_inbeef,
        'consumo_inbeef_g': consumo_inbeef_g,
        'gmd_padrao': gmd_padrao,
        'expectativa_gmd': expectativa_gmd,
        'custo_padrao_diario': custo_padrao_diario,
        'custo_inbeef_diario': custo_inbeef_diario,
        'diferenca_investimento': diferenca_investimento,
        'ponto_equilibrio': ponto_equilibrio,
        'ganho_liq_por_animal': ganho_liq_por_animal,
        'custo_total_padrao': custo_total_padrao,
        'custo_total_inbeef': custo_total_inbeef,
        'qtde_arrobas_padrao': qtde_arrobas_padrao,
        'valor_arrobas_padrao': valor_arrobas_padrao,
        'qtde_arrobas_inbeef': qtde_arrobas_inbeef,
        'valor_arrobas_inbeef': valor_arrobas_inbeef,
        'retorno_inbeef': retorno_inbeef
    }

    # Apresenta resultados
    st.subheader("Resultados de la Simulación")
    col_out1, col_out2 = st.columns(2)
    with col_out1:
        st.metric("Costo diario estándar (US$)", formatar_reais(custo_padrao_diario))
        st.metric("Costo total de la suplementación estándar (US$)", formatar_reais(custo_total_padrao))
        st.metric("Diferencia de inversión por animal/día (US$)", formatar_reais(diferenca_investimento))
        st.metric("Ganancia neta por animal (US$)", formatar_reais(ganho_liq_por_animal))
    with col_out2:
        st.metric("Costo diario con Inbeef (US$)", formatar_reais(custo_inbeef_diario))
        st.metric("Costo total de la suplementación con Inbeef (US$)", formatar_reais(custo_total_inbeef))
        st.metric("Punto de equilibrio (g/día)", f"{ponto_equilibrio:.2f}")
        st.metric("Retorno sobre la Inversión", f"{retorno_inbeef:.2f}")

    # Gera e oferece download do PDF
    pdf = render_pdf(r)
    st.download_button(
        "⬇️ Descargar Informe (PDF)",
        data=pdf,
        file_name=f"sim_inbra_pasto_{dias}d.pdf",
        mime="application/pdf"
    )
