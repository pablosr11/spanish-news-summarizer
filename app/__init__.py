from flask import Flask
from flask import Blueprint
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
import rq

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('forocanario-tasks', connection=app.redis)

from app import routes, models

