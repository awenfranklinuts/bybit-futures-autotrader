from bot.trade_executor import place_order

place_order(
    symbol="BTCUSDT",
    side="Buy",
    order_type="Market",
    qty=0.005,
    leverage=10,
    take_profit=210000,
    stop_loss=197000
)
