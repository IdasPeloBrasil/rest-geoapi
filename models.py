from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
Base = declarative_base()

class Edificacao(Base):
    __tablename__ = 'edificacao'
    __table_args__ = {'schema': 'public'}

    id = Column('id', Integer, primary_key=True)
    nome = Column('nome', String(length=100))
    geom = Column('geom', Geometry(geometry_type='POLYGON', srid=4674, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True)
