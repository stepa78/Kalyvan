import datetime
import random
import decimal

from models import Stock, StockTick, Tick, db
from sqlalchemy import func


BURSE_START_DATE = datetime.datetime(year=2024, month=1, day=1)
BURSE_TICK_STEP = 30


def run_ticker(flask_app):
    with (flask_app.app_context()):
        now_tick = int((datetime.datetime.now() + datetime.timedelta(minutes=2)).timestamp())
        start_tick = db.session.query(func.max(Tick.tick)).scalar()

        if start_tick:
            stock_prices = {s.stock_id: s.price for s in StockTick.query.filter(StockTick.tick == start_tick)}
        else:
            start_tick = int(BURSE_START_DATE.timestamp())
            stock_prices = {s.id: s.start_price for s in Stock.query.all()}

        #if now_tick < start_tick:
        #    return

        #if now_tick - start_tick >= 121:
        #    return

        stocks = Stock.query.all()
        print(stock_prices)

        for t in range(start_tick, now_tick, BURSE_TICK_STEP):
            # tick = Tick(tick=t)
            # db.session.add(tick)

            if not Tick.query.filter(Tick.tick == t).first():
                tick = Tick(tick=t)
                db.session.add(tick)

            for i, s in enumerate(stocks):

                if StockTick.query.filter(StockTick.tick == t, StockTick.stock_id == s.id).first():
                    continue

                price = stock_prices[s.id]

                if t != BURSE_START_DATE.timestamp():
                    price = stock_prices[s.id] + \
                        decimal.Decimal(
                            random.choices([1, -1])[0] * random.random()
                        )
                    if price <= 0:
                        price = decimal.Decimal(1.0)

                stock_tick = StockTick(
                    tick=t,
                    stock_id=s.id,
                    price=price
                )
                stock_prices[s.id] = price
                print(f'tick={t}; new price for stock_id {s.id} = {price}')

                db.session.add(stock_tick)
        db.session.commit()
