import pandas as pd

# Read the Excel file without a header row
df = pd.read_excel("add_class.xlsx", header=None)

# Export as a tab-separated TXT file without column names or index
df.to_csv("add_class.txt", sep="\t", index=False, header=False)