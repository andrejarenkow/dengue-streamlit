# Importação de bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px

# Carrega dados de casos de dengue de um arquivo CSV
arquivo = 'https://ti.saude.rs.gov.br/ws/dengue_resid_csv.csv'
dados_dengue = pd.read_csv(arquivo, sep=',', encoding='latin1')


dados_dengue_2024 = dados_dengue.loc[dados_dengue['Ano']==2024]
dados_dengue_2024
