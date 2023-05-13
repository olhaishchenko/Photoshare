import enum

from sqlalchemy import Boolean, Column, Integer, String, Date, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'

tags_images = Table('tags_images', Base.metadata,
    Column('image_id', ForeignKey('image.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="images")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True)

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    image_id = Column(Integer, ForeignKey("image.id"), nullable=True)
    image = relationship('Image', backref="comments")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship('User', backref="comments")
    image_id = Column(Integer, ForeignKey("image.id"), nullable=True)
    image = relationship('Image', backref="comments")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(355), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    roles = Column('roles', Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    is_aсtive = Column(Boolean, default=True)