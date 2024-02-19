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

#teste mapa
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

token = open(".mapbox_token").read() # you will need your own token

app = Dash(__name__)

# Carregar seus dados
meus_dados = pd.read_csv('https://ti.saude.rs.gov.br/ws/dengue_resid_csv.csv')

app.layout = html.Div([
    html.H4('Polotical candidate voting pool analysis'),
    html.P("Select a candidate:"),
    dcc.RadioItems(
        id='candidate', 
        options=["Joly", "Coderre", "Bergeron"],
        value="Coderre",
        inline=True
    ),
    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"), 
    Input("candidate", "value"))
def display_choropleth(candidate):
    # Substitua os dados de exemplo pelos seus próprios dados
    df = meus_dados
    geojson = px.data.election_geojson()

    fig = px.choropleth_mapbox(
        df, geojson=geojson, color=candidate,
        locations="district", featureidkey="properties.district",
        center={"lat": -30.056318114872877, "lon": , -51.18480842416186}, zoom=9,
        range_color=[0, 6500])
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_accesstoken=token)

    return fig

app.run_server(debug=True)
