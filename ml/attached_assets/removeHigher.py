import pandas as pd 

# read csv
df = pd.read_csv('./cleaned-por-data-withG12.csv', sep=',')

# remove higher column
df = df.drop(columns=['higher'])

# save as cleaned
df.to_csv('./Hcleaned-por-data-withG12.csv', sep=',', index=False)