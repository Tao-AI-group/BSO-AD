import pandas as pd

file1 = "./step1_outputs/TEO_labels_template.tsv"   # File with header
file2 = "./step1_outputs/TEO_labels_nonclass_template.tsv"    # File without header
out   = "./step1_outputs/TEO_labels_merged_template.tsv"

# Read the first TSV file (with header)
df1 = pd.read_csv(file1, sep="\t", dtype=str)

# Read the second TSV file (without header)
# Assign column names based on the first file
df2 = pd.read_csv(file2, sep="\t", header=None, names=df1.columns, dtype=str)

# Merge the two dataframes
merged = pd.concat([df1, df2], ignore_index=True)

# Optional: remove duplicate rows based on the first column (e.g., ID)
# merged = merged.drop_duplicates(subset=df1.columns[0], keep="first")

# Save the merged dataframe as a TSV file
merged.to_csv(out, sep="\t", index=False)
print(f"Saved: {out} ({len(merged)} rows)")
