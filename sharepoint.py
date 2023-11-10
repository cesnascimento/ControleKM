from shareplum import Site
from shareplum import Office365
import csv

# Autenticar e conectar ao SharePoint
authcookie = Office365('https://dermage.sharepoint.com',
                       username='cnascimento@dermage.com.br', password='039579X').GetCookies()
site = Site('https://dermage.sharepoint.com/sites/testekm',
            authcookie=authcookie)

# Obter dados da lista SharePoint
# Certifique-se de que 'testekm' é o nome correto da lista
sp_list = site.List('testekm')
data = sp_list.GetListItems()

# Processamento adicional para a coluna 'KMTotal' e 'Data'
for row in data:
    # Processamento para 'KMTotal'
    if 'KMTotal' in row:
        km_value = row['KMTotal']
        if km_value.startswith('float;#'):
            km_value = km_value.replace('float;#', '')
        try:
            row['KMTotal'] = "{:.2f}".format(float(km_value.replace(',', '.')))
        except ValueError:
            pass

    # Processamento para 'Data'
    if 'Data' in row and row['Data']:
        # Formatando a data para exibir apenas a data, sem a hora
        row['Data'] = row['Data'].strftime('%Y-%m-%d')

# Escrever os dados em um arquivo CSV
# Determinando automaticamente os nomes das colunas a partir dos dados
if data:
    fieldnames = data[0].keys()
    with open('sharepoint_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print("Dados salvos em sharepoint_data.csv!")
else:
    print("Nenhum dado foi encontrado na lista.")
