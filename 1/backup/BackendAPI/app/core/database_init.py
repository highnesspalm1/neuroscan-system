#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initialization and migration utilities
"""

import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import engine, Base
from app.models import Customer, Product, Certificate, ScanLog, APIKey, User

logger = logging.getLogger(__name__)


def init_database():
    """
    Initialize the database with proper error handling
    """
    try:
        # Check if database connection is working
        with engine.connect() as connection:
            logger.info("Database connection established successfully")
            
            # Check if we're using PostgreSQL
            if "postgresql" in str(engine.url):
                logger.info("Using PostgreSQL database")
                # Enable UUID extension for PostgreSQL
                try:
                    connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                    connection.commit()
                    logger.info("UUID extension enabled")
                except Exception as e:
                    logger.warning(f"Could not enable UUID extension: {e}")
            
            # Create tables using SQLAlchemy models
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
            # Verify tables exist
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
            
            # Create default admin user if it doesn't exist
            create_default_admin_user()
            
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return False


def create_default_admin_user():
    """Create default admin user if none exists"""
    try:
        from sqlalchemy.orm import sessionmaker
        from app.core.security import get_password_hash
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if admin user already exists
        admin_exists = session.query(User).filter(User.role == "admin").first()
        
        if not admin_exists:
            logger.info("Creating default admin user...")
            
            # Create default admin
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                username="admin",
                email="admin@neuroscan.com",
                hashed_password=hashed_password,
                role="admin",
                is_active=True
            )
            
            session.add(admin_user)
            session.commit()
            logger.info("Default admin user created successfully (username: admin, password: admin123)")
        else:
            logger.info("Admin user already exists")
            
        session.close()
        
    except Exception as e:
        logger.error(f"Failed to create default admin user: {e}")


def reset_database():
    """
    Reset database by dropping and recreating all tables
    WARNING: This will delete all data!
    """
    try:
        logger.warning("Resetting database - all data will be lost!")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("Database reset completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


def check_database_health():
    """
    Check database connectivity and basic health
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                logger.info("Database health check passed")
                return True
            else:
                logger.error("Database health check failed")
                return False
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
