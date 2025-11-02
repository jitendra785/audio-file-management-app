from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from dbentities.user import User, UserRole
from dependencies.database import get_db_session
from basemodels.user import UserCreateRequest, UserUpdateRequest
from services.auth_service import AuthService


class UserService:
    """Service for user management (CRUD operations)"""

    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users"""
        db = get_db_session()
        return db.query(User).all()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = get_db_session()
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(user_data: UserCreateRequest) -> Dict[str, Any]:
        """
        Create a new user (admin function)
        Returns dict with success status and message
        """
        db = get_db_session()

        try:
            # Hash the password
            password_hash = AuthService.hash_password(user_data.password)

            # Create new user
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                full_name=user_data.full_name,
                role=UserRole[user_data.role]
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
    def update_user(user_id: int, user_data: UserUpdateRequest) -> Dict[str, Any]:
        """
        Update an existing user
        Returns dict with success status and message
        """
        db = get_db_session()

        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            # Update fields if provided
            if user_data.email is not None:
                user.email = user_data.email

            if user_data.full_name is not None:
                user.full_name = user_data.full_name

            if user_data.role is not None:
                user.role = UserRole[user_data.role]

            if user_data.password is not None:
                user.password_hash = AuthService.hash_password(user_data.password)

            db.commit()
            db.refresh(user)

            return {
                'success': True,
                'message': 'User updated successfully',
                'user': user
            }

        except IntegrityError as e:
            db.rollback()
            if 'email' in str(e.orig):
                return {
                    'success': False,
                    'message': 'Email already exists'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update user'
                }

        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }

    @staticmethod
    def delete_user(user_id: int) -> Dict[str, Any]:
        """
        Delete a user
        Returns dict with success status and message
        """
        db = get_db_session()

        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            db.delete(user)
            db.commit()

            return {
                'success': True,
                'message': 'User deleted successfully'
            }

        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }
