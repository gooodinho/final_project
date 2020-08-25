import sqlite3

from aiogram import types


class Database:
    def __init__(self, path_to_db="data/main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False,
                fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        cursor.execute(sql, parameters)
        data = None
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE Users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        username varchar(255),
        full_name varchar(255),
        referral INTEGER,
        balance int DEFAULT 0 NOT NULL
        );
        """
        self.execute(sql, commit=True)

    def add_user(self, user_id: int, username: str = None, full_name: str = None, referral=None):
        parameters = (user_id, username, full_name)
        if referral:
            parameters += (int(referral),)
            sql = "INSERT INTO Users(user_id, username, full_name, referral) VALUES (?, ?, ?, ?)"
        else:
            sql = "INSERT INTO Users(user_id, username, full_name) VALUES(?, ?, ?)"
        try:
            self.execute(sql, parameters, commit=True)
        except Exception as e:
            print(e)

    def check_referrals(self, user_id: int):
        sql = "SELECT user_id FROM Users WHERE referral=(SELECT id FROM Users WHERE user_id = ?)"
        parameters = (user_id,)
        rows = self.execute(sql, parameters, fetchall=True)
        return rows

    def check_balance(self, user_id: int):
        sql = "SELECT balance FROM Users WHERE user_id = ?"
        parameters = (user_id,)
        return self.execute(sql, parameters, fetchone=True)

    def add_money(self, money: int, user_id: int):
        sql = "UPDATE Users SET balance=balance+? WHERE user_id=?"
        parameters = (money, user_id)
        return self.execute(sql, parameters, commit=True)

    def select_all_users(self):
        sql = "SELECT * FROM Users"
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def get_id(self, user_id: int):
        parameters = (user_id,)
        return self.execute("SELECT id FROM Users WHERE user_id = ?", parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def delete_all_users(self):
        self.execute("DELETE FROM Users;", commit=True)


def logger(statement):
    print(f"""
    Executing: {statement}
    """)