'''

The sql expression system builds on the table metadata to make sql statements in python

we can build python objects that represent individual sql statements that we want to send to the database
     these are composed of other objets that represents some unit of sql such as a comparison, select statement a
     conjunction like AND or OR

we can work with these objects in python which are converted to strings when we execute

sql expressions in both core and orm variants rely heavily on method changing (i.e. object.method1.method2.method3....)

For the following expressions and code, the idea is to create an expression that will be compiled and sent to the
    db to run. For example, when we do table.c.username == 'keagan' we are essentially tieing in the expression:

    username == 'keagan'

    into the statement. When we select with the above expression like so

    (select([table.username.c]).where(user_table.c.username == 'keagan'))
    we will get the following:

    SELECT table.username
    FROM table
    WHERE table.username == 'keagan'


it looks like there are two major ways of designing expresions:
    1. table.update.values(column=new_value)
    2. engine.execute(table.update,{column1:value1,column2:value2})
'''

print('*********************************** basic **********************************************************')
# get the table set up

from sqlalchemy import MetaData, Table, Column, String, Integer, select, create_engine

metadata = MetaData()

user_table = Table(
    'user2',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50)),
    Column('fullname', String(50))
)

engine = create_engine('sqlite:///some.db')
# doing read/write us begin(), just doing read use connect()
with engine.begin() as conn:
    metadata.create_all(conn)

print('*********************************** and/or **********************************************************')

# with user_table.c we can make expressions like so
# a main thing about sqlalchemy is that you can make expressions by overloading python operators such as
#   __eq__, __ne__, etc...


print(str(user_table.c.username == 'spongebob'))  # get this if you stringify it

# compile objects
print((user_table.c.username == 'spongebob').compile().params)  # when you do compile and params you get paramaters
print((user_table.c.username == 'spongebob').compile().string)  # what you get when you use the string

# you can combine ColumnElements to produce more ColumnElements
# makes use of the bitwise operator (| or OR)
print(
    (user_table.c.username == 'spongebob') | (user_table.c.username == 'patrick')
)

# can use and_ or or_ as well
from sqlalchemy import and_, or_

print(
    and_(
        user_table.c.fullname == 'spongebob squarepants',
        or_(user_table.c.username == 'spongebob', user_table.c.username == 'patrick')
    ),
)

print('*********************************** comparisons **********************************************************')

# examples of comparisons
print(user_table.c.id > 5)
print(user_table.c.fullname == None)
print(user_table.c.fullname != None)

# using the + operator may mean to add if given an int or concate if given a string
print(user_table.c.id + 5)
print(user_table.c.fullname + 'Jr.')

# making use of the in operator
print(user_table.c.username.in_(['sandy', 'squidward', 'spongebob']))
print(user_table.c.username.in_(['sandy', 'squidward', 'spongebob']).compile().params)
with engine.connect() as conn:
    res = conn.execute(select([user_table.c.username.in_([])]))

print('*********************************** dialects **********************************************************')

# we can apply a dialect to an expression for various databases
expression = user_table.c.fullname + " Jr."

from sqlalchemy.dialects import postgresql, sqlite

# essentially this allows sqlalchemy to be database agnostic; or have an ability to define expressions apporpriately
# for a database
print(expression.compile(dialect=postgresql.dialect()))
print(expression.compile(dialect=sqlite.dialect()))

print('*********************************** insert **********************************************************')

# we can use the insert construct to insert some data
# essentially we are making the statement here, and then applying it below in the execute statement
insert_stmt = user_table.insert().values(
    username='spongebob', fullname='spongebob sdquarepants'
)

engine = create_engine('sqlite:///some.db')
# doing read/write (transaction) lets use begin()
# again because we are on a context manager, it will auto commit and close by itself.
with engine.begin() as conn:
    conn.execute(insert_stmt)

