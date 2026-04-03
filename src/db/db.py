import sqlite3
from typing import Generator

from src.db.migration import create_tables

def get_test_db():
    conn = sqlite3.connect(":memory:")
    return conn

def get_connection():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> Generator:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    create_tables(conn)
    conn.close()

