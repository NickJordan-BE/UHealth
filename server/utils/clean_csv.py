import pandas as pd

CSV_PATH = "Data_Entry_2017_v2020.csv"
OUTPUT_CSV = "4999.csv"
MAX_ROWS = 4999

df = pd.read_csv(CSV_PATH)

df_truncated = df.iloc[:MAX_ROWS]

df_truncated.to_csv(OUTPUT_CSV, index=False)

print(f"Truncated CSV saved to: {OUTPUT_CSV}")
print(f"Original rows: {len(df)}, Remaining rows: {len(df_truncated)}")
