from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import time
import os
# Start Chrome in background
options=webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver=webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options)
# Open CoinMarketCap
driver.get("https://coinmarketcap.com/")
time.sleep(5)
rows=driver.find_elements(By.CSS_SELECTOR,"table tbody tr")
crypto_data=[]
# Extract top 10 coins
for row in rows:
    if len(crypto_data)>=10:
        break
    try:
        columns=row.find_elements(By.TAG_NAME,"td")
        if len(columns)<8:
            continue
        name=columns[2].text.split("\n")[0].strip()
        if "Index" in name:
            continue
        crypto_data.append({
            "Coin Name":name,
            "Price":columns[3].text,
            "24h Change":columns[4].text,
            "Market Cap":columns[7].text,
            "Timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print("Error:",e)
driver.quit()
# Create DataFrame
df=pd.DataFrame(crypto_data)
print("\nCryptocurrency Data:\n")
print(df)
# Save data
file_name="crypto_data.csv"
df.to_csv(file_name,mode="a",
          header=not os.path.exists(file_name),index=False)
#1.Filter
df["Price_Num"]=pd.to_numeric(
    df["Price"].str.replace("$","").str.replace(",",""),
    errors="coerce")
df["Change_Num"]=pd.to_numeric(
    df["24h Change"].str.replace("%",""),
    errors="coerce")
filtered=df[
    (df["Price_Num"]>=100) |
    (df["Change_Num"]>=0.10)
]
print("\nFiltered Coins:\n")
print(filtered[["Coin Name","Price","24h Change"]])
# 2.HISTORICAL DATA
history_file="crypto_history.csv"

df.to_csv(
    history_file,
    mode="a",
    header=not os.path.exists(history_file),
    index=False)
#3.Trend analysis
history=pd.read_csv(history_file)
history["Coin Name"]=(
    history["Coin Name"]
    .astype(str)
    .str.split("\n")
    .str[0]
    .str.strip())
history["Price_Num"]=pd.to_numeric(
    history["Price"]
    .astype(str)
    .str.replace("$","")
    .str.replace(",",""),
    errors="coerce")
trend=history.groupby("Coin Name")["Price_Num"].agg(
    ["mean","max","min"]).round(2)
print("\nTrend Analysis:\n")
print(trend)
# 4.Dashboard
trend.to_csv("crypto_dashboard.csv")
print("\nDashboard data saved!")
#5.Portfolio
portfolio={
    "Bitcoin":0.01,
    "Ethereum":0.5,
    "BNB":1}
total=0
for coin,quantity in portfolio.items():
    price=df.loc[
        df["Coin Name"].str.lower()==coin.lower(),
        "Price_Num"
    ]
    if not price.empty:
        total+=price.iloc[0]*quantity
print("\nPortfolio Value: $",round(total,2))
print("\nProject Completed!")