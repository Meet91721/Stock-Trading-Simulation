from backend.config.secrets import MONGO_CREDENTIALS

MONGO_USER = MONGO_CREDENTIALS['user']
MONGO_DATABASE = MONGO_CREDENTIALS['dbname']
MONGO_PASSWORD = MONGO_CREDENTIALS['password']
MONGO_HOST = MONGO_CREDENTIALS['host']
MONGO_PORT = MONGO_CREDENTIALS['port']
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"