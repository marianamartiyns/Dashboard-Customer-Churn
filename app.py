import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# Carregando dados
df = pd.read_csv('data/churn.csv')

# Inicializando app
app = dash.Dash(__name__)
server = app.server  # Para o Render reconhecer

# Layout
app.layout = html.Div([
    html.H1("Dashboard de Clientes e Churn", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H4("Taxa de Churn"),
            html.Div(id='churn-rate', className='kpi'),
        ], className='card'),

        html.Div([
            html.H4("CLTV Médio"),
            html.Div(id='avg-cltv', className='kpi'),
        ], className='card'),

        html.Div([
            html.H4("Faturamento Médio"),
            html.Div(id='avg-revenue', className='kpi'),
        ], className='card'),
    ], className='kpi-container'),

    html.Div([
        html.Label("Filtrar por contrato:"),
        dcc.Dropdown(
            id='contract-filter',
            options=[{'label': i, 'value': i} for i in df['Contract'].unique()],
            multi=True
        ),
        html.Label("Filtrar por tipo de pagamento:"),
        dcc.Dropdown(
            id='payment-filter',
            options=[{'label': i, 'value': i} for i in df['Payment Method'].unique()],
            multi=True
        ),
    ], className='filter-container'),

    dcc.Graph(id='churn-by-gender'),
    dcc.Graph(id='cltv-map'),
    dcc.Graph(id='boxplot-charges'),
])

# Callback
@app.callback(
    Output('churn-rate', 'children'),
    Output('avg-cltv', 'children'),
    Output('avg-revenue', 'children'),
    Output('churn-by-gender', 'figure'),
    Output('cltv-map', 'figure'),
    Output('boxplot-charges', 'figure'),
    Input('contract-filter', 'value'),
    Input('payment-filter', 'value')
)
def update_dashboard(selected_contracts, selected_payments):
    filtered_df = df.copy()
    if selected_contracts:
        filtered_df = filtered_df[filtered_df['Contract'].isin(selected_contracts)]
    if selected_payments:
        filtered_df = filtered_df[filtered_df['Payment Method'].isin(selected_payments)]

    churn_rate = filtered_df['Churn Value'].mean() * 100
    avg_cltv = filtered_df['CLTV '].mean()
    avg_revenue = filtered_df['Monthly Charges'].mean()

    churn_fig = px.bar(
        filtered_df.groupby('Gender')['Churn Value'].mean().reset_index(),
        x='Gender', y='Churn Value',
        title="Churn por Gênero",
        labels={'Churn Value': 'Churn Rate'}
    )

    map_fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude", lon="Longitude",
        color="CLTV ",
        size="Monthly Charges",
        mapbox_style="open-street-map",
        zoom=2,
        title="Mapa de Clientes"
    )

    boxplot_fig = px.box(
        filtered_df,
        x="Contract", y="Monthly Charges",
        color="Churn Value",
        title="Distribuição de Cobrança Mensal por Contrato"
    )

    return (
        f"{churn_rate:.2f}%",
        f"R$ {avg_cltv:.2f}",
        f"R$ {avg_revenue:.2f}",
        churn_fig,
        map_fig,
        boxplot_fig
    )

if __name__ == '__main__':
    app.run_server(debug=True)
