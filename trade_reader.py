from notion_client import Client
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
TRADE_DB_ID = os.environ["NOTION_TRADE_DB_ID"]

notion = Client(auth=NOTION_TOKEN)


def read_trade_db():

    response = notion.databases.query(
        database_id=TRADE_DB_ID
    )

    trades = []

    for page in response["results"]:

        props = page["properties"]

        trade = {

            "page_id": page["id"],

            # 관계형
            "ticker": (
                props["종목명"]["select"]["name"]
                if props["종목명"]["select"] else None
            ),

            # 선택
            "type": props["매수/매도"]["select"]["name"],

            # 날짜
            "date": props["날짜"]["date"]["start"],

            # 숫자
            "qty": props["수량"]["number"],

            "price": props["단가"]["number"],

            "amount": props["거래금액"]["formula"]["number"]

        }

        trades.append(trade)

    return trades
