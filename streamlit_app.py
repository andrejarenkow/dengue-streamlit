# Importação de bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd

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
coluna_filtros, coluna_notif, coluna_confirmados, coluna_porcentagem, coluna_obitos = st.columns(5)
with coluna_filtros:
    container_filtros = st.container(border=True)

# Carrega dados de casos de dengue de um arquivo CSV
arquivo = 'https://ti.saude.rs.gov.br/ws/dengue_resid_csv.csv'
dados_dengue = pd.read_csv(arquivo, sep=',', encoding='latin1')

# Carrega dados de referência dos municípios
pop_municipios = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv')
pop_municipios['Município'] = pop_municipios['Município'].replace("Sant'Ana do Livramento", 'Santana do Livramento')

ano = 2024

# Qual index
with container_filtros:
    lista_crs = sorted((dados_dengue['CRS'].unique()).tolist())
    lista_crs.append('Todas')
    crs_selecionada = st.selectbox('Selecione a CRS', lista_crs, index=18)

# Filtrar o dataframe
if crs_selecionada == 'Todas':
    dados_dengue_ano = dados_dengue.loc[(dados_dengue['Ano']==ano)]
    pop_municipio_crs = pop_municipios.copy() #criação fake
    index_selecionado = 'CRS'
    pop_municipios_index = pd.DataFrame()
else:
    dados_dengue_ano = dados_dengue.loc[(dados_dengue['Ano']==ano)&(dados_dengue['CRS'] == crs_selecionada)]
    pop_municipio_crs = pop_municipios.loc[(pop_municipios['CRS'] == crs_selecionada)]
    pop_municipios_index = pd.DataFrame(columns=[], index=pop_municipio_crs['Munic\u00edpio'].unique())

    index_selecionado = 'Nome Município'

# Create a pivot table
pivot_table = pd.pivot_table(dados_dengue_ano, values='Confirmados', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)
# Concatenando as tabelas para gerar TUDO
pivot_table = pd.concat([pop_municipios_index, pivot_table], axis=1).fillna(0)

pivot_table_notific = pd.pivot_table(dados_dengue_ano, values='Notificações', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)
pivot_table_obitos = pd.pivot_table(dados_dengue_ano, values='Óbitos', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)

coluna_tabela, coluna_mapa_grafico = st.columns([3,2])

# Print the pivot table
altura_dinamica = 800/24*len(pivot_table)
with coluna_tabela:
    aba_confirmados, aba_notificacoes = st.tabs(['Confirmados', 'Notificações'])
    with aba_confirmados:
        st.write(f'Casos confirmados por semana epidemiológica por município, RS, {ano}')
        heatmap_fig_conf = px.imshow(pivot_table, text_auto=True, color_continuous_scale='OrRd', width=800, height=altura_dinamica)
        heatmap_fig_conf.update_layout(xaxis=dict(side='top', title='Semana Epidemiológica')) # Posicionando o rótulo do eixo X na parte superior
     # Posicionando o rótulo do eixo X na parte superior
        st.plotly_chart(heatmap_fig_conf, use_container_width=False)

    with aba_notificacoes:
        st.write(f'Notificações por semana epidemiológica por município, RS, {ano}')
        heatmap_fig_notific = px.imshow(pivot_table_notific, text_auto=True, color_continuous_scale='Blues', width=800, height=altura_dinamica)
        heatmap_fig_notific.update_layout(xaxis=dict(side='top')) # Posicionando o rótulo do eixo X na parte superior
        st.plotly_chart(heatmap_fig_notific, use_container_width=False)    


#Cálculo do total de confirmados
total_confirmados = dados_dengue_ano['Confirmados'].sum()
casos_novos_semana = int(pivot_table.iloc[:, -1].sum())

#Cálculo do total de notificações
total_notific = dados_dengue_ano['Notificações'].sum()
notific_novos_semana = int(pivot_table_notific.iloc[:, -1].sum())

#Cálculo do total de óbitos
total_obitos = dados_dengue_ano['Óbitos'].sum()
obitos_novos_semana = int(pivot_table_obitos.iloc[:, -1].sum())

#Cálculo da porcentagem de confirmação em relação às notificações
total_notificacoes = dados_dengue_ano['Notificações'].sum()
porcentagem_notificacoes = (total_confirmados*100/total_notificacoes).round(1)
valor_porcentagem = f'{porcentagem_notificacoes}%'

