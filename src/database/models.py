import enum

from sqlalchemy import Boolean, Column, Table, Integer, String, Date, Enum, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class TagsImages(Base):
    __tablename__ = "tags_images"
    id = Column(Integer, primary_key=True)
    image_id = Column('image_id', Integer, ForeignKey('images.id', ondelete="CASCADE"))
    tag_id = Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))




class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    image_url = Column(String(255), unique=True, nullable=False)
    qr_code_url = Column(String(255), unique=True)
    public_id = Column(String(255), unique=True, nullable=False)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())
    description = Column(String(255))
    user = relationship('User', backref="images")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True)


# class Rating(Base):
#     __tablename__ = "ratings"
#     id = Column(Integer, primary_key=True, index=True)
#     rating = Column(Integer)
#     image = relationship('Image', backref="ratings")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship('User', backref="comments")
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
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
    created_at = Column(DateTime, default=func.now())
    confirmed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
