# Автоматизация обновления данных в базах данных с использованием SQLAlchemy
# Скрипт подключается к базе, получает данные из внешнего API, и обновляет цены продуктов в базе данных.
# Такой подход полезен для интеграции данных и их синхронизации между системами, что актуально для интернет-магазинов и аналитических платформ.


from sqlalchemy import create_engine, Column, Integer, String, Float, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)


def fetch_product_data(api_url: str):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе API: {e}")
        return []


def update_database(products_data):
    engine = create_engine('sqlite:///products.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for product in products_data:
        stmt = update(Product).where(Product.id == product['id']).values(price=product['price'])
        session.execute(stmt)

    session.commit()
    session.close()


# Пример использования
product_api_url = "https://api.example.com/products"
products = fetch_product_data(product_api_url)
if products:
    update_database(products)
