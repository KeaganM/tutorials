'''

some notes:
    - Object relational mapping is the process of associating objects oriented classes with database tables
    - most basic task it translate between a domain obejct and a table row
    - can query the database in terms of the domain model structure
    - some orms can represent class inheritance
    - some can hadle sharding or sotring a domain model across multiple schemas
    - provide various patterns for concurrency  including row versioning
    - provide patterns for data validation and coercion

flavors of orm
    - active record:when you have an object that representings row in the db, its responseible for its on persistance
        user_record = User(name='ed,'fullname='ed jones')
        user_record.save()

    # *** most familar with this one ***
    - data mapper: you have objects and there is a central coordinational system to matches up everything
        dbsession = Session()
        user_record = User(name='ed,'fullname='ed jones')
        dbsession.add(user_record)

    - some configurational styles include:
        - declarative style where class and table information is together:
            class User(Base):
                __tablename__ = 'user'
                id=Column(INterger,primary_key=True)
                name=Column(String(length=50))
                fullname = Column(String(length=100))

- sql alchemy orm is essentailly a data mapper style orm
- modern versions us declarative configuration, domain/schema separate config model is present underneath this layer
- this orm builds upon sqlalchemy core, all sql expression langaguge concepts are present when working with the orm
- the orm presents a domain-model centric view of data in contrast to the schema centric view sql language presents.

Key orm patterns
    - unit of work: objects maintained by a system track changes over the course of a transaction, and flushes pending
        changes periodically in a transparant or semi-transparent manner
    - identity map: objecst are tracked by their pimrary key within the unit of work, and are kept unique on that
        primary key identity
    - lazy loading: Some attributes of an object may emit additional sql queries when they are accessed
    - eager loading: attributes are loaded immediately, related table smay be loaded using joins to the primary
        select statement or additional queries can be emitted.
    -
'''

from sqlalchemy import MetaData, Table, Column, String, Integer, select, create_engine


print('*********************************** declarative system ********************************************************')


# the primary system used to ocnfigure object relational mappings
# basically a class that we subclass, we have a table metadata and columns we create
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Very similar to how we would create a table like before
# also see this using flask-models
class User(Base):
    __tablename__ = 'user4'

    id = Column(Integer,primary_key=True)
    username = Column(String)
    fullname = Column(String)

    def __repr__(self):
        return f'User:{(self.username,self.fullname)}'

print('\nsame table object we were using before')
print(User.__table__)
print('\nmapper object (dont worry about this)')
print(User.__mapper__)

print('\nwe can create a new User object')
spongebob = User(username='spongebob',fullname='spongebob squarepants')
print(spongebob)
print(spongebob.__dict__)
# we can access a column; id is defaulted to None
print(repr(spongebob.id))

print('*********************************** create a table ********************************************************')

engine = create_engine('sqlite:///some.db')
with engine.begin() as conn:
    # similar to before we are essentially using the metadata to create all the tables, which is in the declarative_base
    # class
    Base.metadata.create_all(conn)

print('*********************************** Sessions ********************************************************')

from sqlalchemy.orm import Session

engine = create_engine('sqlite:///some.db')

# a data mapper orm style uses a coordination layer, which is what the session object does
# the session will deal with the engine.connect()/.begin()
# handles the job of starting transaction, committing, and interpretation

session = Session(bind=engine)

spongebob = User(username='spongebob',fullname='spongebob squarepants')

# nothing will happen just yet
session.add(spongebob)
# when something is added to the session, it gets added to a list of pending objects which we can see below using
#   .new
# these are objects that will be inserted when we tell it to; it doesn't do it yes since we are in the middle of a
# transaction and we need to call commit; think of it like you get all your work out the door when it is all done.
# it is implicitly in a transactional state.
print(session.new)

# this says hey session we want to query the User table, and filiter where username = spongebob and thats it
# that is until you call .first(); so the select does not do anything with the database if it does not need to, up
# until the point where it actually needs to run the query.
also_spongebob = session.query(User).filter_by(username='spongebob').first()
# so we will get a result back in this instance, however there still will not be spongebob inputted into the db
# that is again due to the fact that we are in a transactional state, so select was like let me push in what
#   I have and then do this.
print(also_spongebob)


# so when we want to put stuff in the database, it will call flush (automatically so we don't have to worry)

# we can add some more objects (like session.add)
session.add_all(
    [
        User(username='patrick',fullname='patrick start'),
        User(username='sandy',fullname='sandy cheeks')
    ]
)

# we can make changes to an exisiting object; consider a dirty object
spongebob.fullname = 'Spongebob Jones'
print(session.new) # pending objects
print(session.dirty) # dirty/presistent objects

# commit a transaction
session.commit()

# once you have committed, you will start a new transaction and relaod from the database


print('*********************************** Rolling Back Changes ******************************************************')

# lets make a dirty change and a pending change that we might want to change our minds about
spongebob.username = 'Spongy'
fake_user = User(username='fakeuser',fullname='invalid')
session.add(fake_user)

# so first lets go ahead and make a query which will flush
# again we are in a transaction so nothing has really been  commited to the database just yet.
print(session.query(User).filter(User.username.in_(['Spongy','fakeuser'])).all())

# but we don't want the above so lets rollback
# again if we want to rollback changes, as long as we don't commit (remain in a transaction) we can rollback
session.rollback()
print(spongebob.username)
print(session.query(User).filter(User.username.in_(['spongebob','fakeuser'])).all())


print('*********************************** ORM Querying ******************************************************')

# like a column but not (has a column in it)
print(User.username == 'spongebob')
print(repr(User.username)) # acts like a column

# with the order_by, it is simlar to how we were doing it before when we were making expressions
query = (
    session.query(User).filter(User.username == 'spongebob').order_by(User.id)
)

# gives me a list of User objects
print(query.all())
print('\n for loop with tuple')
# you can also create a for loop that can query like so, where you have tuple composed of the User columns
for username, fullname in session.query(User.username, User.fullname):
    print(username,fullname)
print('\nfor loop with row:')
# or you can create a for loop that loops over rows
for row in session.query(User,User.username):
    print(row.User,row.username)

# make use of the filter by like so
print('\nfor loop with filter_by:')
for (username,) in session.query(User.username).filter_by(
    fullname='Spongebob Jones'
):
    print(username)

# if you want to use things like select, where, etc..
# we can use .filter() like so
print('\nfor loop using filter with where and or_')
from sqlalchemy import or_
for user in (
    session.query(User)
    .filter(User.username == 'spongebob') # want username to equal spongebob
    .filter(or_(User.fullname == 'Spongebob Jones',User.id < 5)) # and want fullname to be spongebob jones or userid to be < 5
):
    print(user)

# for a variaty of return
print('\n differnt kinds of returns')
query = session.query(User).filter(User.username == 'spongebob').order_by(User.id)
print(query.all()) # get a list
print(query.first()) # get a single object
# print(query.one())


print('*********************************** Filter and Binary Expressions *********************************************')

# filter accepts an object called a binary expression and essentially accepts *args
# however, filter_by accepts only **kwargs and just wants things like username='foo',fullname='bar'
expr = User.username == 'spongebob'
print(repr(expr))
q = session.query(User).filter(expr) # you can pass in expr; its accepting *args
print(q.all())
q2 = session.query(User).filter_by(username='spongebob') # filter_by accepts **kwargs
print(q2.all())