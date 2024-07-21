import os
import atexit
import datetime
from dotenv import load_dotenv
from typing import List

from sqlalchemy import String, ForeignKey, DateTime, Text, func
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


load_dotenv()

DB_NAME = os.getenv('DB_NAME', 'adverts.db')

engine = create_async_engine(
    f'sqlite+aiosqlite:///{DB_NAME}?charset=utf8',
)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100))
    adverts: Mapped[List['Advert']] = relationship(back_populates="owner")

    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


class Advert(Base):
    __tablename__ = 'advert'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    owner: Mapped[User] = relationship(User, back_populates="adverts")

    @property
    async def json(self):
        owner = await self.awaitable_attrs.owner
        return {
            'id': self.id,
            'title': self.title,
            'note': self.note,
            'created_at': int(self.created_at.timestamp()),
            'owner': owner.name
        }


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
