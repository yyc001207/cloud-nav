from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    BigInteger,
    JSON,
    Index,
)
from sqlalchemy.sql import func
from app.core.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TabModel(Base):
    __tablename__ = "tabs"
    __table_args__ = (Index("idx_tabs_user_order", "user_id", "order"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    label = Column(String(100), nullable=False)
    desc = Column(String(500), nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WebsiteModel(Base):
    __tablename__ = "websites"
    __table_args__ = (
        Index("idx_websites_user_tab_order", "user_id", "tab_id", "order"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    tab_id = Column(Integer, nullable=False, index=True)
    label = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    desc = Column(String(500), nullable=True)
    icon = Column(JSON, nullable=True)
    document = Column(JSON, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MenuModel(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(200), nullable=True)
    name = Column(String(100), nullable=True)
    component = Column(String(200), nullable=True)
    meta = Column(JSON, nullable=True)
    parent_id = Column(Integer, nullable=True, index=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class HolidayModel(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, unique=True)
    holiday = Column(Text, nullable=True)
    adjustment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TextTransferModel(Base):
    __tablename__ = "text_transfers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FileTransferModel(Base):
    __tablename__ = "file_transfers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_size = Column(BigInteger, default=0)
    file_hash = Column(String(64), nullable=True)
    content_type = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")
    chunks_uploaded = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class OpenListGlobalConfigModel(Base):
    __tablename__ = "openlist_global_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    base_url = Column(String(500), nullable=False)
    token = Column(String(500), nullable=False)
    video_extensions = Column(JSON, nullable=True)
    subtitle_extensions = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class OpenListTaskConfigModel(Base):
    __tablename__ = "openlist_task_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    output_dir = Column(String(500), nullable=True)
    task_paths = Column(Text, nullable=False)
    max_scan_depth = Column(Integer, nullable=True)
    execution_history = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
