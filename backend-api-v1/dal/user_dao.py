
from typing import Optional
from entities.user import User
from sqlalchemy.orm import Session
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Check if a password matches a hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(session:Session,user:User):
    # Fix: correct filter syntax
    filtred_user=session.query(User).filter(User.email == user.email).one_or_none()
    if filtred_user != None :
        return False
    # Hash the password before storing
    user.password = hash_password(user.password)
    session.add(user)
    try :
        session.commit()
        session.refresh(user)
        return True
    except Exception as e:
        session.rollback()   
        return False
def get_all_users(session:Session):
    return session.query(User).all()

def authenticate(session:Session,user:User):
    filtred_user:User=session.query(User).filter(
        User.email==user.email
        ).one_or_none()
    if filtred_user and check_password(user.password, filtred_user.password):
        return filtred_user
    return False