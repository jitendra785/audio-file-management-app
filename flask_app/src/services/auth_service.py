import bcrypt
from typing import Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from dbentities.user import User, UserRole
from dependencies.database import get_db_session
from basemodels.auth import SignupRequest


class AuthService:
    """Authentication service for user login and signup"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password
        Returns User object if authentication successful, None otherwise
        """
        db = get_db_session()
        user = db.query(User).filter(User.username == username).first()

        if user and AuthService.verify_password(password, user.password_hash):
            return user

        return None

    @staticmethod
    def signup_user(signup_data: SignupRequest) -> Dict[str, Any]:
        """
        Create a new user account
        Returns dict with success status and message
        """
        db = get_db_session()

        try:
            # Hash the password
            password_hash = AuthService.hash_password(signup_data.password)

            # Create new user
            new_user = User(
                username=signup_data.username,
                email=signup_data.email,
                password_hash=password_hash,
                full_name=signup_data.full_name,
                role=UserRole.USER  # Default role is USER
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return {
                'success': True,
                'message': 'User created successfully',
                'user': new_user
            }

        except IntegrityError as e:
            db.rollback()
            if 'username' in str(e.orig):
                return {
                    'success': False,
                    'message': 'Username already exists'
                }
            elif 'email' in str(e.orig):
                return {
                    'success': False,
                    'message': 'Email already exists'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create user'
                }

        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = get_db_session()
        return db.query(User).filter(User.id == user_id).first()
