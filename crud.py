from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Comic
from schemas import ComicCreate

async def get_comics(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Comic)
        .where(Comic.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Comic.created_at.desc())
    )
    return result.scalars().all()

async def get_comic(db: AsyncSession, comic_id: int, user_id: int):
    result = await db.execute(
        select(Comic).where(Comic.id == comic_id, Comic.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def create_comic(db: AsyncSession, comic: ComicCreate, user_id: int):
    db_comic = Comic(**comic.dict(), user_id=user_id)
    db.add(db_comic)
    await db.commit()
    await db.refresh(db_comic)
    return db_comic

async def update_comic(db: AsyncSession, comic_id: int, comic_update: ComicCreate, user_id: int):
    db_comic = await get_comic(db, comic_id, user_id)
    if not db_comic:
        return None
    for key, value in comic_update.dict(exclude_unset=True).items():
        setattr(db_comic, key, value)
    await db.commit()
    await db.refresh(db_comic)
    return db_comic

async def delete_comic(db: AsyncSession, comic_id: int, user_id: int):
    db_comic = await get_comic(db, comic_id, user_id)
    if not db_comic:
        return None
    await db.delete(db_comic)
    await db.commit()
    return db_comic