# 🗃️ Customer Dashboard and Churn Analysis

An interactive dashboard to visualize customer churn metrics and indicators for a fictional service, built using **Dash**, **Plotly**, and **Bootstrap**.

https://github.com/user-attachments/assets/9143b0da-534c-44e6-a30c-43586eed0432

### 🚀 Features

- **KPI Cards** with:
  - Average churn rate  
  - Average CLTV (Customer Lifetime Value)  
  - Average revenue  
  - Average tenure  
  - Percentage of senior customers  
- **Interactive Filters**:
  - Contract type  
  - Payment method  
- **Charts**:
  - Churn Score trend by tenure  
  - Churn by payment method  
  - Churn by contract type  
  - Churn by gender and age group  
  - Service indicators (phone, internet, security)  
  - Customer map with CLTV  

### ▶️ How to Run

1. Make sure the CSV file is located at `data/churn.csv`.  
2. In the terminal, navigate to the project folder and activate the virtual environment, then run:
   ```bash
   python app.py
3. Open your browser and go to:
   ```bash
   http://127.0.0.1:8050

### 📁 Project Structure

```
dashboard-churn/
├── app.py               # Main Dash script
├── data/
│   └── churn.csv        # Sample dataset
├── assets/              # Custom CSS
│   └── custom.css
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .gitignore
```

### 🛠 Technologies Used

- [x] Python
- [X] Dash
- [X] Plotly
- [X] Dash Bootstrap Components
- [X] pandas

### 🎯 Usage

- Select the Contract Type and/or Payment Method using the filters.
- The KPI Cards and charts will update automatically.
- Explore the charts using zoom, tooltips, and other interactive features.

```py
- # Authors Info

# Cleydson de Souza, csfj@academico.ufpb.br
# Davi Nasiasene Amorim, davi.nasiasene@academico.ufpb.br
# Mariana Martins, marianamartiyns@gmail.com
# Thiago Rodrigues, thiago.rodrigues@academico.ufpb.br
```

<img align="right" width ='40px' src ='https://img.icons8.com/?size=100&id=lOqoeP2Zy02f&format=png&color=000000'> </a>
<img align="right" width ='40px' src ='https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg'> </a>
