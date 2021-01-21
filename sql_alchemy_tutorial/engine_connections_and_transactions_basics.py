from sqlalchemy import create_engine, text
# import logging
#
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
print('*********************************** ***************************************************************************')
print('*********************************** Engine Basics *************************************************************')
print('***********************************  **************************************************************************\n')

print('*********************************** basics **********************************************************')

# loads up the dialect and checks if the url is correct; doesn't really do anything just yet
# the engine is should be global, the connections should not. The engine is like the main source/connection to the
# database while connections are when you want to do something to the database.
engine = create_engine('sqlite:///some.db')
# connection creates the connection between the fb and a connection object; allows access
# Generally want to treat the connection as a file, open, do your stuff, and close; don't leav it open.
connection = engine.connect()

# an example of sending text where you can replace a value in the execute method
# a bit safer than passing in a raw string
smt = text('select emp_id,emp_name from employee where emp_id=:emp_id')
result = connection.execute(smt, {'emp_id': 1})

# to get the actual results you can use fetchone which returns tuples
row = result.fetchone()
# there are multiple ways to access data from a fetched result
print(row)
print(row.keys())
print(row['emp_id'])
print(row.emp_name)

# result does have a cursor object which you can close but you don't have to
result.close()
print('*********************************** iteration **********************************************************')

# here you can get the result and iterate over each of the results
result = connection.execute(text('select * from employee'))
for row in result:
    print(row)

print('*********************************** fetch all **********************************************************')

# another option is to use fetch_all()
result = connection.execute(text('select * from employee'))
# returns a list of tuples
print(result.fetchall())

# Note this will give you a list of strings in 1.4
# result = connection.execute(text('select * from employee'))
# rows = result.scalars('emp_name').all()
# print(rows)

print('*********************************** context manager **********************************************************')
# really want to use a context manager like with to close out a connection and not let the garbage collector handle it
# can also close the connection
connection.close()

# like opening a text file you should use a context manager (with)
# note in 1.4 there may be an all() method you can use instead of fetchall
with engine.connect() as connection:
    result = connection.execute(text('select * from employee'))
    print(result.fetchall())

print('*********************************** begin and committ **********************************************************')

# an example of applying an insert statement
with engine.begin() as connection:
    connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'kristen'})

# we can use a transaction; so here we connect with the engine as a connection object, assign trans to the connection
# which uses the begins method, execute with the connection object and commit the changes; however we can also roll back
# so emily2 was supposedly insertedinto the db, however instead of committing, the trans object rolls back.
with engine.connect() as connection:
    trans = connection.begin()
    connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'emily'})
    trans.commit()
    trans = connection.begin()
    connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'emily2'})
    trans.rollback()


print('*********************************** more context managers **********************************************************')

# like opening up a connection, you can open up a transaction as well which will close automatcially after finishing
with engine.connect() as connection:
    with connection.begin() as trans:
        connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'emily3'})


print('*********************************** save points **********************************************************')
# save points act as a point which you can rollback during a transaction
# there are two examples here

with engine.connect() as connection:
    with connection.begin() as trans:
        # The first example is setting the savepoint explictly like so
        # so you can have a save point set here
        # its like a named marker that you can roll back to when you are in the middle of a transaction
        # which is the connection.begin() as trans
        savepoint = connection.begin_nested()
        # try to execute something
        connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'emily_save_point_before'})
        connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'emily_save_point_before2'})
        connection.execute(text('insert into emp_of_month (name) values (:name)'),{'name':'emily_save_point_before3'})
        # then rollback to when you lasted save
        savepoint.rollback()

        # the second example is using a context manager
        with connection.begin_nested() as savepoint:
            connection.execute(text('insert into emp_of_month (name) values (:name)'),
                               {'name': 'emily_save_point_after'})
        # this would release the save point
        # either or will work

# Note context managers will automatically committ the transaction and if it throws an exception, it will
# roll back


