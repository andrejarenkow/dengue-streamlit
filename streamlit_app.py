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

# Qual index
index_selecionado = st.selectbox('Selecione qual variável quer na linha', ['Nome Município', 'CRS'])

# Create a pivot table
pivot_table = pd.pivot_table(dados_dengue_ano, values='Confirmados', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)

# Print the pivot table
pivot_table

#teste 1
dados_dengue_final = dados_dengue.set_index("Cód IBGE")

#testa mapa
map_fig = px.choropleth_mapbox(dados_dengue, geojson=dados_andre.geometry,
                          locations=dados_dengue_final.index, color='Confirmados',
                          color_continuous_scale = px.colors.diverging.hot,
                          center ={'lat':-30.452349861219243, 'lon':-53.55320517512141},
                          zoom=5.5,
                          mapbox_style="carto-darkmatter",
                          hover_name='NM_MUN',
                          width=800,
                          height=700,
                          template='plotly_dark',
                          title = f'Casos confirmados: {ano}')
