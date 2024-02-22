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

# Qual index
with container_filtros:
    lista_crs = sorted((dados_dengue['CRS'].unique()).tolist())
    lista_crs.append('Todas')
    crs_selecionada = st.selectbox('Selecione a CRS', lista_crs, index=18)

# Filtrar o dataframe
if crs_selecionada == 'Todas':
    dados_dengue_ano = dados_dengue.loc[(dados_dengue['Ano']==ano)]
    index_selecionado = 'CRS'
else:
    dados_dengue_ano = dados_dengue.loc[(dados_dengue['Ano']==ano)&(dados_dengue['CRS'] == crs_selecionada)]
    index_selecionado = 'Nome Município'

# Create a pivot table
pivot_table = pd.pivot_table(dados_dengue_ano, values='Confirmados', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)
pivot_table_obitos = pd.pivot_table(dados_dengue_ano, values='Óbitos', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)

# Print the pivot table
with coluna_dados:
    heatmap_fig = px.imshow(pivot_table, text_auto=True, color_continuous_scale='OrRd', width=800, height=800,
                            title=f'Casos por semana epidemiológica por município, RS, {ano}')
    st.plotly_chart(heatmap_fig, use_container_width=False)


#Cálculo do total de confirmados
total_confirmados = dados_dengue_ano['Confirmados'].sum()
casos_novos_semana = int(pivot_table.iloc[:, -1].sum())

#Cálculo do total de óbitos
total_obitos = dados_dengue_ano['Óbitos'].sum()
obitos_novos_semana = int(pivot_table_obitos.iloc[:, -1].sum())

#Cálculo da porcentagem de confirmação em relação às notificações
total_notificacoes = dados_dengue_ano['Notificações'].sum()
porcentagem_notificacoes = (total_confirmados*100/total_notificacoes).round(1)
valor_porcentagem = f'{porcentagem_notificacoes}%'

with coluna_filtros:
    coluna_confirmados, coluna_porcentagem = st.columns(2)
    coluna_confirmados.metric(label="Confirmados", value=total_confirmados, delta = casos_novos_semana, delta_color="inverse")
    coluna_porcentagem.metric(label='% confirmados', value=valor_porcentagem)
    st.metric(label="Óbitos", value=total_obitos, delta = obitos_novos_semana, delta_color="inverse")

# Agrupe os dados pela semana epidemiológica e some os casos confirmados
# Filtrar o dataframe
if crs_selecionada == 'Todas':
    dados_dengue_2020_atual = dados_dengue[(dados_dengue['Ano']>2019)]

else:
    dados_dengue_2020_atual = dados_dengue[(dados_dengue['Ano']>2019)&(dados_dengue['CRS'] == crs_selecionada)]
    
dados_dengue_consolidados = dados_dengue_2020_atual.groupby(['Ano', 'Semana Epidemiológica']).agg({'Confirmados': 'sum'}).reset_index()

fig = px.line(dados_dengue_consolidados, x='Semana Epidemiológica', y='Confirmados', color='Ano', markers=True, title='Casos confirmados por semana epidemiológica, RS, 2020-2024')
st.plotly_chart(fig, use_container_width=True)
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
