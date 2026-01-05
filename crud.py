from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Publisher, Grade, Comic
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
    publisher_id = None
    if comic.publisher:
        result = await db.execute(select(Publisher.id).where(Publisher.name.ilike(comic.publisher.strip())))
        publisher_id = result.scalar_one_or_none()
        if not publisher_id:
            # Create new publisher if not exists
            new_pub = Publisher(name=comic.publisher.strip())
            db.add(new_pub)
            await db.flush()
            publisher_id = new_pub.id

    grade_id = None
    if comic.grade:
        result = await db.execute(select(Grade.id).where(Grade.abbreviation == comic.grade.strip()))
        grade_id = result.scalar_one_or_none()

    db_comic = Comic(
        user_id=user_id,
        title=comic.title,
        issue_number=comic.issue_number,
        publisher_id=publisher_id,
        grade_id=grade_id,
        cover_image_url=comic.cover_image_url,
        buy_price=comic.buy_price,
        current_value=comic.current_value,
        sell_price=comic.sell_price
    )
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