from app.api import create_app
from app.sample_data import load_sample_data
from app.storage import Storage

storage = Storage("data.db")
load_sample_data(storage)
app = create_app(storage)
