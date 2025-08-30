import pandas as pd
import numpy as np

csv_input= 'test.csv'
csv_output= 'output.csv'

df = pd.read_csv(csv_input, sep=',')
print(df.head(5))

# fill mean value depand on other two in G1 and G2 and G3 if 0, 
grades = ['G1', 'G2', 'G3']
df[grades] = df[grades].replace(0, np.nan)
def fill_grades(row):
    vals = row[grades].values.astype(float)
    for i in range(3):
        if np.isnan(vals[i]):
            others = [vals[j] for j in range(3) if j != i and not np.isnan(vals[j])]
            if others:
                vals[i] = np.floor(np.mean(others))
            else:
                vals[i] = 0  # fallback if all are NaN
    row[grades] = vals
    return row

df = df.apply(fill_grades, axis=1)

# save as csv

df.to_csv(csv_output, sep=',', index=False)