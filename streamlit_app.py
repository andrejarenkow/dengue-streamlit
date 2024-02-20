# Importação de bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px

# Configurações da página
st.set_page_config(
    page_title="Dengue RS",
    page_icon=":rainbow:",
    layout="wide",
    initial_sidebar_state='collapsed'
)

col1, col2, col3 = st.columns([1,4,1])

col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=100)
col2.header('Painel Alternativo Dengue')
col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=150)

#Layout padrão
coluna_filtros, coluna_dados = st.columns([1,4])
with coluna_filtros:
    container_filtros = st.container(border=True)

# Carrega dados de casos de dengue de um arquivo CSV
arquivo = 'https://ti.saude.rs.gov.br/ws/dengue_resid_csv.csv'
dados_dengue = pd.read_csv(arquivo, sep=',', encoding='latin1')

# Criar um input widget (filtro)
with container_filtros:
    ano = st.selectbox('Selecione o ano', sorted(dados_dengue['Ano'].unique()), index=9)

# Filtrar o dataframe
dados_dengue_ano = dados_dengue.loc[dados_dengue['Ano']==ano]

# Qual index
with container_filtros:
    index_selecionado = st.selectbox('Selecione qual variável quer na linha', ['Nome Município', 'CRS'])

# Create a pivot table
pivot_table = pd.pivot_table(dados_dengue_ano, values='Confirmados', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)

# Print the pivot table
with coluna_dados:
    pivot_table

#Cálculo do total de confirmados
total_confirmados = dados_dengue_ano['Confirmados'].sum()
casos_novos_semana = pivot_table.iloc[:, -1].sum()

#Cálculo do total de óbitos
total_obitos = dados_dengue_ano['Óbitos'].sum()

#Cálculo da porcentagem de confirmação em relação às notificações
total_notificacoes = dados_dengue_ano['Notificações'].sum()
porcentagem_notificacoes = (total_confirmados*100/total_notificacoes).round(1)
valor_porcentagem = f'{porcentagem_notificacoes}%'

with coluna_filtros:
    coluna_confirmados, coluna_porcentagem = st.columns(2)
    coluna_confirmados.metric(label="Confirmados", value=total_confirmados, delta = casos_novos_semana)
    coluna_porcentagem.metric(label='% confirmados', value=valor_porcentagem)
    st.metric(label="Óbitos", value=total_obitos)

# Plotar um botão
#if st.button('Clique aqui'):
#    st.write('Botão clicado!')
  
#testa mapa
#map_fig = px.choropleth_mapbox(dados_dengue, geojson=dados_andre.geometry,
                         # locations=dados_dengue_final.index, color='Confirmados',
                        # color_continuous_scale = px.colors.diverging.hot,
                         # center ={'lat':-30.452349861219243, 'lon':-53.55320517512141},
                         # zoom=5.5,
                         # mapbox_style="carto-darkmatter",
                         # hover_name='NM_MUN',
                         # width=800,
                         # height=700,
                         # template='plotly_dark',
                         # title = f'Casos confirmados: {ano}')
