#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:21:06 2017

@author: kelly
"""

import simpy
import random

RANDOM_SEED = 40
NUM_DATA_BLOCKS = 3
MAX_READ_WRITE_TIME = 200
NUM_REQUESTS = 10
INTERVAL_REQUESTS = 5.0  # Generate new requests roughly every x seconds

"""Use first-come-first-served strategy to avoid starvation"""

env = simpy.Environment()
def source(env, numRequests, interval, readLockArray, writeLockArray):
    """Source generates read/write requests randomly"""
    for i in range(numRequests):
        blockNum = random.randint(0, NUM_DATA_BLOCKS-1)
        readWrite = random.randint(0, 1) # 1/2 probability of read, 1/2 write
        if (readWrite!=0):
            # read block
            name = 'Read%d Block%d' % (i, blockNum)
            requestQueue[blockNum].append(name)
            c = read(env, name, readLockArray, writeLockArray, blockNum, readTime=20)
        else:
            # write to block
            name = 'Write%d Block%d' % (i, blockNum)
            requestQueue[blockNum].append(name)
            c = write(env, name, readLockArray, writeLockArray, blockNum, writeTime=100)       
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, name, readLockArray, writeLockArray, blockNum, readTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))
    
    # If this read is not the first request in the queue, wait
    while (requestQueue[blockNum][0] != name):
        yield env.timeout(1)
    
    # Wait for writeLock.count to be 0
    while writeLockArray[blockNum].count != 0:
        yield env.timeout(1)
        
    with readLockArray[blockNum].request() as req:
        yield req
        requestQueue[blockNum].remove(name)
        wait = env.now - arrive
        
        # We got to the block
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        
        timeReading = random.expovariate(1.0 / readTime)
        if timeReading > MAX_READ_WRITE_TIME:
            timeReading = MAX_READ_WRITE_TIME
    
        yield env.timeout(timeReading)
        print('%7.4f %s: Finished' % (env.now, name))
        
def write(env, name, readLockArray, writeLockArray, blockNum, writeTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))

    # If this write is not the first request in the queue, wait
    while (requestQueue[blockNum][0] != name):
            yield env.timeout(1)
            
    # Wait for readLock.count to be 0
    while readLockArray[blockNum].count != 0:
        yield env.timeout(1)
        
    with writeLockArray[blockNum].request() as req:
        # Wait for the block to be free from reading or writing
        yield req
        requestQueue[blockNum].remove(name)
        wait = env.now - arrive

        # We got to the block
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        
        timeWriting = random.expovariate(1.0 / writeTime)
        if timeWriting > MAX_READ_WRITE_TIME:
            timeWriting = MAX_READ_WRITE_TIME
        
        yield env.timeout(timeWriting)
        print('%7.4f %s: Finished' % (env.now, name))
        

    
# Setup and start the simulation
print('Lab A')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
readLockArray = []
writeLockArray = []
requestQueue = []
for i in range (0,NUM_DATA_BLOCKS):
    readLockArray.append(simpy.Resource(env, capacity=5))
    writeLockArray.append(simpy.Resource(env, capacity=1))
    requestQueue.append([])
    
env.process(source(env, NUM_REQUESTS, INTERVAL_REQUESTS, readLockArray, writeLockArray))
env.run()