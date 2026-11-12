import pandas as pd

url = 'https://huggingface.co/datasets/ic-fspml/stock_news_sentiment/resolve/main/data/train-00000-of-00001-161ce92db66dabb3.parquet'
df = pd.read_parquet(url)

print("Date range:", df['article_date'].min(), "to", df['article_date'].max())
print("Total rows:", len(df))

for t in ['NVDA', 'AAPL', 'TSLA', 'AMZN', 'GOOG', 'MSFT']:
    sub = df[df['ticker'] == t]
    if not sub.empty:
        print(f"  {t}: {len(sub)} news | {sub['article_date'].min()} to {sub['article_date'].max()}")
    else:
        print(f"  {t}: NOT FOUND")
