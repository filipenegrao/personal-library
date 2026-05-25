from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import make_engine, make_session_factory
from app.routers import auth, books, export, labels, loans, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = make_engine(settings.database_url)
    app.state.session_factory = make_session_factory(app.state.engine)
    yield
    await app.state.engine.dispose()


app = FastAPI(title="Personal Library", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(labels.router, prefix="/labels", tags=["labels"])
app.include_router(export.router, prefix="/export", tags=["export"])
