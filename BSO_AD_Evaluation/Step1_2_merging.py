import pandas as pd

df1 = pd.read_csv("./version2/screening/Llama4_results-07312025.csv")
df2 = pd.read_csv("./version2/screening/Qwen3_results-07312025.csv")

df1_prefixed = df1.rename(columns={col: f"Llama4_{col}" for col in df1.columns if col != 'PMID'})
df2_prefixed = df2.rename(columns={col: f"Qwen3_{col}" for col in df2.columns if col != 'PMID'})

# Merge on 'PMID'
merged_df = pd.merge(df1_prefixed, df2_prefixed, on='PMID', how='outer')

# Reorder to have PMID first
cols = ['PMID'] + [col for col in merged_df.columns if col != 'PMID']
merged_df = merged_df[cols]

# Define LLM-specific columns
llm1_prefix = 'Llama4'
llm2_prefix = 'Qwen3'

# Columns to check
decision_cols = ['ADRD_focus', 'behavior_social_focus', 'human_study', 'include']

# Function to create condition for each LLM
def all_true_condition(df, prefix):
    return (
        (df[f'{prefix}_ADRD_focus'] == True) &
        (df[f'{prefix}_behavior_social_focus'] == True) &
        (df[f'{prefix}_human_study'] == True) &
        (df[f'{prefix}_include'].isin([True, 'Yes']))
    )

# Apply condition for both LLMs
llm1_all_true = all_true_condition(merged_df, llm1_prefix)
merged_df["Llama4_final"] = llm1_all_true
llm2_all_true = all_true_condition(merged_df, llm2_prefix)
merged_df["Qwen3_final"] = llm2_all_true

merged_df.to_csv("./version2/screening/LLM-merged.csv",index=False)

filtered = merged_df.dropna(subset=["Qwen3_final", "Llama4_final"])

# Now safely filter for rows where both are True
common = filtered[filtered["Qwen3_final"] & filtered["Llama4_final"]]


lit_filtered = pd.read_excel("./version2/screening/lit-filtered-0728.xlsx")
lit_df = lit_filtered[lit_filtered['PMID'].isin(common['PMID'])]
selected = common[["PMID","Title","Abstract"]]
selected.to_excel("./version2/screening/included_articles-08062025.xlsx")

