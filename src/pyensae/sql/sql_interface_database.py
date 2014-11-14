#-*- coding: utf-8 -*-
"""
@file
@brief Abstract class to connect to a SQL server using various way.
It will be used to implement magic functions
"""
import sys, os, pandas, sqlite3

from .database_main import Database
from .database_exception import ExceptionSQL
from .sql_interface import InterfaceSQL, InterfaceSQLException
from pyquickhelper import noLOG

class InterfaceSQLDatabase(InterfaceSQL):
    """
    Abstract class to connect to a SQL server using various way.
    It will be used to implement magic functions
    """

    def __init__(self, filename):
        """
        initialize the object

        @param      filename        str
        """
        self.obj = Database(filename, LOG = noLOG)

    def connect(self):
        """
        connection to the database
        """
        self.obj.connect()
        self.populate_completion()

    def close(self):
        """
        close the connection to the database
        """
        self.obj.close()

    def get_table_list(self):
        """
        returns the list of tables in the database

        @return     list of strings
        """
        return self.obj.get_table_list()

    def get_table_columns(self, table_name):
        """
        returns the list of columns in a table

        @param      table_name      table name
        @return                     dictionary { "column": (position, type) }
        """
        return self.obj.get_table_columns(table_name, True)

    def execute_clean_query(self, sql_query):
        """
        return the resuls of a SQL query

        @param      sql_query       query to execute
        @return                     pandas DataFrame
        """
        con = self.obj._connection
        try:
            return pandas.read_sql(sql_query, con)
        except pandas.io.sql.DatabaseError as e :
            try:
                self.obj.execute_view(sql_query)
            except Exception as ee :
                raise InterfaceSQLException(str(ee)) from ee

    def import_flat_file(self, filename, table_name):
        """
        import a flat file as a table, we assume the columns
        separator is ``\\t`` and the file name contains a header

        @param      filename        filename
        @param      table           table name
        """
        self.obj.import_table_from_flat_file(filename, table_name, columns = None, header=True)
        self.populate_completion()

    def drop_table(self, table_name):
        """
        drops a table

        @param      table           table name
        """
        self.obj.remove_table(table_name)
        self.populate_completion()

    def add_function(self, code_function):
        """
        add a function to the database which can be called in a SELECT statement

        @param      code_function  pointer to the function
        """
        name = code_function.__name__
        nbp = code_function.__code__.co_argcount
        self.obj.add_function(name, nbp, code_function)

    def import_dataframe(self, tablename, df):
        """
        import a dataframe into the database

        @param      tablename       name of the table
        @param      df              dataframe
        """
        df.to_sql(tablename, self.obj._connection)
        self.populate_completion()