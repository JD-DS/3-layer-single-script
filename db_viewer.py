import sqlite3
import os
import pytest


class Singleton:
    count = 0
    cursor = None
    
    def __new__(cls, db_name = 'aquarium.db' ):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
            cls.instance.get_cursor(db_name)
        return cls.instance

    def __init__(self, db_name = 'aquarium.db'):
        self.db_name = db_name
        self.count += 1

    def get_cursor(self, db_name = 'aquarium.db'):
        if os.path.exists(db_name):
            print("DB found, getting cursor")
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()
        else:
            print("DB NOT found!  run initialize_database first")
            self.cursor = None
            

    def sql(self, sql_statement):
        if self.cursor:
            print("Executing: {}".format(sql_statement))
            try:
                rows = self.cursor.execute(sql_statement).fetchall()
            except Exception as e:
                print(e)
                return []
            return rows
        else:
            print("No database connection")
            return []


def initialize_database(db_name = 'aquarium.db'): 
    """Initialise a file, and use sqlite3 to generate a small table we'll use for testing"""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    print("INTIALIZING DATABASE")
    cursor.execute("CREATE TABLE fish (name TEXT, species TEXT, tank_number INTEGER)")
    cursor.execute("INSERT INTO fish VALUES ('Sammy', 'shark', 1)")
    cursor.execute("INSERT INTO fish VALUES ('Jamie', 'cuttlefish', 7)")
    connection.commit()

def delete_database(db_name = 'aquarium.db'):
    """Delete, or clear the entire database completely
       Sqlite3 uses files to store your date, so clearing it just deleting the file
    """
    if os.path.exists(db_name):
        os.remove(db_name)
   
def db_fresh_start():
    """For testing purposes, it's useful to reset to a known state.
        So we clear the database, and then unitialize it with only our small set of data
    """
    delete_database()
    initialize_database()

################################
# ***** TESTS *****
################################
def test_is_singleton():
    delete_database()
    a = Singleton()
    b = Singleton()
    assert id(a) == id(b)
    
def test_not_initialized():
    delete_database()
    db = Singleton()
    assert [] == db.sql("SELECT * FROM FISH;")

def test_database_connect():
    db_fresh_start()
    db = Singleton()
    db.get_cursor()
    assert 2 == len(db.sql("SELECT * FROM fish;"))
    delete_database()

def test_resetting_after_db_creation():
    delete_database()

    db_a = Singleton()
    db_b = Singleton()
    assert id(db_a) == id(db_b)
    db_a.get_cursor()
    assert [] == db_a.sql("SELECT * FROM FISH;")
    assert [] == db_b.sql("SELECT * FROM FISH;")

    initialize_database()

    db_a.get_cursor()
    assert 2 == len(db_b.sql("SELECT * FROM fish;"))
    delete_database()




######################## Adding a pytest fixture to test the the data in the test database ############################

# Define a Pytest fixture with session scope, it will be run once per test session

@pytest.fixture(scope="session")
def test_db():

    # Create a new in-memory SQLite database connection.

    conn = sqlite3.connect(":memory:")

     # Get a cursor object for the new database connection.

    c = conn.cursor()

    # Create a new "fish" table with columns for name, species, and tank number.

    c.execute("CREATE TABLE fish (name TEXT, species TEXT, tank_number INTEGER)")
    c.execute("INSERT INTO fish VALUES ('Sammy', 'shark', 1)")
    c.execute("INSERT INTO fish VALUES ('Jamie', 'cuttlefish', 7)")
    conn.commit()

    yield conn  # Return the database connection to the test
    conn.close()  # Close the database connection after the test completes


# Create an xfail test to make sure data was initialized correclty

@pytest.mark.xfail(reason= "This is the newly added pytest fixture test,  Failure was expected")
def test_fish_count(test_db):

    # Call the test_db() function 

    c = test_db.cursor()

    # Get the count of entries when the db was initilaized

    count = c.execute("SELECT COUNT(*) FROM fish").fetchone()[0]

    # Assert the count is 2, as expected - through xfail assertion that count is 3

    assert count == 3, f'Expected 2 and got {count}.'


#######################################################################################################################






if __name__=="__main__":

    
    db = Singleton()
    
    while True:
        stmt = input("=> ")
        if stmt == 'quit':
            break

        rows = db.sql(stmt)
        for row in rows:
            print(row)
            