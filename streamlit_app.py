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
col2.header('Painel Regional Dengue, 2024')
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
    zoom_ini = 5
else:
    dados_dengue_ano = dados_dengue.loc[(dados_dengue['Ano']==ano)&(dados_dengue['CRS'] == crs_selecionada)]
    pop_municipio_crs = pop_municipios.loc[(pop_municipios['CRS'] == crs_selecionada)]
    pop_municipios_index = pd.DataFrame(columns=[], index=pop_municipio_crs['Munic\u00edpio'].unique())
    zoom_ini = 7
    index_selecionado = 'Nome Município'

# Create a pivot table
pivot_table = pd.pivot_table(dados_dengue_ano, values='Confirmados', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)
# Concatenando as tabelas para gerar TUDO
pivot_table = pd.concat([pop_municipios_index, pivot_table], axis=1).fillna(0)

pivot_table_notific = pd.pivot_table(dados_dengue_ano, values='Notificações', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)
pivot_table_notific = pd.concat([pop_municipios_index, pivot_table_notific], axis=1).fillna(0)

pivot_table_obitos = pd.pivot_table(dados_dengue_ano, values='Óbitos', index=index_selecionado, columns='Semana Epidemiol\u00f3gica', aggfunc='sum', fill_value=0)
pivot_table_obitos = pd.concat([pop_municipios_index, pivot_table_obitos], axis=1).fillna(0)

#Criar as abas
aba_confirmados, aba_notificacoes, aba_consolidados, aba_estimativa = st.tabs(['Confirmados', 'Notificações', 'Consolidados', 'Estimativas - Infodengue'])

with aba_confirmados:
    coluna_tabela_confirmados, coluna_mapa_grafico_confirmados = st.columns([2,2])

with aba_notificacoes:
    coluna_tabela_notificacoes, coluna_mapa_grafico_notificacoes = st.columns([2,2])

# Print the pivot table
if len(pivot_table)<10:
    altura_dinamica = 500

else:
    altura_dinamica = 800/24*len(pivot_table)
    
with coluna_tabela_confirmados:
        st.write(f'Casos confirmados por semana epidemiológica por município, RS, {ano}')
        heatmap_fig_conf = px.imshow(pivot_table, text_auto=True, color_continuous_scale='OrRd', width=800, height=altura_dinamica, aspect = 'equal')
        heatmap_fig_conf.update_layout(xaxis=dict(side='top', title='Semana Epidemiológica')) # Posicionando o rótulo do eixo X na parte superior
     # Posicionando o rótulo do eixo X na parte superior
        st.plotly_chart(heatmap_fig_conf, use_container_width=False)

with coluna_tabela_notificacoes:
        st.write(f'Notificações por semana epidemiológica por município, RS, {ano}')
        heatmap_fig_notific = px.imshow(pivot_table_notific, text_auto=True, color_continuous_scale='Blues', width=800, height=altura_dinamica, aspect = 'equal')
        heatmap_fig_notific.update_layout(xaxis=dict(side='top')) # Posicionando o rótulo do eixo X na parte superior
        st.plotly_chart(heatmap_fig_notific, use_container_width=False)    

# Aba de consolidados

with aba_consolidados:
    pivot_table_consolidados = pd.pivot_table(dados_dengue_ano, values=['Notificações', 'Confirmados','Autóctones', 'Investigação','Óbitos'], index=index_selecionado, aggfunc='sum', fill_value=0)
    heatmap_fig_consolidados = px.imshow(pivot_table_consolidados, text_auto=True,
                                         color_continuous_scale='Greys', width=1200,
                                         height=altura_dinamica, aspect = 'equal')
    heatmap_fig_consolidados.update_layout(xaxis=dict(side='top')) # Posicionando o rótulo do eixo X na parte superior
    st.plotly_chart(heatmap_fig_consolidados, use_container_width=True)   


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
fig_confirmados = px.line(dados_dengue_consolidados, x='Semana Epidemiológica', y='Confirmados', color='Ano', markers=True, title='Casos confirmados por semana epidemiológica, RS, 2020-2024')

dados_dengue_notific = dados_dengue_2020_atual.groupby(['Ano', 'Semana Epidemiológica']).agg({'Notificações': 'sum'}).reset_index()
fig_notificacoes = px.line(dados_dengue_notific, x='Semana Epidemiológica', y='Notificações', color='Ano', markers=True, title='Notificações por semana epidemiológica, RS, 2020-2024')



# Mapa
# Criação da tabela suporte
indice_mapa = pop_municipio_crs[['Município', 'IBGE6']].set_index(['Município', 'IBGE6'])

# Filtro somente das últimas 4 semanas
from datetime import datetime, timedelta

def ultimas_quatro_semanas():
    data_atual = datetime.now()
    semanas = []

    # Calcula os números das últimas quatro semanas
    for i in range(4):
        semana_inicio = data_atual - timedelta(days=data_atual.weekday() + i * 7)
        semana_fim = semana_inicio + timedelta(days=6)
        semana_numero = data_atual.isocalendar()[1] - i  # Número da semana atual menos i
        semanas.append(semana_numero)

    return semanas

