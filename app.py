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
    dbc.Row(dbc.Col(dcc.Graph(id='churn-gender-age-fig'))),  # Alterado aqui

    dbc.Row([
        dbc.Col(dcc.Graph(id='phone-service-fig'), width=4),
        dbc.Col(dcc.Graph(id='internet-service-fig'), width=4),
        dbc.Col(dcc.Graph(id='security-service-fig'), width=4)
    ]),
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
    Output('churn-gender-age-fig', 'figure'),
    Output('phone-service-fig', 'figure'),
    Output('internet-service-fig', 'figure'),
    Output('security-service-fig', 'figure'),
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
        return [html.Div("0", className="card-value")]*11

    color_map = {
        'Feminino - Adulto': '#A054DE',
        'Feminino - Idoso': '#5F209E',
        'Masculino - Adulto': '#3C80DE',
        'Masculino - Idoso': '#083B96',
        'Cheque eletrônico': '#e0db56',
        'Cheque enviado pelo correio': '#9fc22c',
        'Transferência bancária (automática)': '#d04343',
        'Cartão de crédito (automático)': '#f4a259',
        'Mensal': '#d04343',
        'Anual (1 ano)': '#f4e285',
        'Bienal (2 anos)': '#8cb369',
    }

    title_font = {'family': 'Arial', 'size': 18, 'color': '#2c3e50', 'weight': 'bold'}
    common_layout = {'title_font': title_font, 'title_x': 0.5, 'template': 'plotly_white'}

    df2['Gender'] = df2['Gender'].map({0: 'Masculino', 1: 'Feminino'})
    df2['Senior Citizen'] = df2['Senior Citizen'].map({0: 'Adulto', 1: 'Idoso'})
    df2['Grupo'] = df2['Gender'] + " - " + df2['Senior Citizen']

    churn_group = df2.groupby(['Gender', 'Senior Citizen', 'Grupo'])['Churn Value'].mean().reset_index()

    churn_gender_age_fig = px.bar(
        churn_group, x='Gender', y='Churn Value', color='Grupo',
        title='Churn por Gênero e Faixa Etária',
        text='Churn Value', color_discrete_map=color_map
    )
    churn_gender_age_fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    churn_gender_age_fig.update_layout(
        xaxis_title='Gênero',
        yaxis_title='Taxa de Churn',
        barmode='stack',
        **common_layout
    )

    # KPIs
    kpis = {
        "Taxa de Churn (%)": df2['Churn Value'].mean() * 100,
        "CLTV Médio (R$)": df2['CLTV'].mean(),
        "Faturamento Médio (R$)": df2['Monthly Charges'].mean(),
        "Tempo Médio (meses)": df2['Tenure Months'].mean(),
        "% de Idosos": df2['Senior Citizen'].map({'Adulto': 0, 'Idoso': 1}).mean() * 100
    }

    card_classes = ["card card-churn", "card card-cltv", "card card-retention", "card card-mensal", "card card-idosos"]
    cards = [html.Div([
        html.Div(f"{val:.1f}" + ("%" if "%" in label else ""), className="card-value"),
        html.Div(label, className="card-label")
    ], className=card_classes[i]) for i, (label, val) in enumerate(kpis.items())]

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

    payment_fig = px.bar(df2.groupby('Payment Method')['Churn Value'].mean().reset_index(),
                         x='Payment Method', y='Churn Value', title='Churn por Pagamento',
                         color='Payment Method', color_discrete_map=color_map, text='Churn Value')
    payment_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    payment_fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')

    contract_fig = px.bar(df2.groupby('Contract')['Churn Value'].mean().reset_index(),
                          x='Contract', y='Churn Value', title='Churn por Contrato',
                          color='Contract', color_discrete_map=color_map, text='Churn Value')
    contract_fig.update_layout(xaxis=dict(visible=False), **common_layout)
    contract_fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')

    df2['Phone Service'] = df2['Phone Service'].map({0: 'No', 1: 'Yes'}).fillna(df2['Phone Service'])
    df2['Internet Service'] = df2['Internet Service'].map({0: 'DSL', 1: 'Fiber optic', 2: 'No'}).fillna(df2['Internet Service'])
    df2['Online Security'] = df2['Online Security'].map({0: 'No', 1: 'Yes', 2: 'No internet service'}).fillna(df2['Online Security'])

    phone_service_fig = px.pie(df2, names='Phone Service', title='Distribuição: Serviço de Telefone',
                               color='Phone Service',
                               color_discrete_map={'Yes': '#52BC20', 'No': '#6c757d'})
    phone_service_fig.update_layout(**common_layout)

    internet_service_fig = px.pie(df2, names='Internet Service', title='Distribuição: Serviço de Internet',
                                  color='Internet Service',
                                  color_discrete_map={'DSL': '#007bff', 'Fiber optic': '#ffc107', 'No': '#6c757d'})
    internet_service_fig.update_layout(**common_layout)

    security_service_fig = px.pie(df2, names='Online Security', title='Distribuição: Segurança Online',
                                  color='Online Security',
                                  color_discrete_map={'Yes': '#17a2b8', 'No': '#6c757d', 'No internet service': '#D1CCC6'})
    security_service_fig.update_layout(**common_layout)

    map_fig = px.scatter_mapbox(df2, lat='Latitude', lon='Longitude',
                                color='CLTV', size='Monthly Charges',
                                title='Mapa de Clientes por CLTV',
                                mapbox_style='carto-positron',
                                color_continuous_scale='Viridis')
    map_fig.update_layout(**common_layout)

    return cards, churn_hist_fig, churn_hist_fig2, churn_score_fig, payment_fig, contract_fig, churn_gender_age_fig, phone_service_fig, internet_service_fig, security_service_fig, map_fig

if __name__ == '__main__':
    app.run(debug=True)
