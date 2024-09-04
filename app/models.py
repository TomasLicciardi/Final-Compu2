from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    alias = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)

    reviews = relationship('Review', back_populates='usuario')

    def __repr__(self):
        return f'<Usuario(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, alias={self.alias})>'

class Pelicula(Base):
    __tablename__ = 'peliculas'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    genero = Column(String, nullable=False)

    reviews = relationship('Review', back_populates='pelicula')

    def __repr__(self):
        return f'<Pelicula(id={self.id}, nombre={self.nombre}, genero={self.genero})>'

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    texto = Column(Text, nullable=False)
    calificacion = Column(Integer, nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    id_pelicula = Column(Integer, ForeignKey('peliculas.id'), nullable=False)

    usuario = relationship('Usuario', back_populates='reviews')
    pelicula = relationship('Pelicula', back_populates='reviews')

    def __repr__(self):
        return f'<Review(id={self.id}, texto={self.texto}, calificacion={self.calificacion}, id_usuario={self.id_usuario}, id_pelicula={self.id_pelicula})>'

# Conexión a la base de datos
engine = create_engine('sqlite:///reviews.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
