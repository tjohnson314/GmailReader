
import sqlite3

def queryWithKeyword(c, substr):
    c.execute("SELECT * FROM texts")
    print(c.fetchone())

def main():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    queryWithKeyword(c, "I love you")