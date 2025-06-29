import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Aktienliste (Beispiel)
selected_stocks = ['NVDA', 'SHOP', 'UBER']

# Backtest-Zeitraum
start_date = "2022-01-01"
end_date = "2023-12-31"

# Ergebnisse speichern
results = []

# Plot-Vorbereitung
fig, axes = plt.subplots(len(selected_stocks), 1, figsize=(12, 5 * len(selected_stocks)))

# Für jede Aktie einzeln backtesten
for idx, symbol in enumerate(selected_stocks):
    data = yf.download(symbol, start=start_date, end=end_date)
    if data.empty:
        print(f"Daten für {symbol} konnten nicht geladen werden.")
        continue

    # SMA und EMA berechnen
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['EMA_10'] = data['Close'].ewm(span=10, adjust=False).mean()

    # Initialwerte
    position = False
    buy_price = 0
    balance = 100
    shares = 0
    trades = []

    # Durchlauf durch Kursdaten
    for i in range(1, len(data)):
        try:
            price = float(data['Close'].iloc[i])
            sma = float(data['SMA_20'].iloc[i])
            ema = float(data['EMA_10'].iloc[i])
        except (TypeError, ValueError):
            continue  # überspringt Zeilen mit ungültigen Werten (z. B. NaN)

        # Kaufbedingung
        if not position and price < sma and price < ema:
            shares = balance // price
            if shares == 0:
                continue
            buy_price = price
            balance -= shares * buy_price
            position = True
            trades.append(('BUY', data.index[i], price))

        # Verkaufbedingung
        elif position and price > sma and price > ema:
            balance += shares * price
            position = False
            trades.append(('SELL', data.index[i], price))

    # Letzter Verkauf falls offen
    if position:
        balance += shares * float(data['Close'].iloc[-1])

    results.append({
        'Symbol': symbol,
        'Endkapital': round(balance, 2),
        'Anzahl Trades': len(trades),
        'Trades': trades
    })

    # Plot
    ax = axes[idx] if len(selected_stocks) > 1 else axes
    ax.plot(data['Close'], label='Kurs')
    ax.plot(data['SMA_20'], label='SMA 20')
    ax.plot(data['EMA_10'], label='EMA 10')
    for action, date, price in trades:
        color = 'green' if action == 'BUY' else 'red'
        ax.scatter(date, price, color=color, label=action)
    ax.set_title(f'{symbol} SMA/EMA Backtest')
    ax.legend()
    ax.grid()

plt.tight_layout()
plt.savefig("multi_aktien_backtest.png")  # speichert in aktuellem Ordner

# Ergebnisse als CSV
results_df = pd.DataFrame(results)
results_df.to_csv("backtest_ergebnisse.csv", index=False)
