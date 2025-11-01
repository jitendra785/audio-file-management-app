from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from pymongo import MongoClient
from gridfs import GridFS
from typing import Optional
from .app_config import get_config

# SQLAlchemy instance
db = SQLAlchemy()

# MongoDB client and GridFS instances
_mongo_client: Optional[MongoClient] = None
_mongo_db = None
_gridfs: Optional[GridFS] = None


def init_db(app) -> None:
    """Initialize database connections"""
    config = get_config()

    # PostgreSQL configuration
    pg_config = {
        'host': config.get('database.postgres.host'),
        'port': config.get('database.postgres.port'),
        'database': config.get('database.postgres.database'),
        'username': config.get('database.postgres.username'),
        'password': config.get('database.postgres.password')
    }

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{pg_config['username']}:{pg_config['password']}"
        f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Import models to register them with SQLAlchemy
    from dbentities.user import User
    from dbentities.audio_file import AudioFile

    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

        # Create default admin user if it doesn't exist
        from dbentities.user import UserRole
        admin_user = User.query.filter_by(username='Admin').first()
        if not admin_user:
            import bcrypt
            password_hash = bcrypt.hashpw('Admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(
                username='Admin',
                email='admin@audioapp.com',
                password_hash=password_hash,
                role=UserRole.ADMIN,
                full_name='Administrator'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='Admin', password='Admin123'")

    # MongoDB configuration
    global _mongo_client, _mongo_db, _gridfs
    mongo_config = {
        'host': config.get('database.mongodb.host'),
        'port': config.get('database.mongodb.port'),
        'database': config.get('database.mongodb.database'),
        'username': config.get('database.mongodb.username'),
        'password': config.get('database.mongodb.password')
    }

    mongo_uri = (
        f"mongodb://{mongo_config['username']}:{mongo_config['password']}"
        f"@{mongo_config['host']}:{mongo_config['port']}"
    )

    _mongo_client = MongoClient(mongo_uri)
    _mongo_db = _mongo_client[mongo_config['database']]
    _gridfs = GridFS(_mongo_db)


def get_db_session() -> Session:
    """Get SQLAlchemy database session"""
    return db.session


def get_mongo_db():
    """Get MongoDB database instance"""
    return _mongo_db


def get_gridfs() -> GridFS:
    """Get GridFS instance for file storage"""
    return _gridfs
