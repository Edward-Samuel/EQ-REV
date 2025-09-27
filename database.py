from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
import os

# Database configuration
DATABASE_URL = "sqlite:///./stock_data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    city_name = Column(String)
    product_id = Column(String)
    product_name = Column(String)
    category = Column(String)
    total_orders = Column(Integer)
    total_sales = Column(Float)
    stock_quantity = Column(Integer)
    instock_darkstores = Column(Integer)
    oos_darkstores = Column(Integer)
    total_darkstores = Column(Integer)

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_data_from_csv(csv_file_path="stock_data.csv"):
    """Load data from CSV file into database"""
    if not os.path.exists(csv_file_path):
        print(f"CSV file {csv_file_path} not found!")
        return False
    
    # Read CSV file
    df = pd.read_csv(csv_file_path)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(StockData).delete()
        
        # Insert new data
        for _, row in df.iterrows():
            stock_record = StockData(
                date=row['date'].date(),
                city_name=row['city_name'],
                product_id=row['product_id'],
                product_name=row['product_name'],
                category=row['category'],
                total_orders=row['total_orders'],
                total_sales=row['total_sales'],
                stock_quantity=row['stock_quantity'],
                instock_darkstores=row['instock_darkstores'],
                oos_darkstores=row['OOS_darkstores'],
                total_darkstores=row['total_darkstores']
            )
            db.add(stock_record)
        
        db.commit()
        print(f"Successfully loaded {len(df)} records into database")
        return True
        
    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    load_data_from_csv()
