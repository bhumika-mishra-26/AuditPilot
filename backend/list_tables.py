import sqlite3

conn = sqlite3.connect(r"c:\Users\karti\Downloads\bp\backend copy\data\auditpilot.db")
res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in res:
    print(row[0])
conn.close()
