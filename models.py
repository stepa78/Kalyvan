import datetime
import decimal

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Integer, String, ForeignKey, DECIMAL, DATETIME, TIMESTAMP, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from flask_login import UserMixin


STOCK_PRICE = lambda : DECIMAL(precision=10, scale=2)


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)


class User(UserMixin, db.Model):
    #__tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    password: Mapped[str] = mapped_column(String(80))
    avatar: Mapped[str] = mapped_column(String(1000), nullable=True)

    def get_account(self, account_id):
        return Account.query.filter(Account.user_id == self.id, Account.id == account_id).first()

    def get_accounts(self):
        return [a for a in Account.query.filter(Account.user_id == self.id)]


class Account(db.Model):
    __tablename__ = 'account'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    balance: Mapped[decimal.Decimal] = mapped_column(STOCK_PRICE(), default=100000)

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'code': self.code
        }

    def get_account_stock(self, stock_id):
        return AccountStock.query.filter(AccountStock.account_id == self.id, AccountStock.stock_id == stock_id).first()


class Stock(db.Model):
    __tablename__ = 'stock'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    start_date: Mapped[datetime.datetime] = mapped_column(DATETIME(), nullable=False)
    start_price: Mapped[decimal.Decimal] = mapped_column(STOCK_PRICE())
    lot_size: Mapped[int] = mapped_column(Integer, default=1)


class AccountStock(db.Model):
    __tablename__ = 'account_stock'
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('account.id'), primary_key=True, nullable=False)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey('stock.id'), primary_key=True, nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[decimal.Decimal] = mapped_column(STOCK_PRICE())
    buy_date: Mapped[datetime.datetime] = mapped_column(DATETIME(), nullable=False)


class Tick(db.Model):
    tick: Mapped[int] = mapped_column(Integer, primary_key=True)


class StockTick(db.Model):
    tick: Mapped[int] = mapped_column(Integer)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey('stock.id'))
    price: Mapped[decimal.Decimal] = mapped_column(STOCK_PRICE())

    __table_args__ = (PrimaryKeyConstraint('tick', 'stock_id'), )

