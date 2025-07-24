import pandas as pd

file_path = 'đo-lần-1-thang-máy.csv'
df = pd.read_csv(file_path)

df['Y Position'] = -abs(df['Y Position'])

output_path = 'đo-lần-1-thang-máy-updated.csv'
df.to_csv(output_path, index=False)

