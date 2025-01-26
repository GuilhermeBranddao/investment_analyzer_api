from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models import models

class RepositoryUser():
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: schemas.User):
        user_bd = models.User(name=user.name,
                                    password=user.password,
                                    email=user.email)
        
        print(">>>>>", user)
        self.session.add(user_bd)
        self.session.commit()
        self.session.refresh(user_bd)
        return user_bd

    def list_user(self):
        stmt = select(models.User)
        users = self.session.execute(stmt).scalars().all()
        return users

    def get_user_per_email(self, email) -> models.User:
        query = select(models.User).where(
            models.User.email == email)
        return self.session.execute(query).scalars().first()