import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('./database/database.db',isolation_level=None)
        with open('./database/schema.sql') as f:
            self.connection.executescript(f.read())
        self.cur = self.connection.cursor()

    def getter(self,table):
        result = self.cur.execute("SELECT * from {0}".format(table))
        return result
        

    def set_keyword(self,word):
        try:  
            self.cur.execute("INSERT INTO SEARCHES (Keyword) \
                    VALUES ('{0}')".format(word))
        except Exception as e:
            print(e)

    def set_subtitle(self,subtitle,keyword):
        try:  
            self.cur.execute("INSERT INTO SUBTITLES (Name,Keyword) \
                    VALUES ('{0}','{1}')".format(subtitle,keyword))
        except Exception as e:
            print(e)
