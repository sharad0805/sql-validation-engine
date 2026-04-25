from src.db_connector import get_table

df = get_table("employees")
print(df)
print(f"\nShape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")