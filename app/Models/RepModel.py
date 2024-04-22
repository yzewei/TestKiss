from app import db
from app.Models.CommonModel import CommonModel


class Rep(CommonModel):
    def __init__(self):
        self.table = db['reps']
