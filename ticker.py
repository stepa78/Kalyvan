import datetime
import random
import decimal

from models import Stock, StockTick, Tick, db
from sqlalchemy import func
from app import BURSE_TICK_STEP, BURSE_START_DATE




def ticker():
    StockTick.query.delete()
    Tick.query.delete()

    stocks = Stock.query.all()
    stock_prices = [s.start_price for s in stocks]

    stop_tm = int(datetime.datetime.now().timestamp())
    start_tm = db.session.query(func.max(Tick.tick)).scalar()
    if not start_tm:
        start_tm = int(BURSE_START_DATE.timestamp())
    else:
        stock_prices = [s.price for s in StockTick.query.filter(tick=start_tm).first()]

    for t in range(start_tm, stop_tm, BURSE_TICK_STEP):
        tick = Tick(tick=t)
        db.session.add(tick)

        for i, s in enumerate(stocks):
            price = stock_prices[i]
            if t != BURSE_START_DATE.timestamp():
                price = stock_prices[i] + decimal.Decimal(random.choices([1,-1])[0] * random.random() * 10 + 1)
            stock_tick = StockTick(
                 tick=t,
                 stock_id=s.id,
                 price=price
            )
            stock_prices[i] = price

            db.session.add(stock_tick)
    db.session.commit()