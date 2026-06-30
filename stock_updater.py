from notion_client import Client
import yfinance as yf
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

def rich_text(value):
    return {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": str(value) if value else ""
                }
            }
        ]
    }
def get_naver_price(code):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = (
        f"https://polling.finance.naver.com/api/realtime"
        f"?query=SERVICE_ITEM:{code}"
    )

    data = requests.get(
        url,
        headers=headers,
        timeout=10
    ).json()

    item = data["result"]["areas"][0]["datas"][0]

    return {
        "price": item["nv"],
        "change": item["cv"],
        "rate": item["cr"]
    }

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_PRICE_DB_ID"]

notion = Client(auth=NOTION_TOKEN)

def update_stock_prices():

    # 데이터베이스 조회
    response = notion.databases.query(database_id=DATABASE_ID)

    for page in response["results"]:

        props = page["properties"]

        ticker_data = props["티커"]["rich_text"]

        if len(ticker_data) == 0:
            print("티커가 비어있어 건너뜀")
            continue

        ticker = ticker_data[0]["plain_text"]

        try:
            # 국내 주식 여부
            if ticker.isdigit():

                price_info = get_naver_price(ticker)

                current_price = price_info["price"]
                change = price_info["change"]

                stock = yf.Ticker(f"{ticker}.KS")
                print(item)
                print("\n\n")
                print(item.keys())
                
            else:

                stock = yf.Ticker(ticker)

                hist = stock.history(period="5d")

                current_price = float(hist["Close"].iloc[-1])
                previous_price = float(hist["Close"].iloc[-2])

                change = current_price - previous_price

            
            info = stock.info
            market_cap = info.get("marketCap", 0)
            if market_cap is None:
                market_cap = 0

            high_52 = info.get("fiftyTwoWeekHigh")
            low_52 = info.get("fiftyTwoWeekLow")

            currency = info.get("currency")
            country = info.get("country")
            sector = info.get("sector")
            industry = info.get("industry")

            update_time = datetime.now(
                ZoneInfo("Asia/Seoul")
            ).strftime("%Y-%m-%d %H:%M")

            properties = {
                "현재가_깃허브_원본": {
                    "number": current_price
                },
                "전일대비_깃허브": {
                    "number": change
                },
                "시가총액_깃허브": {
                    "number": market_cap
                },
                "52주 최고가": {
                    "number": high_52
                },
                "52주 최저가": {
                    "number": low_52
                },
                "통화": rich_text(currency),
                "국가": rich_text(country),
                "업종": rich_text(sector),
                "산업": rich_text(industry),
                "마지막 업데이트": rich_text(update_time)
            }

            notion.pages.update(
                page_id=page["id"],
                properties=properties
            )

            print(
                f"✅ {ticker} | 현재가: {current_price:,.0f} "
                f"전일대비: {change:+,.0f}"
            )

        except Exception as e:
            print(f"❌ {ticker} 오류: {e}")


if __name__ == "__main__":
    update_stock_prices()
