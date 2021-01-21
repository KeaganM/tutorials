from sqlalchemy import Table, MetaData, create_engine, Column, Integer, String, ForeignKey, select

print('*********************************** setup **********************************************************')
metadata = MetaData()
user_table = Table(
    'user3',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50)),
    Column('fullname', String(50))
)

address_table = Table(
    'address',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('user3.id'), nullable=False),
    Column('email_address', String(100), nullable=False)
)

print(user_table)
print(address_table)

engine = create_engine('sqlite:///some.db')
with engine.begin() as conn:
    metadata.drop_all(conn)
    metadata.create_all(conn, checkfirst=True)

with engine.begin() as conn:
    conn.execute(
        # remember we can do it this way or use the values method as well; again it is just a list of dictionarys
        # where the keys corresponde to the columns and the values are the pieces of data you want to insert into
        # said column
        user_table.insert(),
        [
            {'user_id': 1, 'username': 'spongebob', 'fullname': 'spongebob squarepants'},
            {'user_id': 2, 'username': 'sandy', 'fullname': 'sandy cheeks'},
            {'user_id': 3, 'username': 'patrick', 'fullname': 'patrick star'}
        ]
    )

    conn.execute(
        address_table.insert(),
        [
            {'user_id': 1, 'email_address': 'spongebob@gmail.com'},
            {'user_id': 1, 'email_address': 'spongebob2@gmail.com'},
            {'user_id': 2, 'email_address': 'sandy@gmail.com'},
            {'user_id': 3, 'email_address': 'patrick@gmail.com'},

        ]
    )

print('*********************************** joins **********************************************************')

# to join an object, we can first use one table and use the join method, then explicitly state which columns
# by accessing columns using the c attribute and setting them equal
# essentially get: 'user' JOIN address ON user.id = address.user_id
# explicitly stating inside the join method is the ON clause
print('join examples')
join_obj = user_table.join(
    address_table, user_table.c.id == address_table.c.user_id
)
print(join_obj)
# you can also do outjoins, and if there is an forign key between two tables, you do not need to
# state an ON clause
print(user_table.outerjoin(address_table))

print('here is our join statement ')
# essentially doing a select statement with a join clause at the end
# remember we can specify which things we want to have returned by doing: table.c.columnname; or if we want everything
#   just use the table object
join_stmt = select([user_table.c.username, address_table.c.email_address]).select_from(join_obj)
print(join_stmt)
with engine.connect() as conn:
    res = conn.execute(join_stmt).fetchall()
    print(list(res))

print('*********************************** aliases **********************************************************')

# used when we want to select from the same table multiple times
# generates an anom name

# for example
address_alias1 = address_table.alias()
address_alias2 = address_table.alias()

select_stmt = (
    select(
        [  # selec the columns you want
            user_table.c.username,
            address_alias1.c.email_address,
            address_alias2.c.email_address,
        ]
    )
        .select_from(user_table.join(address_alias1).join(
        address_alias2))  # join usertable to address_alias1 which is joined to address_alias2
        .where(
        address_alias1.c.email_address == 'spongebob@gmail.com')  # where address_alias1 email is equal to spongebob@gmail.com
        .where(address_alias2.c.email_address == 'spongebob2@gmail.com')
    # where address_alias2 email is equal to spongebob2@gmail.com
)
print(select_stmt)

res2 = engine.execute(select_stmt).fetchall()
print(list(res2))

print('*********************************** subquery **********************************************************')

# if you say .alias() on a select object, you will get a table like object
print('\nsubquery')
select_subquery = (
    select([user_table.c.username, address_alias1.c.email_address])
        .select_from(user_table.join(address_table))
        .alias()
)
print(select_subquery)
print('\nstmt with subquery')
# we an essentially access columns from the sub query since it is like a table object
stmt = select([select_subquery.c.username]).where(
    select_subquery.c.username == 'spongebob'
)
print(stmt)

# here we can illustrate the difference between the table object and the subquery object
print('\naddress_table email address query')
print(select([address_table.c.email_address]))
print('\nsubquery email address query')
print(select([select_subquery.c.email_address]))

print('*********************************** func **********************************************************')

# func acts as a sort of package for various functions
from sqlalchemy import func

# for example, we can use func.count to access the COUNT function, where we take the count of address_table ids and
# label them as count
address_select = (
    select([address_table.c.user_id, func.count(address_table.c.id).label('count')])
        .group_by(address_table.c.user_id) # we can also make use of the group_by function
)
print('\n address select subquery')
# essentially we will get: SELECT address.user_id,count(address.id) AS count FROM address GROUP BY address.user_id
print(address_select)

# turn this into a subq and give it a c attribute (like c in the table object)
address_subq = address_select.alias()

username_plus_count = (
    select([user_table.c.username,address_subq.c.count])
# we don't have to explicitly state the on clause since sqlalchemy will still remember that the user_table and the address table are tied together with a foreign key
    .select_from(user_table.join(address_subq))
    .order_by(user_table.c.username)
)
print('\n username_plus_count query')
print(username_plus_count)

res3 = engine.execute(username_plus_count).fetchall()
print('\n results')
print(list(res3))

print('*********************************** cte (common table expression) *********************************************')

# similar to a subquery

# creates a cte object
address_cte = address_select.cte()
print(repr(address_select))
print(address_select)


# we can use the cte object the same way we use the subquery
# instead of getting a subquery in the from clause we get a common table expression
# adds a with clause to the top
print('\n username plus count with cte')
username_plus_count = (
    select([user_table.c.username,address_cte.c.count])
    .select_from(user_table.join(address_cte))
    .order_by(user_table.c.username)
)
print(username_plus_count)

# they are syntatically the same in python; but they can affect the query plan in a positive way

print('*********************************** scalar subquery *********************************************')

# past subqueries would be a from subquery which returns multiple columns
# a scala subquery is used in the where/columns clause  and returns one row and one column

# work with an aggregate function (like count)
address_corr = (
    select([func.count(address_table.c.id)])
    .where(user_table.c.id == address_table.c.user_id)
    .as_scalar() # denote using this
)
print('\n address corr by itself')
print(address_corr)

print('\n select statement with address corr')
select_stmt2 = select([user_table.c.username,address_corr])
print(select_stmt2)
