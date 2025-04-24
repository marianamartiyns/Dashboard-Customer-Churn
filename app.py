import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

# ===================== DADOS =====================
df = pd.read_csv('data/churn.csv')
df.columns = df.columns.str.strip()

contract_map = {0: 'Mensal', 1: 'Anual (1 ano)', 2: 'Bienal (2 anos)'}
if df['Contract'].dtype != object:
    df['Contract'] = df['Contract'].map(contract_map)

payment_map = {
    0: 'Cheque eletrônico',
    1: 'Cheque enviado pelo correio',
    2: 'Transferência bancária (automática)',
    3: 'Cartão de crédito (automático)'
}
if df['Payment Method'].dtype != object:
    df['Payment Method'] = df['Payment Method'].map(payment_map)

# ===================== APP =====================
contract_options = ['Mensal', 'Anual (1 ano)', 'Bienal (2 anos)']
payment_options = list(payment_map.values())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# ===================== LAYOUT =====================
app.layout = dbc.Container(fluid=True, className="p-4", children=[
    dbc.Row(dbc.Col(html.H1("Dashboard de Clientes e Churn", className="text-center fw-bold mb-4"))),
    dbc.Row(dbc.Col(html.Div(id='kpi-cards', className='d-flex flex-wrap gap-2'))),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='contract-filter',
                             options=[{'label': opt, 'value': opt} for opt in contract_options],
                             placeholder="Tipo de Contrato", clearable=True), width=6),
        dbc.Col(dcc.Dropdown(id='payment-filter',
                             options=[{'label': opt, 'value': opt} for opt in payment_options],
                             placeholder="Método de Pagamento", clearable=True), width=6)
    ], className="my-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='churn-tenure-hist'), width=6),
        dbc.Col(dcc.Graph(id='churn-tenure-hist2'), width=6)
    ]),
    dbc.Row(dbc.Col(dcc.Graph(id='churn-score-time'))),
    dbc.Row([
        dbc.Col(dcc.Graph(id='churn-by-payment'), width=6),
        dbc.Col(dcc.Graph(id='churn-by-contract'), width=6)
    ]),
    dbc.Row(dbc.Col(dcc.Graph(id='churn-gender-senior'))),
    dbc.Row([
        dbc.Col(dcc.Graph(id='phone-service-fig'), width=4),
        dbc.Col(dcc.Graph(id='internet-service-fig'), width=4),
        dbc.Col(dcc.Graph(id='security-service-fig'), width=4)
    ]),
    dbc.Row(dbc.Col(dcc.Graph(id='boxplot-charges'))),
    dbc.Row(dbc.Col(dcc.Graph(id='cltv-map')))
])