# you can also insert many rows at the same time by doing the following
with engine.begin() as conn:
    # this is another format where we just pass in the insert() method along with the data we want inserted
    # similar to one way of adding to a pandas df, where you have a dictionary of column names (keys) and the data
    #    to be inserted (values)
    conn.execute(
        user_table.insert(), {'username': 'squid', 'fullname': 'squidward tenticles'},

    )
    # finally we can do the same thing like we did above, but insert it into a list if we have more than one row
    #   we want to insert
    conn.execute(
        user_table.insert(), [
            {'username': 'patrick', 'fullname': 'patrick star'},
            {'username': 'sandy', 'fullname': 'sandy cheeks'},
        ]
    )

print('*********************************** select **********************************************************')

# note, you can chain in whatever order you want but subqueries you will want to stay in order
# for example, I could have my select().order_by().where() and it should get put together in the right order.
# it might be easier to just keep everything in the right order
# note the from clause is automatically added

from sqlalchemy import select

# to make a select statement you will first want to use the select function, followed by a list of column names.
# if you want to add a where clause, you will want to chain (method chaining) where to the select function, and
# add in your clause like below
# equal to: SELECT user.username, user.fullname FROM user where user.username == 'spongebob'
select_stmt = select([user_table.c.username, user_table.c.fullname]).where(
    user_table.c.username == 'spongebob'
)

# next all you need to do is pass it in like you would any other statement to be executed
engine = create_engine('sqlite:///some.db')
with engine.begin() as conn:
    print('loop over rows')
    res = conn.execute(select_stmt)
    # you get a sequence object back from the result
    for row in res:
        print(row)

    # or do fetch all
    print('fetch all')
    res2 = conn.execute(select_stmt).fetchall()
    print(res2)

# to get all the columns just create a generic select statement like so
# where we just pass in the table object we are working with
print('get all columns back from table')
select_stmt2 = select([user_table])
# kinda don't want to do this necessiarly but for this example whatever
res3 = engine.execute(select_stmt2).fetchall()
print(res3)

print('*********************************** where,order by, or_, and_ *************************************************')
# here are more example of using where, order_by, and conditionals

# you can also add an order_by with where like so
print('get columns with where, or_, and orderby used')
select_stmt3 = select([user_table]).where(
    or_(
        user_table.c.username == 'spongebob',
        user_table.c.username == 'sandy'
    )
).order_by(
    user_table.c.username
)
res4 = engine.execute(select_stmt3).fetchall()
print(res4)

print('an advance select with multiple wheres')
# essentially the wheres done like this translate to: WHERE username = 'spongebob' AND fullname = 'spongebob squarepants'
select_stmt4 = (
    select([user_table])
        .where(user_table.c.username == 'spongebob')
        .where(user_table.c.fullname == 'spongebob sdquarepants')
        .order_by(user_table.c.username)
)
res5 = engine.execute(select_stmt4)
print(list(res5))

print('*********************************** update *************************************************')

# here we can create an update statement like so
update_stmt = (
    user_table.update()
        .where(user_table.c.username == 'patrick')
)

# and we can pass in the values to change during the execute
print('updating with just engine and update method')
result = engine.execute(update_stmt, {'fullname': 'Patrick Star'})
print(repr(result))
# which translate to: UPDATE user SET fullname = 'Patrick Star' WHERE username = 'patrick'
# so we update the table user, set the full name to Patrick Star, everywhere the username is equal to 'patrick'

# another method of going about this would be to use the values method
print('updating with values method')
update_stmt2 = user_table.update().values(fullname='x')
print(update_stmt2)

# we can also do things like concate in a values method like below
print('updating with concat')
update_stmt3 = user_table.update().values(
    fullname=user_table.c.username + ' ' + user_table.c.fullname
)
print(update_stmt3)
with engine.begin() as conn:
    res6 = conn.execute(update_stmt3)

print('*********************************** delete *************************************************')

# delete is very similar to update
delete_stmt = user_table.delete().where(user_table.c.username == 'patrick')
res7 = engine.execute(delete_stmt)
print(res7)