# Cards com as métricas
coluna_confirmados.metric(label="Confirmados", value=total_confirmados, delta = casos_novos_semana, delta_color="inverse")
coluna_porcentagem.metric(label='% confirmados', value=valor_porcentagem)
coluna_obitos.metric(label="Óbitos", value=total_obitos, delta = obitos_novos_semana, delta_color="inverse")
coluna_notif.metric(label="Notificações", value=total_notific, delta = notific_novos_semana, delta_color="inverse")
    
    
    

# Agrupe os dados pela semana epidemiológica e some os casos confirmados
# Filtrar o dataframe
if crs_selecionada == 'Todas':
    dados_dengue_2020_atual = dados_dengue[(dados_dengue['Ano']>2019)]

else:
    dados_dengue_2020_atual = dados_dengue[(dados_dengue['Ano']>2019)&(dados_dengue['CRS'] == crs_selecionada)]
    
dados_dengue_consolidados = dados_dengue_2020_atual.groupby(['Ano', 'Semana Epidemiológica']).agg({'Confirmados': 'sum'}).reset_index()

fig = px.line(dados_dengue_consolidados, x='Semana Epidemiológica', y='Confirmados', color='Ano', markers=True, title='Casos confirmados por semana epidemiológica, RS, 2020-2024')


  
# Mapa
# Criação da tabela suporte
indice_mapa = pop_municipio_crs[['Município', 'IBGE6']].set_index(['Município', 'IBGE6'])

tabela_mapa = pd.pivot_table(dados_dengue_ano, values=['Confirmados', 'Notificações'],
               index=['Nome Munic\u00edpio', 'Cód IBGE'],
               aggfunc='sum', fill_value=0)
tabela_mapa = pd.concat([tabela_mapa, indice_mapa], axis=1).fillna(0).reset_index()
tabela_mapa.columns = ['Nome Munic\u00edpio', 'Cód IBGE', 'Confirmados', 'Notificações']

tabela_mapa_pop = tabela_mapa.merge(pop_municipio_crs, left_on='Cód IBGE', right_on='IBGE6', how='right')
tabela_mapa_pop['Confirmados'] = tabela_mapa_pop['Confirmados'].fillna(0)
tabela_mapa_pop['Notificações'] = tabela_mapa_pop['Notificações'].fillna(0)
                                    
municipios = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
municipios['CD_MUN'] = municipios['CD_MUN'].str[:6]
municipios['CD_MUN'] = municipios['CD_MUN'].astype(int)

tabela_mapa_pop['incidencia_confirmados'] = (tabela_mapa_pop['Confirmados']/tabela_mapa_pop['População_estimada']*100000).round(2)
tabela_geo_mapa_pop_inci =  municipios.merge(tabela_mapa_pop, left_on='CD_MUN', right_on='IBGE6')
tabela_geo_mapa_pop_inci['incidencia_confirmados'] = tabela_geo_mapa_pop_inci['incidencia_confirmados'].fillna(0)

latitude_media = tabela_geo_mapa_pop_inci['geometry'].centroid.y.mean()
longitude_media = tabela_geo_mapa_pop_inci['geometry'].centroid.x.mean()

#Mapa da incidência por município
map_fig = px.choropleth_mapbox(tabela_geo_mapa_pop_inci, geojson=tabela_geo_mapa_pop_inci.geometry,
                          locations=tabela_geo_mapa_pop_inci.index, color='incidencia_confirmados',
                          color_continuous_scale='OrRd',
                          center ={'lat':latitude_media, 'lon':longitude_media},
                          #zoom=5.5,
                          mapbox_style="open-street-map",
                          hover_name='NM_MUN',
                          width=800,
                          height=700,
                          #template='plotly_dark',
                          title = 'Incidência de casos confirmados de dengue, RS, 2024')

map_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=50, b=10),
                                  )
map_fig.update_traces(marker_line_width=0.2)
map_fig.update_coloraxes(colorbar={'orientation':'h'},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.13)

with coluna_mapa_grafico:
    st.plotly_chart(map_fig, use_container_width=True)
    st.plotly_chart(fig, use_container_width=True)
