import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'default')
app = create_app(env)

if __name__ == '__main__':
    app.run()
