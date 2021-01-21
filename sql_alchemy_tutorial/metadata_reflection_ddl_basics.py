from sqlalchemy import MetaData, Table, Column, Integer, String, select, Text, DateTime
from sqlalchemy import create_engine

# import logging
#
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

'''
metadata describes the structure of the databse such as tables, columns, constraints in terms of data structures in 
python

serves as the bassis for sql gernation and object relational mapping (like the classes in a flask model)

can generate to a schema; turned into ddl (data def language) that is emitted to the database 

introspect a database and generate python structure objects that represent tables

basis for migration tools like sqlalchemy alembic

some basic types:
    Integer: basic int type generates a INT
    String: strings, generates a VARCHAR
    Unicode: unicode strings, generates VARCHAR, NVARCHAR depending on database 
    Boolean: generates a BOOLEAN,INT,TINYINT,BIT all depending on the database
    Datetime: generates DATEIMTE or TIMESTAMP, returns pythong datetime objects
    Float: floating point values
    Numeric: precision numerics using python Decimal()
    JSON: supported by postgresql, mysql, sqlite
    Array: supported by postgresql
'''

print('*********************************** metadata **********************************************************')

# looks like a sql create table statement


metadata = MetaData()  # a collection of table objects
user_table = Table(
    'user',  # we are calling the table 'user'
    metadata,  # placing it in the metadata that we defined above
    Column('id', Integer, primary_key=True),
    Column('username', String(50), nullable=False),
    Column('fullname', String(255))
)

# some useful things here
print(user_table.name)  # get table name

print(user_table.c)  # get column names

# we can use repr in print to print with the __repr__ method if there is not a custom __str__ defined
print(repr(user_table.c.username))  # get column info of the column called username

# get some basic information about a specfic column
print(user_table.c.username.name)
print(user_table.c.username.type)

# you can also check out primary keys
print(user_table.primary_key)

# you can see tables in the metadata using a dictionary object
print(metadata.tables.keys())
print(repr(metadata.tables['user']))

print('*********************************** creating a table **********************************************************')
from sqlalchemy import ForeignKey, ForeignKeyConstraint

engine = create_engine('sqlite:///some.db')
metadata = MetaData()  # a collection of table objects
user_table = Table(
    'user',  # we are calling the table 'user'
    metadata,  # placing it in the metadata that we defined above
    Column('id', Integer, primary_key=True),
    Column('username', String(50), nullable=False),
    Column('fullname', String(255))
)

address_table = Table(
    'address',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('email_address', String(100), nullable=False),
    # here we can create a foreign key which just means that this value has to exist someplace else and is essentially a
    # constraint. Typically a primary key of another table, in this case the user table.
    Column('user_id', ForeignKey('user.id'), nullable=False)
)

story_table = Table(
    'story',
    metadata,
    Column('story_id', Integer, primary_key=True),
    Column('version_id', Integer, primary_key=True),
    Column('headline', String(100), nullable=True),
    Column('body', Text)
)

published_table = Table(
    'published',
    metadata,
    Column('pub_id', Integer, primary_key=True),
    Column('pub_timestamp', DateTime, nullable=False),
    Column('story_id', Integer),
    Column('version_id', Integer),
    ForeignKeyConstraint(
        # used when we have more than one foreign keys; typically when a table has multiple primary keys
        ['story_id', 'version_id'], ['story.story_id', 'story.version_id']
    )
)

# we can create a table like so
with engine.begin() as conn:
    metadata.create_all(conn)

print('*********************************** reflection **********************************************************')

# one example of usage would be in Alembic that compares model code to the database for migrations
# another example would be if you want to play around with a database, it is easier to reflect them and mess around
#   rather then rename those tables

# *mostly used for migrations

engine = create_engine('sqlite:///some.db')
# refers to the laoding of table objects based on reading from an existing database; will get a table object back!
# introspection of a table
metadata2 = MetaData()
with engine.connect() as conn:
    # like we would with creating a table, instead we do not add columsn and we do set the autoload_with
    user_reflected = Table('user', metadata2, autoload_with=conn)
    print(repr(user_reflected))  # info about the user table

# you can also use inspect which can give you more information about the table
from sqlalchemy import inspect

inspector = inspect(engine)  # handle the connection (read only option)

# here are some examples of the values that inspect can give you
print('\n****** inspection ******\n')
print(inspector.get_table_names())
print(inspector.get_columns('address'))
print(inspector.get_foreign_keys('address'))

# if you want to reflect an entire schema you can do the following
metadata3 = MetaData()
with engine.connect() as conn:
    metadata3.reflect(conn) # note this will return a none
    print(metadata3.tables.keys()) # have to use the actual metadata3 object
    print(metadata3.tables['user']) # similar to the above when reflecting a single table we can mess around


# finally we can make sql statements on reflected tables; kinda like a view?
print('\n*****sql statements on a reflected table*****\n')
statment = select([user_reflected])
print(statment) # this is our statement

# again we can preform the following in order to apply the statement
print('\nfrom engine.execute\n')
result = engine.execute(statment) # we can execute the statement
print(list(result))
print('\nfrom engine.connect() as conn\n')
with engine.connect() as conn:
    result = conn.execute(statment)
    print(list(result))


print('*********************************** create/delete all **********************************************************')

engine = create_engine('sqlite:///some.db')
metadata4 = MetaData()

test_table = Table(
    'test',
    metadata4,
    Column('id',Integer,primary_key=True),
    Column('color',Text)
)

test_table2 = Table(
    'test',
    metadata4,
    Column('id',Integer,primary_key=True),
    Column('color',Text)
)

# all currently accept a conn object, but can use an engine object
# up in the air if this will continue

# with engine.connect() as conn:
#     metadata4.drop_all(conn) # deletes all tables associated with this metadata instance
#     metadata4.create_all(conn) # creates all tables associated with this metadata instance
#     test_table2.drop(conn) # deletes table from the created table object
#     test_table2.create(conn) # creates a table from the created table object



