import os
import sqlite3

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'benchmark-framework'))

import src.dbi as old_dbi

class DBi(old_dbi.DBi):
    def add_run(self, loop_offset, loop_size):
        return self.__create_run(loop_offset, loop_size)

    def __setup_db(self):
        connection = sqlite3.connect(self.db_loc)
        cursor = connection.cursor()
        to_exec = """
        CREATE TABLE runs (
            run_id INTEGER PRIMARY KEY,
            loop_offset INTEGER,
            loop_size INTEGER
        );"""
        cursor.execute(to_exec)

        to_exec = """
        CREATE TABLE results (
            id INTEGER PRIMARY KEY,
            run_id INTEGER,
            time INT,
            energy REAL,
            FOREIGN KEY (run_id) REFERENCES runs
        );"""
        cursor.execute(to_exec)

        connection.commit()
        cursor.close()
        connection.close()

    def __create_run(self, loop_offset, loop_size):
        with self:
            self.cursor.execute("INSERT INTO runs(loop_offset, loop_size) VALUES(?, ?)", (loop_offset, loop_size))
            run_id = self.cursor.lastrowid

            self.connection.commit()
        return run_id
