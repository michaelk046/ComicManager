from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from database import AsyncSessionLocal, get_db, engine
from models import Base, User, Grade, Publisher
from schemas import UserCreate, UserOut, ComicCreate, ComicOut
from auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash
)
from crud import get_comics, create_comic, update_comic, delete_comic
from seed_data import grades, publishers
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Comic Manager API")
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        try:
            # Populate grades if empty
            result = await db.execute(select(Grade))
            if not result.scalars().all():
                for g in grades:
                    db.add(Grade(**g))
                await db.commit()
                print("Grades populated")

            # Populate publishers if empty
            result = await db.execute(select(Publisher))
            if not result.scalars().all():
                for p in publishers:
                    db.add(Publisher(name=p))
                await db.commit()
                print("Publishers populated")
        except Exception as e:
            print(f"Error populating tables: {e}")
# === AUTH ROUTES ===

@app.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if username exists
        result = await db.execute(select(User).where(User.username == user.username))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Hash password
        hashed_password = get_password_hash(user.password)

        # Create new user
        new_user = User(username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserOut(id=new_user.id, username=new_user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# === COMIC ROUTES ===
@app.get("/comics", response_model=list[ComicOut])
async def read_comics(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: UserOut = Depends(get_current_user)
):
    return await get_comics(db, current_user.id, skip=skip, limit=limit)
@app.post("/comics", response_model=ComicOut)
async def add_comic(
        comic: ComicCreate,
        db: AsyncSession= Depends(get_db),
        current_user: UserOut = Depends(get_current_user)
):
    return await create_comic(db, comic, current_user.id)
@app.patch("/comics/{comic_id}", response_model=Comic)
async def edit_comic(
        comic_id: int,
        comic_update: ComicCreate,
        db: AsyncSession= Depends(get_db),
        current_user: UserOut = Depends(get_current_user)
):
    comic = await update_comic(db, comic_id, comic_update, current_user.id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    return comic
@app.delete("/comics/{comic_id}")
async def remove_comic(
        comic_id: int,
        db: AsyncSession= Depends(get_db),
        current_user: UserOut = Depends(get_current_user)
):
    comic = await delete_comic(db, comic_id, current_user.id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {"detail": "Comic deleted"}
@app.get("/")
async def root():
    return {"message": "Comic Manager API is running! 📚🦸"}

@router.get("/comics", response_model=list[Comic])
async def read_comics(
    db: AsyncSession= Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    return await get_comics(db, current_user.id)

@router.post("/comics", response_model=Comic)
async def add_comic(
    comic: ComicCreate,
    db: AsyncSession= Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    return await create_comic(db, comic, current_user.id)

@router.patch("/comics/{comic_id}", response_model=Comic)
async def edit_comic(
    comic_id: int,
    comic_update: ComicCreate,
    db: AsyncSession= Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    comic = await update_comic(db, comic_id, comic_update, current_user.id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    return comic

@router.delete("/comics/{comic_id}")
async def remove_comic(
    comic_id: int,
    db: AsyncSession= Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    comic = await delete_comic(db, comic_id, current_user.id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {"detail": "Comic deleted"}

app.include_router(router)