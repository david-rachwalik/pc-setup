#!/usr/bin/env python

# Basename: multiprocess_boilerplate
# Description: Common business logic for processes
# Version: 0.4
# VersionDate: 4 Feb 2020

# --- ProcessEvent Commands ---
# .Run, .IsRunning

# --- ProcessPool Commands ---
# .Close, .RunAsync, .await_results

from logging_boilerplate import *
import multiprocessing
import time, random

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Classes ------------------------

class ProcessEvent(object):
    def __init__(self):
        logger.debug("(ProcessEvent:__init__): Init")
        # Initial values
        self.running = bool()
        self.event = multiprocessing.Event()
    

    def Run(self):
        try:
            self.event.set()
        except:
            return False
        return True


    def IsRunning(self):
        return self.event.is_set()


class ProcessPool(object):
    def __init__(self):
        logger.debug("(ProcessPool:__init__): Init")
        # Initial values
        self.running = bool()
        self.pool = multiprocessing.Pool()
    

    def Close(self):
        self.pool.close()
        self.pool.join()
    

    def RunAsync(self, func, args_list):
        if not callable(func):
            self.running = False
            return
        try:
            # map_async recommended over apply_async (not used in Python3)
            self.processes = pool.map_async(func, args_list)
            self.running = True
        except:
            self.running = False
        return self.running


    def await_results(self):
        self.Close()
        if running:
            # results = [p.get() for p in self.processes]
            results = self.processes.get()
            return results
        else:
            return None


# Supports either a single function with list of args
# OR takes a list of functions with a list of list of args (lengths must match)
def ProcessPoolAwait(func, args_list, callback=None, log=None):
    if not (callable(func) and isinstance(args_list, list)): return
    pool = ProcessPool(log=log)
    pool.RunAsync(func, args_list)
    results = pool.await_results()
    return results


# Supports either a single function with list of args
# OR takes a list of functions with a list of list of args (lengths must match)
def ProcessPoolAsync(func, args_list, callback=None):
    if not callable(func): return
    # Create pool and args enumerable
    pool = multiprocessing.Pool()
    # Run async processes, close pool, await (join), gather results
    # recommended over apply_async, which isn't used anymore in Python3
    processes = pool.map_async(func, args_list)
    pool.close()
    pool.join()
    # results = [p.get() for p in processes]
    results = processes.get()
    return results


def rando(args):
    # print("rando init")
    if isinstance(args, tuple):
        (in_num, tester) = args
    else:
        raise TypeError("rando() requires tuple")
    num = random.random()
    print("{0} '{1}' in with rando: {2}".format(in_num, tester, num))

    try:
        data[in_num] = num
    except:
        print("rando nope!")
    
    result = dict()
    result[in_num] = num
    return result


def rng_generate(in_num, tester):
    # print("rng_generate): Init")
    num = random.random()
    print("{0} '{1}' in with rng_generate: {2}".format(in_num, tester, num))
    try:
        data[in_num] = num
    except:
        print("rng_generate): Nope!")
    
    result = dict()
    result[in_num] = num
    return result


data = {}

def end_print(start_time):
    end_time = time.time() - start_time
    print("time taken: {0}".format(end_time))
    print("")


def data_callback(pack):
    # print("data_callback): Init")
    for (key, val) in pack.items():
        # print("key: {0}".format(key))
        # print("val: {0}".format(val))
        data[key] = val


# def timer((func, *args, **kwargs)):
def timer(args):
    if not isinstance(args, tuple):
        raise TypeError("timer() expects tuple parameter")
    (func, val) = args
    if not callable(func):
        raise TypeError("timer() requires 1st arg to be a function")

    start_time = time.time()
    func(val)
    end_time = time.time() - start_time

    print("val: {0}".format(num))
    print("end time: {0}".format(end_time))
    print("")


def random_num():
    num = random.random()
    print(num)