# ===================== CALLBACK =====================
@app.callback(
    Output('kpi-cards', 'children'),
    Output('churn-tenure-hist', 'figure'),
    Output('churn-tenure-hist2', 'figure'),
    Output('churn-score-time', 'figure'),
    Output('churn-by-payment', 'figure'),
    Output('churn-by-contract', 'figure'),
    Output('churn-gender-senior', 'figure'),
    Output('phone-service-fig', 'figure'),
    Output('internet-service-fig', 'figure'),
    Output('security-service-fig', 'figure'),
    Output('boxplot-charges', 'figure'),
    Output('cltv-map', 'figure'),
    Input('contract-filter', 'value'),
    Input('payment-filter', 'value')
)
def update_dashboard(selected_contract, selected_payment):
    df2 = df.copy()
    if selected_contract:
        df2 = df2[df2['Contract'] == selected_contract]
    if selected_payment:
        df2 = df2[df2['Payment Method'] == selected_payment]

    if df2.empty:
        empty_fig = px.scatter()
        return [html.Div("0", className="card-value")]*12

    color_map = {
        'Cheque eletrônico': '#ee6352',
        'Cheque enviado pelo correio': '#59cd90',
        'Transferência bancária (automática)': '#3fa7d6',
        'Cartão de crédito (automático)': '#fac05e',
        'Mensal': '#8cb369',
        'Anual (1 ano)': '#f4e285',
        'Bienal (2 anos)': '#f4a259',
        'Adulto': '#348aa7',
        'Idoso': '#525174'
    }

    title_font = {'family': 'Arial', 'size': 18, 'color': '#2c3e50', 'weight': 'bold'}
    common_layout = {'title_font': title_font, 'title_x': 0.5, 'template': 'plotly_white'}

    kpis = {
        "Taxa de Churn (%)": df2['Churn Value'].mean() * 100,
        "CLTV Médio (R$)": df2['CLTV'].mean(),
        "Faturamento Médio (R$)": df2['Monthly Charges'].mean(),
        "Tempo Médio (meses)": df2['Tenure Months'].mean(),
        "% de Idosos": df2['Senior Citizen'].mean() * 100
    }
    card_classes = [
        "card card-churn",
        "card card-cltv",
        "card card-retention",
        "card card-mensal",
        "card card-idosos"
    ]

    cards = [html.Div([
        html.Div(f"{val:.1f}" + ("%" if "%" in label else ""), className="card-value"),
        html.Div(label, className="card-label")
    ], className=card_classes[i]) for i, (label, val) in enumerate(kpis.items())]

    # Histograma de churn
    churn_hist_fig = px.histogram(df2[df2['Churn Value'] == 1], x="Tenure Months", nbins=50,
                                  title="Duração de Permanência - Clientes que Cancelaram",
                                  color_discrete_sequence=["#9b0d27"])
    churn_hist_fig.update_traces(marker_line_color="white", marker_line_width=1)
    churn_hist_fig.update_layout(**common_layout)

    churn_hist_fig2 = px.histogram(df2[df2['Churn Value'] == 0], x="Tenure Months", nbins=50,
                                   title="Duração de Permanência - Clientes que Não Cancelaram",
                                   color_discrete_sequence=["#1E7B4A"])
    churn_hist_fig2.update_traces(marker_line_color="white", marker_line_width=1)
    churn_hist_fig2.update_layout(**common_layout)

    churn_score_fig = px.line(df2.groupby('Tenure Months')['Churn Score'].mean().reset_index(),
                              x='Tenure Months', y='Churn Score', title="Churn Score por Tempo")
    churn_score_fig.update_layout(**common_layout)

    # Churn por método de pagamento
    payment_fig = px.bar(df2.groupby('Payment Method')['Churn Value'].mean().reset_index(),
                         x='Payment Method', y='Churn Value', title='Churn por Pagamento',
                         color='Payment Method', color_discrete_map=color_map,
                         text='Churn Value')
    payment_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    payment_fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')

    # Churn por tipo de contrato
    contract_fig = px.bar(df2.groupby('Contract')['Churn Value'].mean().reset_index(),
                          x='Contract', y='Churn Value', title='Churn por Contrato',
                          color='Contract', color_discrete_map=color_map,
                          text='Churn Value')
    contract_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    contract_fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')

    # Churn por gênero e idade
    df2['Gender'] = df2['Gender'].map({0: 'Masculino', 1: 'Feminino'})
    df2['Senior Citizen'] = df2['Senior Citizen'].map({0: 'Adulto', 1: 'Idoso'})

    gender_senior_fig = px.bar(df2.groupby(['Gender', 'Senior Citizen'])['Churn Value'].mean().reset_index(),
                               x='Gender', y='Churn Value', color='Senior Citizen', barmode='group',
                               title='Churn por Gênero e Idade', text='Churn Value',
                               color_discrete_map=color_map)
    gender_senior_fig.update_layout(**common_layout)
    gender_senior_fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')

    # Serviços
    df2['Phone Service'] = df2['Phone Service'].map({0: 'No', 1: 'Yes'}).fillna(df2['Phone Service'])
    df2['Internet Service'] = df2['Internet Service'].map({0: 'DSL', 1: 'Fiber optic', 2: 'No'}).fillna(df2['Internet Service'])
    df2['Online Security'] = df2['Online Security'].map({0: 'No', 1: 'Yes', 2: 'No internet service'}).fillna(df2['Online Security'])

    phone_service_fig = px.histogram(df2, x='Phone Service', title='Serviço de Telefone',
                                     color='Phone Service', text_auto=True,
                                     color_discrete_map={'Yes': '#3fa7d6', 'No': '#9b0d27'})
    phone_service_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    phone_service_fig.update_traces(texttemplate='%{y}', textposition='outside')

    internet_service_fig = px.histogram(df2, x='Internet Service', title='Serviço de Internet',
                                        color='Internet Service', text_auto=True,
                                        color_discrete_map={'DSL': '#fac05e', 'Fiber optic': '#ee6352', 'No': '#59cd90'})
    internet_service_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    internet_service_fig.update_traces(texttemplate='%{y}', textposition='outside')

    security_service_fig = px.histogram(df2, x='Online Security', title='Segurança Online',
                                        color='Online Security', text_auto=True,
                                        color_discrete_map={'Yes': '#3fa7d6', 'No': '#9b0d27', 'No internet service': '#748594'})
    security_service_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    security_service_fig.update_traces(texttemplate='%{y}', textposition='outside')

    bar_df = df2.groupby('Contract')['Monthly Charges'].mean().reset_index()
    bar_df = bar_df.sort_values(by='Monthly Charges', ascending=False)
    boxplot_fig = px.bar(
    df2.groupby('Contract')['Monthly Charges'].mean().reset_index().sort_values(by='Monthly Charges', ascending=False),
    x='Monthly Charges',
    y='Contract',
    orientation='h',
    title='Média de Cobrança Mensal por Contrato',
    color='Contract',
    color_discrete_map={
        'Mensal': '#8cb369',         # Verde oliva
        'Anual (1 ano)': '#f4e285',  # Amarelo claro
        'Bienal (2 anos)': '#f4a259' # Laranja queimado
    },
    text='Monthly Charges'
    )
    boxplot_fig.update_layout(**common_layout)
    boxplot_fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')


    map_fig = px.scatter_mapbox(df2, lat='Latitude', lon='Longitude',
                                color='CLTV', size='Monthly Charges',
                                title='Mapa de Clientes por CLTV',
                                mapbox_style='carto-positron',
                                color_continuous_scale='Viridis')
    map_fig.update_layout(**common_layout)

    return cards, churn_hist_fig, churn_hist_fig2, churn_score_fig, payment_fig, contract_fig, gender_senior_fig, phone_service_fig, internet_service_fig, security_service_fig, boxplot_fig, map_fig


if __name__ == '__main__':
    app.run(debug=True)
