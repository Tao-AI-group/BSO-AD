import pandas as pd

# read Excel，without header
df = pd.read_excel("SDoH_Obpro_datapro_Literature_Ob_20250907.xlsx")

# outpout TXT
df.to_csv("SDoH_Obpro_datapro_Literature_Ob_20250907.tsv", sep="\t", index=False, encoding="utf-8")


