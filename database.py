import sqlite3


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('database.db')

    def get_records(self):
        records= [record[0]/100 for record in self.connection.cursor().execute('SELECT * FROM records')]
        return records

    def add_record(self, record):
        self.connection.cursor().execute(f"insert into records values ({record*100})")
        self.connection.commit()
