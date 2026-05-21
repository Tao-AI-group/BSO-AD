import pandas as pd

# 读取 Excel，没有表头
df = pd.read_excel("SDoH_Obpro_datapro_Literature_Ob_20250907.xlsx")

# 导出 TXT，不要输出列名
df.to_csv("SDoH_Obpro_datapro_Literature_Ob_20250907.tsv", sep="\t", index=False, encoding="utf-8")