quatro_ultimas_semanas = ultimas_quatro_semanas()
filtro_quatro_ultimas_semanas = dados_dengue_ano['Semana Epidemiológica'].isin(quatro_ultimas_semanas)
st.write(quatro_ultimas_semanas)

# Criando DF para usar no mapa
tabela_mapa = pd.pivot_table(dados_dengue_ano[filtro_quatro_ultimas_semanas], values=['Confirmados', 'Notificações'],
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
tabela_mapa_pop['incidencia_notificacoes'] = (tabela_mapa_pop['Notificações']/tabela_mapa_pop['População_estimada']*100000).round(2)
tabela_geo_mapa_pop_inci =  municipios.merge(tabela_mapa_pop, left_on='CD_MUN', right_on='IBGE6')
tabela_geo_mapa_pop_inci['incidencia_confirmados'] = tabela_geo_mapa_pop_inci['incidencia_confirmados'].fillna(0)
tabela_geo_mapa_pop_inci['incidencia_notificacoes'] = tabela_geo_mapa_pop_inci['incidencia_notificacoes'].fillna(0)

latitude_media = (tabela_geo_mapa_pop_inci['geometry'].centroid.y.max() + tabela_geo_mapa_pop_inci['geometry'].centroid.y.min())/2
longitude_media = (tabela_geo_mapa_pop_inci['geometry'].centroid.x.max() + tabela_geo_mapa_pop_inci['geometry'].centroid.x.min())/2
tabela_geo_mapa_pop_inci
#Mapa da incidência por município
map_fig_confirmados = px.choropleth_mapbox(tabela_geo_mapa_pop_inci, geojson=tabela_geo_mapa_pop_inci.geometry,
                          locations=tabela_geo_mapa_pop_inci.index, color='incidencia_confirmados',
                          color_continuous_scale='OrRd',
                          center ={'lat':latitude_media, 'lon':longitude_media},
                          zoom=zoom_ini,
                          hover_data={'tabela_geo_mapa_pop_inci.index':False},
                          mapbox_style="carto-positron",
                          hover_name='NM_MUN',
                          width=800,
                          height=700,
                          #template='plotly_dark',
                          title = 'Incidência de casos confirmados de dengue nas últimas 4 semanas epidemiológicas, RS, 2024')

map_fig_confirmados.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=50, b=10),
                                  )
map_fig_confirmados.update_traces(marker_line_width=0.2)
map_fig_confirmados.update_coloraxes(colorbar={'orientation':'h'},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.13)

#Mapa da incidência por município
map_fig_notificacoes = px.choropleth_mapbox(tabela_geo_mapa_pop_inci, geojson=tabela_geo_mapa_pop_inci.geometry,
                          locations=tabela_geo_mapa_pop_inci.index, color='incidencia_notificacoes',
                          color_continuous_scale='Blues',
                          center ={'lat':latitude_media, 'lon':longitude_media},
                          zoom=zoom_ini,
                          mapbox_style="carto-positron",
                          hover_name='NM_MUN',
                          width=800,
                          height=700,
                          #template='plotly_dark',
                          title = 'Incidência de Notificações de dengue nas últimas 4 semanas epidemiológicas, RS, 2024')

map_fig_notificacoes.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=50, b=10),
                                  )
map_fig_notificacoes.update_traces(marker_line_width=0.2)
map_fig_notificacoes.update_coloraxes(colorbar={'orientation':'h'},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.13)

with coluna_mapa_grafico_confirmados:
    st.plotly_chart(map_fig_confirmados, use_container_width=True)
    st.plotly_chart(fig_confirmados, use_container_width=True)

with coluna_mapa_grafico_notificacoes:
    st.plotly_chart(map_fig_notificacoes, use_container_width=True)
    st.plotly_chart(fig_notificacoes, use_container_width=True)

