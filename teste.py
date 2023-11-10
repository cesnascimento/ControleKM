import streamlit as st
import pandas as pd
import plotly.express as px
import json
from io import StringIO

# Função para carregar e limpar os dados


@st.cache_data
def load_data():
    # Caminho atualizado para o novo arquivo CSV
    path = 'sharepoint_data.csv'
    df = pd.read_csv(path)

    # Remova ou ajuste esta seção se a coluna 'Criado por' em seu novo CSV não estiver em formato JSON
    def extract_display_name(s):
        try:
            data = json.loads(s.replace("'", '"'))
            return data['DisplayName']
        except:
            return s

    df['Criado por'] = df['Criado por'].apply(extract_display_name)

    # Certifique-se de que as colunas no CSV correspondem a estas
    df['Data'] = pd.to_datetime(df['Data'])

    return df


# Carregar dados
df = load_data()

# Título
st.title('Painel de Quilometragem')

# Seleção de usuário
lista_usuarios = ['Todos'] + df['Criado por'].unique().tolist()
usuario_selecionado = st.selectbox('Escolha um usuário:', lista_usuarios)

# Seleção de intervalo de datas
data_inicial, data_final = st.date_input('Escolha um intervalo de datas:', [
                                         df['Data'].min().date(), df['Data'].max().date()])

# Convertendo objetos date para Timestamp para comparação
data_inicial = pd.Timestamp(data_inicial)
data_final = pd.Timestamp(data_final)

# Filtrar dados
df_filtrado = df[(df['Data'] >= data_inicial)
                 & (df['Data'] <= data_final)]

if usuario_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Criado por'] == usuario_selecionado]

# Gráficos
if not df_filtrado.empty:
    titulo = f'Total de Quilometragem entre {data_inicial.date()} e {data_final.date()}'

    if usuario_selecionado == 'Todos':
        totais_usuarios = df_filtrado.groupby('Criado por')['KMTotal'].sum()
        fig = px.bar(totais_usuarios.reset_index(), x='Criado por', y='KMTotal', text='KMTotal', title=f"{titulo} - Totais Individuais de Quilometragem",
                     labels={'KMTotal': 'Quilometragem Total', 'Criado por': 'Usuário'})
        st.plotly_chart(fig)

        st.subheader("Totais de Todos os Usuários:")
        total_todos_usuarios = totais_usuarios.sum()
        st.write(
            f"Total de Quilometragem de Todos os Usuários: {total_todos_usuarios:.2f}")

        st.subheader("Totais Individuais de Quilometragem:")
        for user, total in totais_usuarios.items():
            st.write(f"{user}: {total:.2f}")

    else:
        user_df = df_filtrado[df_filtrado['Criado por'] == usuario_selecionado]
        fig = px.bar(user_df, x='Data', y='KMTotal', text='KMTotal', title=f"{titulo} para {usuario_selecionado} - Quilometragem Diária",
                     labels={'KMTotal': 'Quilometragem Total', 'Data': 'Data'})
        st.plotly_chart(fig)
        total_usuario = user_df['KMTotal'].sum()
        st.write(
            f"Total percorrido por {usuario_selecionado}: {total_usuario:.2f}")

    # Adicionando opção para exportar dados para CSV
    csv_buffer = StringIO()
    df_filtrado.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()
    st.download_button(
        label="Baixar dados como CSV",
        data=csv_str,
        file_name="dados_filtrados.csv",
        mime="text/csv",
    )

else:
    st.write("Nenhum dado disponível para a seleção atual.")
