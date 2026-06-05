import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

engine = create_engine("sqlite:///./test.db")
models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Add 10,000 products
if db.query(models.Product).count() == 0:
    print("Inserting 10,000 products...")
    products = [models.Product(name=f"Product {i}", price=10.0, filepath="assets/test.pdf") for i in range(10000)]
    db.add_all(products)
    db.commit()

# Measure query time
start = time.time()
db.query(models.Product).all()
end = time.time()
print(f"Time to fetch 10,000 products: {end - start:.4f} seconds")

# Measure with limit and offset
start = time.time()
db.query(models.Product).offset(0).limit(50).all()
end = time.time()
print(f"Time to fetch 50 products: {end - start:.4f} seconds")

db.close()
