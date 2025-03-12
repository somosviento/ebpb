from __init__ import create_app, db
from flask_migrate import Migrate
from sqlalchemy import text

app = create_app()
migrate = Migrate(app, db)

def add_estado_column():
    with app.app_context():
        # Create a specific migration to add the estado column
        print("Adding 'estado' column to reservations table...")
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE reservations ADD COLUMN estado VARCHAR(20) DEFAULT 'activa'"))
            conn.commit()
        print("Column added successfully!")

if __name__ == "__main__":
    add_estado_column()