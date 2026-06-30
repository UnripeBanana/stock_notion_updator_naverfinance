from trade_reader import read_trade_db
from fifo import group_by_ticker, process_fifo
from notion_updater import update_trade_page
from stock_updater import update_stock_prices

# --------------------------
# 거래내역 FIFO 계산
# --------------------------

trades = read_trade_db()
trades.sort(key=lambda x: x["date"])

groups = group_by_ticker(trades)
results = process_fifo(groups)

for ticker, result in results.items():

    print(f"\n===== {ticker} =====")

    # 잔량 업데이트
    for page_id, qty in result["remaining"].items():
        update_trade_page(
            page_id=page_id,
            remaining=qty
        )

    # 실현수익 업데이트
    for page_id, profit in result["profit_by_sell"].items():
        update_trade_page(
            page_id=page_id,
            profit=profit
        )

    print(f"{ticker} 거래내역 업데이트 완료")

# --------------------------
# 현재가 업데이트
# --------------------------

print("\n현재가 업데이트 시작...\n")

update_stock_prices()

print("\n모든 업데이트 완료!")
