import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'default'))

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
