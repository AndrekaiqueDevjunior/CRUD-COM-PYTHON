import sqlite3 as sql

con = sql.connect ('form_db.db')
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS usuarios')

sql = ''' CREATE TABLE "usuarios" (
    "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "NOME" TEXT,
    "IDADE" TEXT,
    "RUA" TEXT,
    "CIDADE" TEXT,
    "NUMERO" TEXT,
    "ESTADO" TEXT,
    "EMAIL" TEXT
        )'''

cur.execute(sql)
con.commit()
con.close()



