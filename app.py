import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

# ===================== DADOS =====================
df = pd.read_csv('data/churn.csv')
df.columns = df.columns.str.strip()

# Se a sua coluna 'Contract' vier como 0,1,2, mapeia pra string:
contract_map = {
    0: 'Month-to-month',
    1: 'One year',
    2: 'Two year'
}
if df['Contract'].dtype != object:
    df['Contract'] = df['Contract'].map(contract_map)

# Se a sua coluna 'Payment Method' vier como código 0–3, mapeia também:
payment_map = {
    0: 'Electronic check',
    1: 'Mailed check',
    2: 'Bank transfer (automatic)',
    3: 'Credit card (automatic)'
}
if df['Payment Method'].dtype != object:
    df['Payment Method'] = df['Payment Method'].map(payment_map)

# ===================== APP =====================
contract_options = ['Month-to-month', 'One year', 'Two year']
payment_options = [
    'Electronic check',
    'Mailed check',
    'Bank transfer (automatic)',
    'Credit card (automatic)'
]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets'
)
server = app.server

# ===================== LAYOUT =====================
app.layout = dbc.Container(fluid=True, className="p-4", children=[

    # Título
    dbc.Row(
        dbc.Col(
            html.H1("Dashboard de Clientes e Churn",
                    className="text-center fw-bold mb-4"),
            width=16
        )
    ),

    # KPI cards
    dbc.Row(
        dbc.Col(html.Div(id='kpi-cards', className='d-flex flex-wrap gap-2'),
                width=12),
        className="mb-3"
    ),

    # Filtros lado a lado
    dbc.Row(
        className='mb-4 gx-3 gy-1',
        align='center',
        children=[
            dbc.Col([
                html.Label("Tipo de Contrato",
                           className="form-label small mb-1"),
                dcc.Dropdown(
                    id='contract-filter',
                    options=[{'label': opt, 'value': opt}
                             for opt in contract_options],
                    placeholder="Selecione contrato",
                    clearable=True,
                    className='form-select form-select-sm'
                )
            ], width=6),
            dbc.Col([
                html.Label("Método de Pagamento",
                           className="form-label small mb-1"),
                dcc.Dropdown(
                    id='payment-filter',
                    options=[{'label': opt, 'value': opt}
                             for opt in payment_options],
                    placeholder="Selecione pagamento",
                    clearable=True,
                    className='form-select form-select-sm'
                )
            ], width=6),
        ]
    ),

    # Gráficos
    dbc.Row(
        dbc.Col(dcc.Graph(id='churn-score-time',
                          style={'height': '300px'}), width=12),
        className="mb-4"
    ),
    dbc.Row([
        dbc.Col(dcc.Graph(id='churn-by-payment',
                          style={'height': '450px'}), width=6),
        dbc.Col(dcc.Graph(id='churn-by-contract',
                          style={'height': '450px'}), width=6),
    ], className="mb-4"),
    dbc.Row(
        dbc.Col(dcc.Graph(id='churn-gender-senior',
                          style={'height': '450px'}), width=12),
        className="mb-5"
    ),
    dbc.Row([
        dbc.Col(dcc.Graph(id='indicator-phone',
                          style={'height': '350px'}), width=4),
        dbc.Col(dcc.Graph(id='indicator-internet',
                          style={'height': '350px'}), width=4),
        dbc.Col(dcc.Graph(id='indicator-security',
                          style={'height': '350px'}), width=4),
    ], className="mb-5"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='churn-by-gender',
                          style={'height': '450px'}), width=6),
        dbc.Col(dcc.Graph(id='boxplot-charges',
                          style={'height': '450px'}), width=6),
    ], className="mb-4"),
    dbc.Row(
        dbc.Col(dcc.Graph(id='cltv-map',
                          style={'height': '600px'}), width=12),
        className="mb-5"
    ),
])

