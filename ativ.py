import pandas as pd 
import numpy as np 
import matplotlib.pyplot as mat
# Ingestão, Performance e Limpeza:

df = pd.read_csv('transacoes.csv', encoding= 'latin1')


df['valor'] = df['valor'].fillna(
    df.groupby('estado_cliente')['valor'].transform('median')
)


df['plataforma'] = 'mobile'


# Engenharia de Dados & Alinhamento Temporável:


df['data_transacao'] = pd.to_datetime(df['data_transacao'], errors='coerce')
df = df.dropna(subset=['data_transacao'])

df['data_transacao'] = df['data_transacao'].dt.tz_localize(
    'America/Sao_Paulo',
    ambiguous='NaT',
    nonexistent='shift_forward'
)
df = df.dropna(subset=['data_transacao'])

df['dia_semana'] = df['data_transacao'].dt.day_name()

df['mes'] = df['data_transacao'].dt.month


df = df.drop_duplicates(keep='first')

#Operações Vetorizadas e Filtros Bitwise:
 

condicao_mes = (df['mes'] == 9)
condicao_estado = (df['estado_cliente'] == 'SP') | (df['estado_cliente'] == 'RJ')
condicao_valor = (df['valor'] > 5000)

df_filtro = df[condicao_mes & condicao_estado & condicao_valor]

risco_dict = {
    'C100' : 'Baixo',
    'C101' : 'Alto',
    'C102' : 'Medio',
    'C103' : 'Alto',
    'C104' : 'Baixo',
    'C105' : 'Medio'
}

df['nivel_risco'] = df['id_cliente'].map(risco_dict)

tabela = df.pivot_table(
    index = 'mes',
    columns = 'nivel_risco',
    values = 'valor',
    aggfunc = 'sum',
    margins = True,
    margins_name = 'Total'
)


#Detecção Estatística de Outliers (Z-Score):


agrupar = df.groupby('estado_cliente')['valor']

df['zscore'] = (df['valor'] - agrupar.transform('mean')) / agrupar.transform('std')

df_anomalia = df[df['zscore'] > 2.5]


#Visualização Gráfica Orientada a Objetos (Matplotlib):



transacao_Dia = df.set_index ('data_transacao')['valor'].resample('D').sum()


media_movel = transacao_Dia.rolling(7).mean()



fig, ax = mat.subplots(figsize=(12,6))
ax.plot(transacao_Dia.index, transacao_Dia.values, label = 'Total Por Dia')
ax.plot(media_movel.index, media_movel.values, label = 'Média Móvel de 7 Dias',linewidth= 2  )

ax.set_ylim(bottom=0)
ax.set_title('Valor total do dia')
ax.set_xlabel('Data')
ax.set_ylabel('Valor total')
ax.legend()

fig.autofmt_xdate()
mat.show()
