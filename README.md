# Dashboard de Clientes e Churn

Um painel interativo para visualizar métricas e indicadores de churn (cancelamento de clientes) em um serviço fictício, construído com **Dash**, **Plotly** e **Bootstrap**.

## 📋 Conteúdo

- [Funcionalidades](#-funcionalidades)    
- [Estrutura do projeto](#-estrutura-do-projeto)  
- [Tecnologias usadas](#-tecnologias-usadas)  
- [Uso](#-uso)   
- [Licença](#-licença)  

## 🚀 Funcionalidades

- **KPI Cards** com:
  - Taxa média de churn
  - CLTV médio
  - Faturamento médio
  - Tempo médio de permanência
  - Percentual de clientes idosos
- **Filtros** interativos:
  - Tipo de contrato
  - Método de pagamento
- **Gráficos**:
  - Evolução do **Churn Score** por tempo de permanência  
  - **Churn** por método de pagamento  
  - **Churn** por tipo de contrato  
  - **Churn** por gênero e faixa etária  
  - **Indicadores** de serviços (telefone, internet, segurança)  
  - **Boxplot** de cobranças mensais por contrato  
  - **Mapa** de clientes com CLTV  

## ▶️ Como executar

1. Certifique‑se de que o CSV de dados está em `data/churn.csv`.  
2. No terminal, dentro da pasta do projeto e com o ambiente virtual ativado, execute:
   ```bash
   python app.py
   ```
3. Abra o navegador e acesse:
   ```
   http://127.0.0.1:8050
   ```

## 📁 Estrutura do projeto

```text
dashboard-churn/
├── app.py               # Script principal do Dash
├── data/
│   └── churn.csv        # Base de dados de exemplo
├── assets/              # CSS customizado
│   └── custom.css
├── requirements.txt     # Lista de pacotes Python
├── README.md            # Este arquivo
└── .gitignore
```

## 🛠 Tecnologias usadas

- [Python](https://www.python.org/)  
- [Dash](https://dash.plotly.com/)  
- [Plotly](https://plotly.com/python/)  
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)  
- [pandas](https://pandas.pydata.org/)  

## 🎯 Uso

1. Selecione o **Tipo de Contrato** e/ou **Método de Pagamento** nos filtros.  
2. Os **KPI Cards** e **gráficos** serão atualizados automaticamente.  
3. Navegue pelos gráficos para explorar os detalhes (zoom, tooltip, etc).

## 📄 Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).
