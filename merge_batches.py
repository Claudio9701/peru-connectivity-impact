import pandas as pd
from pathlib import Path

dfs = [pd.read_csv(fs, index_col=0) for fs in Path('outputs/').iterdir() if fs.name.startswith('geocoded_df')]

# Concatenate and double check index integrity (i.e. no duplicates)
geocoded_concatenate = pd.concat(dfs)

print(geocoded_concatenate.index.duplicated().sum())
print(geocoded_concatenate.shape)

df_main = pd.read_csv('outputs/geocode_with_nominatim.csv', index_col=0)

print(df_main.head())
print(df_main.shape)

geocoded_df_orig_index = geocoded_concatenate.set_index(df_main.index)
print(geocoded_df_orig_index.shape)
print(geocoded_df_orig_index['lat'].isna().value_counts())
print(geocoded_df_orig_index['lat'].notna().sum())
geocoded_df_orig_index_clean = geocoded_df_orig_index[geocoded_df_orig_index['lat'].notna().values]
print(geocoded_df_orig_index_clean.shape)
geocoded_df_orig_index_clean.to_csv(f'outputs/geocoded_df_all_batches.csv')