def worker():
    # """worker function"""
    # print("Worker pid: {0}".format(os.getpid()))
    # print("Worker process name: {0}".format(multiprocessing.current_process().name))
    name = multiprocessing.current_process().name
    print("{name}, starting...")
    time.sleep(2)
    print("{name}, exiting...")


def my_service():
    name = multiprocessing.current_process().name
    print("{name}, starting...")
    # print("Worker pid: {0}".format(os.getpid()))
    # print("Worker process name: {0}".format(multiprocessing.current_process().name))
    time.sleep(3)
    print("{name}, exiting...")



# ------------------------ Test Program ------------------------

# socket_listener()
def MultiprocessSocketTester(hostName, hostPort, log=None):
    # Initialize the logger
    logger = get_logger(log)
    logger.debug("(MultiprocessSocketTester): Init")

    # Create server socket to communicate with clients
    serverSocket = SocketContext(log=logger)
    connected = serverSocket.ConnectAsServer(hostName, hostPort)
    if not connected:
        logger.debug("(MultiprocessSocketTester): not connected")
        Fail()

    # Signal the main thread that we are up and listening
    logger.info("Socket listener started and listening on {0}:{1}".format(hostName, hostPort))


    logger.debug("(MultiprocessSocketTester): ACTION METHOD")

    # Create server socket to communicate with clients
    serverSocket = SocketContext(log=self.loggerOptions)
    connected = serverSocket.ConnectAsServer(self.hostName, self.config.hostPort)
    if not connected: self.Fail()

    # Signal the main thread that we are up and listening
    bindString = "{0}:{1}".format(self.hostName, self.config.hostPort)
    logger.info("Socket listener started and listening on {0}".format(bindString))

    # Create a holder for our client threads
    clients = {}
    # Accept connections until told to stop
    newConn = False
    while True:
        # Wrap the blocking accept in a try because it will raise
        # an error when the timeout set by 'settimeout' is reached
        # This allows us to break out and periodically check if we
        # need to exit or not.
        try:
            (conn, addr) = serverSocket.accept()
            newConn = True
        except socket.timeout:
            logger.debug("Socket timed out waiting for a client.")
        
        if newConn:
            # Create args enumerable and run against process pool
            args_list = [(conn, addr)]
            results = ProcessPoolAsync(self.socket_client, args_list)
            # Print results
            print("results: {0}".format(results))

            # Launch a new thread to service the client
            clThread = threading.Thread(target=self.socket_client, args=(conn, addr))
            clThread.start()
            addrString = ':'.join([str(x) for x in addr])
            clients[clThread] = addrString
            newConn = False
        # If we are requested to die, break out of the while loop
        if self.killSocketEvent.is_set():
            logger.warning("Socket listener (" + bindString + ") detected exit request, exiting.")
            break
        else:
            continue

    # After the socket server/listener exits wait for clients to finish
    while len(clients) > 0:
        for thrd in clients.keys():
            if thrd.is_alive():
                logger.debug("Waiting for client to disconnect: " + clients[thrd])
            else:
                clients.pop(thrd)
        sleep(1)

    # When finished accepting connections clean up the socket
    serverSocket.Close()
    logger.info("Socket listener shutdown (" + bindString + ")")


# ------------------------ Main Program ------------------------

# Initialize the logger
basename = "multiprocess_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    iterations = range(10)

    # --- MAP ASYNC ---

    start_time = time.time()
    # Create args enumerable and run against process pool
    args_list = []
    for i in iterations: args_list.append((i, "test"))
    results = ProcessPoolAsync(rando, args_list)
    # Print results
    print("results: {0}".format(results))
    end_print(start_time)


    # --- MAP ASYNC (class) ---
    
    start_time = time.time()
    # Create args enumerable and run against process pool
    args_list = []
    for i in iterations: args_list.append((i, "test"))
    results = ProcessPoolAwait(rando, args_list)
    # Print results
    print("results: {0}".format(results))
    end_print(start_time)


    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/multiprocess_boilerplate.py
    # ps -eaf | grep -i python
