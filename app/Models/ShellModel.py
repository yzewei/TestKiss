from app import db
from app.Models.CommonModel import CommonModel


class Shell(CommonModel):
    def __init__(self):
        self.table = db['shells']
