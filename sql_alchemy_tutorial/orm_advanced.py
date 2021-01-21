from sqlalchemy import MetaData, Table, Column, String, Integer, select, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

print('*********************************** setup *********************************************************************')

# a relationship is going to not only have the table User and Address have a relationship by a foreign key
# but the orm will have additonal directives that will have the objects in the collection to presist
Base = declarative_base()


class User(Base):
    __tablename__ = 'user5'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    fullname = Column(String)

    # so what this would be mean is that for addresses, it is a relationship to the table Address and back
    # populateds user; so the first arg would be the table name of the other table that is connected
    # and the second arg is the attribute to relates back to, in this case the user attribute found in the Address
    # table
    addresses = relationship('Address', back_populates='user')

    def __repr__(self):
        return f'User:{(self.username, self.fullname)}'


# we can create a relationship between User and Address by using relationship
# note that we are still responsible for creating the foreign key
class Address(Base):
    __tablename__ = 'address2'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(ForeignKey('user5.id'), nullable=False)

    user = relationship('User', back_populates='addresses')

    def __repr__(self):
        return f'Address {self.email_address}'


engine = create_engine('sqlite:///some.db')

session = Session(bind=engine)

# run once to get the data *********************************************************************************************
run_this = False
if run_this:
    with engine.begin() as conn:
        Base.metadata.create_all(conn)


    session.add_all(
        [
            User(username='spongebob', fullname='spongebob squarepants'),
            User(username='sandy', fullname='sandy cheeks'),
            User(username='patrick', fullname='patrick star'),

        ]
    )
    session.commit()
# run once to get the data *********************************************************************************************

print('*********************************** relationship in action ****************************************************')


squidward = User(username='squidward',fullname='squidward tentacles')
# have an addresses attribute due to the relationship
print(squidward.addresses)

squidward.addresses = [
    Address(email_address='squidward@gmail.com'),
    Address(email_address='s25@yahoo.com'),
    Address(email_address='squiward@hotmail.com')
]

# so we can add some addresses to squidward
# and we can look at one of the addresses, if you pull up the user attribute we get the squidward (User class) we
# created above. Essentially this has handled the many-to-one/one-to-many relationship
# so when we set the address, those addresses also set the user to point to the squidward object
print(squidward.addresses)
print(squidward.addresses[1].user)
print(squidward.addresses[1].user)
# now that we have added squidward to the session, it will cascade and add the addresses in as well
session.add(squidward)
print(session.new)

if run_this:
    session.commit()

# so essentially you can do a lot of your work with using the orm and in turn the session, and then just
# commit, so create your tables, relationships, etc, and then commit.

print('*********************************** collections and references*************************************************')

# so this is an example of the pythons back_populates keyword working
# so what is happening is that we set the attribute spongebob to a result of a query from the database
# next we set the user attribue of first address of the squidward object to spongebob
# since we did that what will happen is that squidward will now lose that address in his addresses attribute,
# while spongebob will get that address;
spongebob = session.query(User).filter_by(username='spongebob').one()
print(spongebob.addresses)
squidward.addresses[1].user = spongebob
print(squidward.addresses)
print(spongebob.addresses)
if run_this:
    session.commit()

print('*********************************** querying multiple tables***************************************************')

print('\n an example of querying multiple tables')
for row in session.query(User,Address).filter(User.id == Address.user_id):
    print(row)

print('\n an example of using join and multiple tables')
print(session.query(User,Address).join(Address).all())
# you can add and explicit on clause
print(session.query(User,Address).join(Address,User.id == Address.user_id).all())

print('\n an example of using join based on the relationships')
print(session.query(User.username).join(User.addresses).filter(
    Address.email_address == 'squidward@gmail.com'
).first())

print('*********************************** alias for orm *************************************************************')

from sqlalchemy.orm import aliased

a1,a2 = aliased(Address),aliased(Address)
print(session.query(User).join(a1).join(a2).filter(
    a1.email_address == 'squidward@gmail.com'
).filter(a2.email_address == 'squidward@hotmail.com').all())


print('*********************************** subquery ******************************************************************')

# we can also use subquries like so
from sqlalchemy import func

# here we are wanting to query for count of address ids and address user id, group by address user id
subq = (
    session.query(func.count(Address.id).label('count'),Address.user_id)
    .group_by(Address.user_id)
    .subquery()
)


# next we want to query for User username, coalesce of the count col from the subquery (remember, we pretty much get
# a table like object and thus we have a c attribute we can access). We then want to outerjoin the subquery, on
# User.id == subq.c.user_id and finally get all results .
print(session.query(User.username,func.coalesce(subq.c.count,0)).outerjoin(
    subq,User.id == subq.c.user_id
).all())


print('***********************************  Eager Loading ************************************************************')
# may want to go over this some more

# so there is a problem called the N pls one problem with ORM; which refers to the many select statements emitted when
# loading collections against a parent result. So you get lots of queries and its slow.
print('\nnormal query loop')
for user in session.query(User):
    print(user,user.addresses)

# eager loading tells the orm to load all the collections in one shot.
from sqlalchemy.orm import selectinload
print('\nselectinload eager loading')
for user in session.query(User).options(selectinload(User.addresses)):
    print(user,user.addresses)

# another option is join load which runs one query and preforms a JOIN (or INNER JOIN) to load both parent and child
# good for many to one loads
from sqlalchemy.orm import joinedload
print('\njoinedload example')
for address_obj in session.query(Address).options(
    joinedload(Address.user,innerjoin=True)
):
    # again we can get the user.username from the address_obj, since we have a relationship and an attribute called user
    print(address_obj.email_address,address_obj.user.username)
