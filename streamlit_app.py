# Importação de bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px

# Carrega dados de casos de dengue de um arquivo CSV
arquivo = 'https://ti.saude.rs.gov.br/ws/dengue_resid_csv.csv'
dados_dengue = pd.read_csv(arquivo, sep=',', encoding='latin1')

# Criar um input widget (filtro)
ano = st.selectbox('Selecione o ano', dados_dengue['Ano'].unique())

# Filtrar o dataframe
dados_dengue_ano = dados_dengue.loc[dados_dengue['Ano']==ano]

# Create a pivot table
pivot_table = pd.pivot_table(dados_dengue_ano, values='Confirmados', index='Nome Munic\u00edpio', columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)

# Print the pivot table
pivot_table
