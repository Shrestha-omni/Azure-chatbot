from app.state.db import Base, engine
from loguru import logger

def main():
    logger.info("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables created successfully.")

if __name__ == "__main__":
    main()
