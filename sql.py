import sqlite3


def delete(key):
    conn = sqlite3.connect(r'C:\Users\morga\PycharmProjects\Pitonchik/serial.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serial(
                       serial_id INT PRIMARY KEY,
                       serial TEXT);
                    """)
    cur.execute("DELETE FROM serial WHERE serial_id=?", key)
    conn.commit()
    conn.close()


def set_value(name):
    conn = sqlite3.connect(r'C:\Users\morga\PycharmProjects\Pitonchik/serial.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serial(
           serial_id INT PRIMARY KEY,
           serial TEXT);
        """)
    cur.execute("SELECT * FROM serial;")
    one_result = cur.fetchall()
    data = (len(one_result) + 1, name)
    cur.execute("INSERT INTO serial VALUES (?, ?)", data)
    conn.commit()
    conn.close()


def get_value():
    conn = sqlite3.connect(r'C:\Users\morga\PycharmProjects\Pitonchik/serial.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serial(
       serial_id INT PRIMARY KEY,
       serial TEXT);
    """)
    cur.execute("SELECT * FROM serial;")
    one_result = cur.fetchall()
    conn.close()
    return one_result