import pandas as pd
from pathlib import Path

geocoded_df = pd.concat([pd.read_csv(fs, index_col=0) for fs in Path('outputs/').iterdir() if fs.name.startswith('geocoded_df') and fs.name.endswith('.csv')])
df_main = pd.read_csv('outputs/df_not_geocoded_final.csv', index_col=0)

print('dfs shapes')
print('gecocded_df:', geocoded_concatenate.shape)
print('main_df:', df_main.shape)

geocoded_df_orig_index = geocoded_concatenate.set_index(df_main.index)
print('Geocoded')
print(geocoded_df_orig_index['lat'].notna().sum())
print(round((geocoded_df_orig_index['lat'].notna().sum() / geocoded_df_orig_index.shape[0]) * 100, 2), '%')
geocoded_df_orig_index_clean = geocoded_df_orig_index[geocoded_df_orig_index['lat'].notna().values]
s
geocoded_df_orig_index_clean.to_csv(f'outputs/geocoded_df_all_batches.csv')
