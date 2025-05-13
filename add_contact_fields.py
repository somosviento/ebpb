from app import db, create_app
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import SchemaItem
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import String

def add_columns():
    """
    Añadir campos de dirección postal y correo electrónico alternativo a la tabla de reservaciones.
    """
    print("Agregando nuevas columnas a la tabla 'reservations'...")
    
    app = create_app()
    with app.app_context():
        op.add_column('reservations', sa.Column('alternative_email', sa.String(120), nullable=True))
        op.add_column('reservations', sa.Column('postal_address', sa.String(200), nullable=True))
        
        # Establecer el valor por defecto para postal_address (que ahora es required)
        op.execute("UPDATE reservations SET postal_address = 'No especificado'")
        
        # Cambiar a NOT NULL después de llenar los valores
        op.alter_column('reservations', 'postal_address', nullable=False)
        
        print("Columnas agregadas correctamente.")

if __name__ == '__main__':
    add_columns()
    print("Migración completada.")
