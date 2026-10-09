from sqlalchemy import create_engine, text

from app.core.config import get_settings

engine = create_engine(get_settings().db_url, pool_pre_ping=True)
with engine.connect() as conn:
    print('CATEGORY_COLUMNS', conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='category' ORDER BY ordinal_position")).fetchall())
    print('VIDEOS_COLUMNS', conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='videos' ORDER BY ordinal_position")).fetchall())
    print('CATEGORY_ROWS', conn.execute(text("SELECT * FROM category ORDER BY id LIMIT 5")).fetchall())
