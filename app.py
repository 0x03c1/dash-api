import streamlit as st
import pandas as pd
import plotly.express as px

from src.api_client import fetch_earthquake

st.set_page_config(
    page_title="Terremotos",
    layout="wide",
)


def carregar_dados(dias: int, magnitude: float) -> pd.DataFrame:
   pass


st.sidebar.title("Filtros dos Terremotos")

st.sidebar.markdown("Selecione o número de dias para buscar os terremotos e a magnitude mínima.")

st.bottom = st.sidebar.slider("Dias para trás", min_value=1, max_value=30, value=7)

