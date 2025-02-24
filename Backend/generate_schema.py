from sqlalchemy import create_engine
from models import Base  # assure-toi que `Base` est importé correctement
from datetime import datetime


# Crée une base de données SQLite temporaire
engine = create_engine('sqlite:///temp_schema.db')
Base.metadata.create_all(engine)
