from sqlalchemy import Column, Float, ForeignKey, Integer, String, func, select
from sqlalchemy.orm import Session, declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True)
    category = Column(String)
    prices = relationship("Price")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    store_id = Column(Integer)
    amount = Column(Float)


def find_product(session: Session, sku: str) -> Product | None:
    return session.scalars(
        select(Product).where(func.lower(Product.sku) == sku.lower())
    ).first()


def apply_markdown(session: Session, category: str, percent: float) -> int:
    products = session.scalars(
        select(Product).where(Product.category == category)
    ).all()
    updated = 0
    for product in products:
        for price in product.prices:
            price.amount = price.amount * (1 - percent / 100)
            updated += 1
        session.commit()
    return updated


def import_prices(session: Session, rows: list[dict]) -> None:
    for row in rows:
        product = find_product(session, row["sku"])
        session.add(
            Price(product_id=product.id, store_id=row["store_id"], amount=row["amount"])
        )
    session.commit()


def price_report(session: Session, store_id: int) -> list:
    return session.execute(
        select(Product.sku, Price.amount)
        .join(Price)
        .where(Price.store_id == store_id)
        .order_by(Price.amount.desc())
    ).all()
