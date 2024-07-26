import sqlite3


def delete(key):
    conn = sqlite3.connect(r'C:\Users\morga\PycharmProjects\Pitonchik/serial.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serial(
                       serial_id INT PRIMARY KEY,
                       serial_name TEXT);
                    """)
    cur.execute("DELETE FROM serial WHERE serial_id=?", key)
    conn.commit()
    conn.close()


def set_value(name, index):
    conn = sqlite3.connect(r'C:\Users\morga\PycharmProjects\Pitonchik/serial.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serial(
           serial_id INT PRIMARY KEY,
           serial_name TEXT);
        """)
    cur.execute("SELECT * FROM serial;")
    one_result = cur.fetchall()
    data = (index, name)
    insert_with_param = """INSERT OR REPLACE INTO serial 
    (serial_id, serial_name) 
    VALUES (?, ?);"""
    cur.execute(insert_with_param, data)
    conn.commit()
    conn.close()


def get_value():
    conn = sqlite3.connect(r'C:\Users\morga\PycharmProjects\Pitonchik/serial.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS serial(
       serial_id INT PRIMARY KEY,
       serial_name TEXT);
    """)
    cur.execute("SELECT * FROM serial;")
    one_result = cur.fetchall()
    conn.close()
    return one_result