# ===================== CALLBACK =====================
@app.callback(
    Output('kpi-cards', 'children'),
    Output('churn-score-time', 'figure'),
    Output('churn-by-payment', 'figure'),
    Output('churn-by-contract', 'figure'),
    Output('churn-gender-senior', 'figure'),
    Output('indicator-phone', 'figure'),
    Output('indicator-internet', 'figure'),
    Output('indicator-security', 'figure'),
    Output('churn-by-gender', 'figure'),
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

    # Se ficou vazio após o filtro, evita nan no cálculo:
    if df2.empty:
        # retorna cards “0” e figuras vazias
        empty_fig = px.scatter()  # gráfico em branco
        cards = [
            html.Div("0", className="card-value") for _ in range(5)
        ]
        return [html.Div([
            html.Div("0", className="card-value"),
            html.Div(label, className="card-label")
        ], className=f"card {cls}") for label, cls in zip(
            ["Taxa de Churn (%)", "CLTV Médio (R$)", "Faturamento Médio (R$)",
             "Tempo Médio (meses)", "% de Idosos"],
            ["card-purple", "card-blue", "card-red", "card-orange", "card-green"]
        )], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # KPI cards
    kpis = {
        "Taxa de Churn (%)": df2['Churn Value'].mean() * 100,
        "CLTV Médio (R$)": df2['CLTV'].mean(),
        "Faturamento Médio (R$)": df2['Monthly Charges'].mean(),
        "Tempo Médio (meses)": df2['Tenure Months'].mean(),
        "% de Idosos": df2['Senior Citizen'].mean() * 100
    }
    card_classes = ["card-purple", "card-blue",
                    "card-red", "card-orange", "card-green"]
    cards = []
    for i, (label, val) in enumerate(kpis.items()):
        txt = f"{val:.1f}" + ("%" if "%" in label else "")
        cards.append(
            html.Div([
                html.Div(txt, className="card-value"),
                html.Div(label, className="card-label")
            ], className=f"card {card_classes[i]}")
        )

    # --- Gráficos com labels descritivos ---

    color_map = {
        'Electronic check': '#31CB00',
        'Mailed check': '#119822',
        'Bank transfer (automatic)': '#2A7221',
        'Credit card (automatic)': '#1E441E',

        'Month-to-month': '#31CB00',
        'One year': '#119822',
        'Two year': '#2A7221',

        'Adulto': '#31CB00',
        'Idoso': '#119822'
    }

    churn_score_fig = px.line(
        df2.groupby('Tenure Months')['Churn Score'].mean().reset_index(),
        x='Tenure Months', y='Churn Score',
        title='Churn Score por Tempo de Permanência',
        labels={
            'Tenure Months': 'Meses de Permanência',
            'Churn Score': 'Score de Churn'
        },
        template='plotly_white'
    )
    churn_score_fig.update_traces(line_color='#119822')

    # Gráfico de churn por método de pagamento
    pay_df = df2.groupby('Payment Method')['Churn Value'].mean().reset_index()
    payment_fig = px.bar(
        pay_df,
        x='Payment Method',
        y='Churn Value',
        text_auto='.1%',
        color='Payment Method',
        color_discrete_map = color_map,
        title='Churn por Método de Pagamento',
        labels={
            'Payment Method': 'Método de Pagamento',
            'Churn Value': 'Churn (%)'
        },
        category_orders={'Payment Method': payment_options},
        template='plotly_white'
    )
    payment_fig.update_traces(textposition='outside')
    payment_fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickvals=[],
        xaxis_ticktext=[],
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        showlegend=True
    )

    # Gráfico de churn por tipo de contrato
    contr_df = df2.groupby('Contract')['Churn Value'].mean().reset_index()
    contract_fig = px.bar(
        contr_df,
        x='Contract',
        y='Churn Value',
        text_auto='.1%',
        color='Contract',
        color_discrete_map = color_map,
        color_discrete_sequence=px.colors.qualitative.Plotly,
        title='Churn por Tipo de Contrato',
        labels = {'Contract': 'Tipo de Contrato'},
        category_orders={'Contract': contract_options},
        template='plotly_white'
    )
    contract_fig.update_traces(textposition='outside')
    contract_fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickvals=[],
        xaxis_ticktext=[],
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        showlegend=True
    )


    gender_senior_fig = px.bar(
        df2.groupby(['Gender', 'Senior Citizen'])['Churn Value'].mean().reset_index()
           .assign(**{'Senior Citizen': lambda d: d['Senior Citizen'].map({0: 'Adulto', 1: 'Idoso'})}),
        x='Gender', y='Churn Value', color='Senior Citizen', barmode='group',
        color_discrete_map = color_map,
        title='Churn por Gênero e Idade',
        labels={
            'Gender': 'Gênero',
            'Churn Value': 'Churn (%)',
            'Senior Citizen': 'Faixa Etária'
        },
        template='plotly_white'
    )
    gender_senior_fig.update_layout(
    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    showlegend=True
    )
    gender_senior_fig.update_traces(texttemplate='%{y:.1%}', textposition='outside')

    ind_phone = px.pie(df2, names='Phone Service', hole=0.5,
                       title='Serviço de Telefone', template='plotly_white')
    ind_internet = px.pie(df2, names='Internet Service', hole=0.5,
                          title='Serviço de Internet', template='plotly_white')
    ind_security = px.pie(df2, names='Online Security', hole=0.5,
                          title='Segurança Online', template='plotly_white')

    churn_by_gender_fig = px.bar(
        df2.groupby('Gender')['Churn Value'].mean().reset_index(),
        x='Gender', y='Churn Value',
        title='Churn por Gênero',
        text_auto='.1%',
        labels={
            'Gender': 'Gênero',
            'Churn Value': 'Churn (%)'
        },
        template='plotly_white'
    )
    churn_by_gender_fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickvals=[],
        xaxis_ticktext=[],
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        showlegend=True
    )

    boxplot_fig = px.box(
        df2, x='Monthly Charges', y='Contract',
        points='all', orientation='h',
        title='Cobrança Mensal (R$) por Tipo de Contrato',
        labels={
            'Monthly Charges': 'Cobrança Mensal (R$)',
            'Contract': 'Tipo de Contrato'
        },
        category_orders={'Contract': contract_options},
        template='plotly_white'
    )

    map_fig = px.scatter_map(
        df2, lat='Latitude', lon='Longitude',
        color='CLTV', size='Monthly Charges',
        title='Mapa de Clientes por CLTV',
        labels={'Latitude': 'Latitude', 'Longitude': 'Longitude'},
        map_style='carto-positron',
        template='plotly_white'
    )

    return (
        cards,
        churn_score_fig,
        payment_fig,
        contract_fig,
        gender_senior_fig,
        ind_phone,
        ind_internet,
        ind_security,
        churn_by_gender_fig,
        boxplot_fig,
        map_fig
    )

if __name__ == '__main__':
    app.run(debug=True)
