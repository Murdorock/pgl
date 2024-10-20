import sqlite3
from datetime import datetime

def configurar_base_datos():
    def adapt_date(date):
        return date.strftime('%Y-%m-%d')

    def convert_date(bytestr):
        return datetime.strptime(bytestr.decode('utf-8'), '%Y-%m-%d').date()

    sqlite3.register_adapter(datetime.date, adapt_date)
    sqlite3.register_converter('DATE', convert_date)

    return sqlite3.connect('resources/BD_Inmel.db', detect_types=sqlite3.PARSE_DECLTYPES)