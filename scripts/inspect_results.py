import pandas as pd

df = pd.read_csv('checkpoints/llm_return_regressor/val_predictions.csv')
print("=== TOP 5 MAYORES SUBIDAS PRONOSTICADAS (LONG) ===")
for i, (_, r) in enumerate(df.sort_values(by='pred_return', ascending=False).head(5).iterrows(), 1):
    hl = str(r['headlines'])[:120].encode('ascii', 'replace').decode('ascii')
    print(f"{i}. [{r['ticker']} | {r['date']}] Precio: ${r['close_price']:.2f}")
    print(f"   Prediccion LLM : {r['pred_return']*100:+.2f}% | Retorno Real: {r['actual_return']*100:+.2f}% (Error: {r['error']*100:+.2f}%)")
    print(f"   Titular noticia: \"{hl}...\"\n")

print("=== TOP 5 MAYORES BAJADAS PRONOSTICADAS (SHORT) ===")
for i, (_, r) in enumerate(df.sort_values(by='pred_return', ascending=True).head(5).iterrows(), 1):
    hl = str(r['headlines'])[:120].encode('ascii', 'replace').decode('ascii')
    print(f"{i}. [{r['ticker']} | {r['date']}] Precio: ${r['close_price']:.2f}")
    print(f"   Prediccion LLM : {r['pred_return']*100:+.2f}% | Retorno Real: {r['actual_return']*100:+.2f}% (Error: {r['error']*100:+.2f}%)")
    print(f"   Titular noticia: \"{hl}...\"\n")
