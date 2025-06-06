#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initialization and migration utilities
"""

import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import engine, Base
from app.models.user import User
from app.models.product import Product
from app.models.certificate import Certificate
from app.models.verification_log import VerificationLog
from app.models.audit_log import AuditLog

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
            
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return False


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
