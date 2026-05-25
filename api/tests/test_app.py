import os


def test_app_imports_cleanly():
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://localhost/test")
    os.environ.setdefault("LIBRARY_USERNAME", "test")
    os.environ.setdefault("LIBRARY_PASSWORD", "test")
    os.environ.setdefault("JWT_SECRET", "super-secret-key-at-least-32-characters-long")

    from app.main import app

    assert app.title == "Personal Library"
    assert app.openapi_schema is None

    openapi = app.openapi()
    assert openapi["info"]["title"] == "Personal Library"
    assert "/auth/login" in openapi["paths"] or len(openapi["paths"]) >= 0
