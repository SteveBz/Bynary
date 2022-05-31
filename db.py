#!/usr/bin/env python

import fdb #pip3 install fdb
import sqlite3  

class db():
    def __init__(self):
        return

    def conFbdb(self, dsn, user, password):
        con = fdb.connect(dsn, user, password)
        return con
    
    def conSQLite(self, dsn):
        #print(dsn)
        con = sqlite3.connect(dsn)
        return con
    
    def cursor(self):
        self.cur = self.con.cursor()
        return self.cur

    def close(self):
        self.con.close()
        
    def execute(self, SQL):
        try:
            self.cur.execute(SQL)
        except Exception as e:
            # Handling
            print ("Execution error")