with aba_estimativa:
    coluna_grafico_estimativa, coluna_mapa_estimativa = st.columns(2)
    # Filtrando o DataFrame de casos reais apenas para 2024
    dados_dengue_consolidados_2024 = dados_dengue_consolidados[dados_dengue_consolidados['Ano']==2024]
    dados_estimativa = pd.read_csv('https://drive.google.com/uc?export=download&id=14-srx6dAphqr6zTgQK2_9Rc4YqsFg4H7',sep=';')
    ibge_crs = pop_municipio_crs[['IBGE6', 'CRS']]
    dados_estimativa_crs = dados_estimativa.merge(ibge_crs, on='IBGE6', how='right')
    dados_estimativa_crs_pivot = pd.pivot_table(dados_estimativa_crs, index='SE', values=['casos_est','casos_est_min', 'casos_est_max'], aggfunc='sum').reset_index()
    dados_estimativa_crs_pivot['Semana Epidemiológica'] = dados_estimativa_crs_pivot['SE']-202400
    
    # Criando o gráfico com Plotly Express
    fig_est = px.line(title='Estimativa de casos de dengue e Confirmados em 2024')

    # Adicionando a linha de estimativa de casos (pontilhada)
    fig_est.add_scatter(x=dados_estimativa_crs_pivot['Semana Epidemiológica'], y=dados_estimativa_crs_pivot['casos_est'], mode='lines+markers', line=dict(dash='dash', color='red'), name='Estimativa de casos', )    
    
    # Adicionando a área hachurada entre os valores mínimos e máximos de casos estimados
    fig_est.add_scatter(x=dados_estimativa_crs_pivot['Semana Epidemiológica'], y=dados_estimativa_crs_pivot['casos_est_min'], fill='tonexty', mode='none', fillcolor='rgba(225,229,232,0.5)', name='Intervalo estimado')
    fig_est.add_scatter(x=dados_estimativa_crs_pivot['Semana Epidemiológica'], y=dados_estimativa_crs_pivot['casos_est_max'], fill='tonexty', mode='none', fillcolor='rgba(225,229,232,0.5)', showlegend=False)


    
    # Adicionando a linha de casos confirmados (contínua)
    fig_est.add_scatter(x=dados_dengue_consolidados_2024['Semana Epidemiológica'], y=dados_dengue_consolidados_2024['Confirmados'], mode='lines+markers', name='Casos Confirmados', line=dict(color='black'))
       
    # Exibindo o gráfico
    with coluna_grafico_estimativa:
        st.markdown("""
            O [InfoDengue](https://info.dengue.mat.br/informacoes/) é um sistema de alerta para arboviroses baseado em dados híbridos gerados por meio da análise integrada de dados minerados
            a partir da web social e de dados climáticos e epidemiológicos, que gera indicadores de situação epidemiológica da dengue e outras arboviroses a nível municipal.
            """)
        with st.expander('Sobre o InfoDengue'):
            st.write("""
                De onde vem os dados?
                
O sistema InfoDengue é uma ferramenta semi-automatizada que coleta, harmoniza e analisa dados para fornecer indicadores da situação epidemiológica da dengue e outras arboviroses em nível municipal. Os dados utilizados incluem casos notificados de dengue, chikungunya e zika, informações meteorológicas e dados demográficos dos municípios brasileiros.

Uma das principais funções do sistema é corrigir o atraso de notificação das doenças, através de um método estatístico baseado em inferência Bayesiana, permitindo a estimativa do número esperado de casos a cada semana, conhecido como "nowcasting". Além disso, o sistema é capaz de detectar transmissão sustentada das arboviroses, estimar o número reprodutivo (R0 e Rt) e analisar a receptividade de diferentes localidades às condições climáticas favoráveis à transmissão.

O InfoDengue também realiza a detecção de situações atípicas, estimando limiares epidêmicos e proporcionando alertas precoces sobre a chegada da temporada de arboviroses. Utilizando metodologias próprias e dados históricos locais, o sistema é capaz de identificar padrões sazonais e definir zonas de atividade semanal, contribuindo para a tomada de decisões em saúde pública e o controle eficaz dessas doenças.
 """)      
            st.image('https://info.dengue.mat.br/static/img/table_color_level_pt.png')
        st.plotly_chart(fig_est, use_container_width=True)
        dados_estimativa_crs['nivel_descricao'] = dados_estimativa_crs['nivel'].fillna(1).replace({
            1:'Baixa Transmissão', 2:'Atenção', 3:'Transmissão Sustentada', 4:'Alta Incidência'
        })
    dados_estimativa_crs_mapa = dados_estimativa_crs.sort_values('SE').drop_duplicates(subset=['Municipio'], keep='last')
    dados_estimativa_crs_mapa_ibge =  municipios.merge(dados_estimativa_crs_mapa, left_on='CD_MUN', right_on='IBGE6').sort_values('nivel')
    map_fig_nivel = px.choropleth_mapbox(dados_estimativa_crs_mapa_ibge, geojson=dados_estimativa_crs_mapa_ibge.geometry,
                          locations=dados_estimativa_crs_mapa_ibge.index, color='nivel_descricao',
                          color_discrete_map = {'Baixa Transmissão':'#6DBE45', 'Atenção':'#FFE34C', 'Transmissão Sustentada':'darkorange', 'Alta Incidência':'#D83027'},
                          center ={'lat':latitude_media, 'lon':longitude_media},
                          zoom=zoom_ini,
                          mapbox_style="carto-positron",
                          hover_name='NM_MUN',
                          width=800,
                          height=600,
                          #template='plotly_dark',
                          title = 'Nível de alerta InfoDengue por município, RS, 2024')

    map_fig_nivel.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=50, b=10),
                                      )
    map_fig_nivel.update_traces(marker_line_width=0.2)
    map_fig_nivel.update_coloraxes(colorbar={'orientation':'h'},
                             colorbar_yanchor='bottom',
                             colorbar_y=-0.13)

    with coluna_mapa_estimativa:
        st.plotly_chart(map_fig_nivel, use_container_width=True)
    


