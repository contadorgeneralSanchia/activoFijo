from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os
DB_PATH = os.getenv("DB_PATH", "data/activos.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
print("👉 Base de datos usada por Flask:", os.path.abspath(DB_PATH))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
class Activo(Base):
    __tablename__ = "activos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    qr_uid = Column(String, unique=True, index=True)
    codigo = Column(String, index=True)
    nombre = Column(String)
    fecha_adquisicion = Column(String)
    fecha_inicio_uso = Column(String)
    meses_depreciacion = Column(Integer)
    ubicacion = Column(String)
    departamento = Column(String)
    serie = Column(String)
    costo_adquisicion = Column(Float)
    total_depreciado = Column(Float)
    pct_depreciacion_anual = Column(Float)
    depreciacion_acumulada = Column(Float)
    saldo_por_depreciar = Column(Float)
def init_db():
    Base.metadata.create_all(bind=engine)
