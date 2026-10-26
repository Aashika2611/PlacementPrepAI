from app import create_app
from app.extensions import db

app = create_app()

# Import models so `db.create_all()` (see README) is aware of every table
from app import models  # noqa: E402,F401

if __name__ == "__main__":
    app.run(debug=True, port=5000)
