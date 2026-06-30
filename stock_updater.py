from notion_client import Client
import yfinance as yf
import os
from datetime import datetime
from zoneinfo import ZoneInfo

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

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_PRICE_DB_ID"]

notion = Client(auth=NOTION_TOKEN)

def update_stock_prices():

    # 데이터베이스 조회
    response = notion.databases.query(database_id=DATABASE_ID)

    for page in response["results"]:

        props = page["properties"]

        ticker_data = props["현재가 DB_티커"]["rich_text"]

        if len(ticker_data) == 0:
            print("티커가 비어있어 건너뜀")
            continue

        ticker = ticker_data[0]["plain_text"]

        try:
            stock = yf.Ticker(ticker)

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

            hist = stock.history(period="5d")

            if len(hist) < 2:
                print(f"{ticker}: 데이터 부족")
                continue

            current_price = float(hist["Close"].iloc[-1])
            previous_price = float(hist["Close"].iloc[-2])

            change = current_price - previous_price

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
