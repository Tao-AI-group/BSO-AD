import pandas as pd

# 读取 Excel，没有表头
df = pd.read_excel("add_class.xlsx", header=None)

# 导出 TXT，不要输出列名
df.to_csv("add_class.txt", sep="\t", index=False, header=False)