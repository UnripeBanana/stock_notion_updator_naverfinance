from collections import defaultdict, deque


def group_by_ticker(trades):
    grouped = defaultdict(list)

    for trade in trades:
        grouped[trade["ticker"]].append(trade)

    return grouped

def process_fifo(grouped_trades):

    results = {}

    for ticker, trades in grouped_trades.items():

        queue = deque()

        remaining = {}

        profit_by_sell = {}

        realized_profit = 0

        for trade in trades:

            # 매수
            if trade["type"] == "매수":

                queue.append({
                    "page_id": trade["page_id"],
                    "qty": trade["qty"],
                    "price": trade["price"]
                })
                remaining[trade["page_id"]] = trade["qty"]

            # 매도
            else:

                sell_qty = trade["qty"]

                # 매도 페이지는 잔량이 항상 0
                remaining[trade["page_id"]] = 0

                sell_profit = 0

                while sell_qty > 0:

                    oldest = queue[0]

                    matched = min(
                        sell_qty,
                        oldest["qty"]
                    )

                    profit = (
                        trade["price"] - oldest["price"]
                    ) * matched

                    realized_profit += profit

                    sell_profit += profit

                    oldest["qty"] -= matched
                    sell_qty -= matched
                    remaining[oldest["page_id"]] -= matched

                    if oldest["qty"] == 0:
                        queue.popleft()
                    profit_by_sell[trade["page_id"]] = sell_profit
                    
        results[ticker] = {
            "remaining": remaining,
            "profit_by_sell": profit_by_sell,
            "profit": realized_profit
        }

    return results
