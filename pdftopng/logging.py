import logging
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import threading
import time

DB_URL = 'sqlite:///app_logs.db'
_engine = None
_sessionmaker = None

# Define the Base for declarative class definitions
Base = declarative_base()


def _get_engine():
    # print("_get_engine")
    global _engine
    if not _engine:
        _engine = create_engine(DB_URL, echo=False)
        # _engine = create_engine(
        #     DB_URL,
        #     echo=False,
        #     connect_args={"check_same_thread": False},
        #     pool_size=5,
        #     max_overflow=10
        # )
        Base.metadata.create_all(_engine)
    return _engine


def _get_session():
    # print("_get_session")
    global _sessionmaker
    if not _sessionmaker:
        engine = _get_engine()
        _sessionmaker = sessionmaker(bind=engine)
    session = _sessionmaker()
    return session


# Define the LogEntry model
class LogEntry(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    created = Column(Float)
    levelname = Column(String)
    message = Column(String)
    logger_name = Column(String)
    filename = Column(String)
    func_name = Column(String)
    line_no = Column(Integer)

    def __repr__(self):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.created))
        return (
            f"<LogEntry(id={self.id}, time='{timestamp}', levelname='{self.levelname}', "
            f"message='{self.message}', logger_name='{self.logger_name}', "
            f"filename='{self.filename}', func_name='{self.func_name}', line_no={self.line_no})>"
        )

# Define the SQLAlchemyHandler
class SQLAlchemyHandler(logging.Handler):
    # singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SQLAlchemyHandler, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  
            logging.Handler.__init__(self)
            self.db_lock = threading.Lock()
            self._initialized = True

    def emit(self, record):
        try:
            with self.db_lock:
                session = _get_session()
                log_entry = LogEntry(
                    created=record.created,
                    levelname=record.levelname,
                    message=record.getMessage(),
                    logger_name=record.name,
                    filename=record.filename,
                    func_name=record.funcName,
                    line_no=record.lineno
                )
                session.add(log_entry)
                session.commit()
        except Exception:
            self.handleError(record)
        finally:
            session.close()


# Retrieve the last n logs
def get_last_n_logs(n):
    session = _get_session()
    try:
        return session.query(LogEntry).order_by(LogEntry.id.desc()).limit(n).all()
    finally:
        session.close()


# Retrieve logs within a date range
def get_logs_in_date_range(start_timestamp, end_timestamp):
    session = _get_session()
    try:
        return session.query(LogEntry).filter(
            LogEntry.created >= start_timestamp,
            LogEntry.created <= end_timestamp
        ).order_by(LogEntry.created.asc()).all()
    finally:
        session.close()

