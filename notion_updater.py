from notion_client import Client
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]

notion = Client(auth=NOTION_TOKEN)


def update_trade_page(page_id, remaining=None, profit=None):

    properties = {}

    if remaining is not None:
        properties["잔량"] = {
            "number": remaining
        }

    if profit is not None:
        properties["실현수익"] = {
            "number": profit
        }

    notion.pages.update(
        page_id=page_id,
        properties=properties
    )
