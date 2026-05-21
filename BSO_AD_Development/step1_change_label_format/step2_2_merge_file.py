import pandas as pd

file1 = "TEO_labels_template.tsv"  # 有表头
file2 = "TEO_labels_nonclass_template.tsv"    # 无表头
out   = "TEO_labels_merged_template.tsv"

# 读第一个文件（带表头）
df1 = pd.read_csv(file1, sep="\t", dtype=str)

# 用第一个文件的列名，读取第二个文件（无表头）
df2 = pd.read_csv(file2, sep="\t", header=None, names=df1.columns, dtype=str)

# 合并
merged = pd.concat([df1, df2], ignore_index=True)

# 如需按第一列（ID）去重（可选）
# merged = merged.drop_duplicates(subset=df1.columns[0], keep="first")

# 保存
merged.to_csv(out, sep="\t", index=False)
print(f"Saved: {out} ({len(merged)} rows)")
