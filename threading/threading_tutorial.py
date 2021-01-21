import time
import threading

start = time.perf_counter()  # measure how long script takes


# just a basic example of a sync program that is having to wait around before moving on
# with threading, we will see some benifits when our tasks are I/O bound, (i.e. reading/writing tasks)
# this would be benificial with say sockets, or gui things.

# won't see much benifit if the task is cpu bound, we will want to use parallel processing
# so if we had to do a lot of processing, threads wouldn't help too much.

def do_something():
    print('sleeping 1 second')
    time.sleep(1)
    print('done sleeping')


# do_something()
# do_something()
#
# finish = time.perf_counter()
# print(f'finished in {round(finish-start,2)} seconds(s)')

print('************* threading basics ********************************************************************************')

# older way of doing threading

# so we can set up threads like so
# not just pass in the fucntion without ()
# t1 = threading.Thread(target=do_something)
# t2 = threading.Thread(target=do_something)

# # start the threads
# t1.start()
# t2.start()
#
# # we will need the join method otherwise, we would get an incorrect output
# # this will make sure that the threads have resolved before moving on
# t1.join()
# t2.join()
#
# finish = time.perf_counter()
# print(f'finished in {round(finish-start,2)} seconds(s)')

print('************* threading loop **********************************************************************************')

# so we can start multipel threads using a loop, we must keep track of them in order to join them later
# using a list
# threads = list()
# for _ in range(10):
#     t = threading.Thread(target=do_something)
#     t.start()
#     threads.append(t)
#
# for thread in threads:
#     thread.join()

# finish = time.perf_counter()
# print(f'finished in {round(finish-start,2)} seconds(s)')

print('************* passing args ************************************************************************************')

# def do_something(secs:int) -> None:
#     print(f'sleeping for {secs} second(s)')
#     time.sleep(secs)
#     print('done sleeping')

# # we can pass in args by passing in a list of args like below
# # similar to some factory function classes you ccreated that build a function and then accept args seperately
# threads = list()
# for _ in range(10):
#     t = threading.Thread(target=do_something,args=[3])
#     t.start()
#     threads.append(t)
#
# for thread in threads:
#     thread.join()
#
# finish = time.perf_counter()
# print(f'finished in {round(finish-start,2)} seconds(s)')

print('************* concurrent.futures ******************************************************************************')

# easier way to switch around threads and a newer method of creating threads
# actually do not need the threads module anymore

import concurrent.futures


def do_something(secs: int) -> str:
    print(f'sleeping for {secs} second(s)')
    time.sleep(secs)
    return f'done sleeping for {secs}'


# # want to use a context manager
# with concurrent.futures.ThreadPoolExecutor() as executor:
#     # submit method schedules a function to be executed and returns a future object
#     # the future object allows us to check in on it and see what is going on
#     # if we want this to run multiple times, we can do that by running submit multiple times
#     f1 = executor.submit(do_something,1)
#     f2 = executor.submit(do_something,1)
#     # use the result method to get a return; it will wait around until the function completes
#     print(f1.result())
#     print(f2.result())
#
#     # you can use a loop like the above with the threads
#     secs = [5,4,3,2,1]
#     # so here we are are submiting the do_somthign fucntion for a number of secs
#     results = [executor.submit(do_something,sec) for sec in secs]
#     # to get the results, we can use the as_completed method
#     # so the as_completed will print out when in the order things are completed
#     for f in concurrent.futures.as_completed(results):
#         print(f.result())
#
# finish = time.perf_counter()
# print(f'finished in {round(finish-start,2)} seconds(s)')

print('************* concurrent.futures executor map *****************************************************************')

# instead of using a loop like above you can use the map method in executor which is similar to the built in map
# method

# context manager will auto join when everything finishes
# handles the join()
with concurrent.futures.ThreadPoolExecutor() as executor:
    secs = [5, 4, 3, 2, 1]
    # like map, needs a function and an iterable
    # using map, we get results rather than a future object
    # this will return results in the order they were started, rather then when they completed
    # with how this is set up, it will look like everything was returned at the same time

    results = executor.map(do_something,secs)
    for result in results:
        print(result)

finish = time.perf_counter()
print(f'finished in {round(finish - start, 2)} seconds(s)')
