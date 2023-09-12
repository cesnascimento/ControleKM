import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# Função para carregar e limpar os dados
@st.cache_data  # Usando st.cache_data em vez de st.cache, conforme as novas práticas recomendadas
def load_data():
    df = pd.read_csv('testekm.csv')
    df['Criado'] = pd.to_datetime(df['Criado'], format='%d/%m/%Y %H:%M')
    df['Modificado'] = pd.to_datetime(df['Modificado'], format='%d/%m/%Y %H:%M')
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df['KMFinal'] = df['KMFinal'].str.replace(',', '.').astype(float)
    df['KMInicial'] = df['KMInicial'].str.replace(',', '.').astype(float)
    df['KMTotal'] = df['KMTotal'].str.replace(',', '.').astype(float)
    return df

# Carregar dados
df = load_data()

# Título
st.title('Dashboard de Quilometragem')

# Seleção de usuário
user_list = ['Todos'] + df['Criado por'].unique().tolist()
selected_user = st.selectbox('Escolha um usuário:', user_list)

# Seleção de intervalo de datas
start_date, end_date = st.date_input('Escolha um intervalo de datas:', [df['Data'].min().date(), df['Data'].max().date()])

# Convertendo objetos date para Timestamp para comparação
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Filtrar dados
filtered_df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]

if selected_user != 'Todos':
    filtered_df = filtered_df[filtered_df['Criado por'] == selected_user]

# Gráficos
if not filtered_df.empty:
    title = f'Total de Quilometragem entre {start_date.date()} e {end_date.date()}'
    
    if selected_user == 'Todos':
        user_totals = filtered_df.groupby('Criado por')['KMTotal'].sum()
        
        fig = px.bar(user_totals.reset_index(), x='Criado por', y='KMTotal', title=f"{title} - Totais Individuais de Quilometragem",
                     labels={'KMTotal': 'Quilometragem Total', 'Criado por': 'Usuário'})
        
        st.plotly_chart(fig)
        
        st.subheader("Totais de Todos os Usuários:")
        total_todos_usuarios = user_totals.sum()
        st.write(f"Total de Quilometragem de Todos os Usuários: {total_todos_usuarios:.2f}")
        
        st.subheader("Totais Individuais de Quilometragem:")
        for user, total in user_totals.items():
            st.write(f"{user}: {total:.2f}")
        
        
    else:
        user_df = filtered_df[filtered_df['Criado por'] == selected_user]
        fig = px.bar(user_df, x='Data', y='KMTotal', title=f"{title} para {selected_user} - Quilometragem Diária",
                     labels={'KMTotal': 'Quilometragem Total', 'Data': 'Data'})
        
        total_user = user_df['KMTotal'].sum()
        st.write(f"Total percorrido por {selected_user}: {total_user:.2f}")
    
        st.plotly_chart(fig)
    
    # Adicionando opção para exportar dados para CSV
    csv_buffer = StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()
    st.download_button(
        label="Baixar dados como CSV",
        data=csv_str,
        file_name="dados_filtrados.csv",
        mime="text/csv",
    )

else:
    st.write("Nenhum dado disponível para a seleção atual.")
