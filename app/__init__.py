from .main import app  # Экспорт FastAPI-приложения
from .database import Base, SessionLocal, engine  # Экспорт DB-объектов
from .models import Link  # Экспорт моделей SQLAlchemy
from .schemas import LinkCreate, LinkResponse  # Экспорт Pydantic-схем
from .crud import create_link, get_link_by_short_code  # Экспорт CRUD-функций

# Опционально: список __all__ для контроля импорта *
__all__ = [
    "app",
    "Base",
    "SessionLocal",
    "engine",
    "Link",
    "LinkCreate",
    "LinkResponse",
    "create_link",
    "get_link_by_short_code",
]