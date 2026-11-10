"""Reusable durable lease; the service being controlled owns this database."""
import sqlite3
from pathlib import Path
import time

class Lease:
    def __init__(self,path,clock=time.time):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True);self.clock=clock
        with self.connect() as db:db.execute('CREATE TABLE IF NOT EXISTS lease(id INTEGER PRIMARY KEY CHECK(id=1),owner TEXT NOT NULL,expires REAL NOT NULL)')
        self.path.chmod(0o600)
    def connect(self):return sqlite3.connect(self.path,timeout=10)
    def owner(self):
        db=self.connect()
        try:row=db.execute('SELECT owner,expires FROM lease WHERE id=1').fetchone()
        finally:db.close()
        return row[0] if row and row[1]>self.clock() else None
    def acquire(self,owner,ttl=90):
        if not owner or not 15<=ttl<=300:raise ValueError('invalid_lease')
        db=self.connect()
        try:
            with db:
                db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT owner,expires FROM lease WHERE id=1').fetchone()
                if row and row[0]!=owner and row[1]>self.clock():return False
                db.execute('INSERT OR REPLACE INTO lease VALUES(1,?,?)',(owner,self.clock()+ttl));return True
        finally:db.close()
    def release(self,owner):
        db=self.connect()
        try:
            with db:db.execute('DELETE FROM lease WHERE id=1 AND owner=?',(owner,))
        finally:db.close()
