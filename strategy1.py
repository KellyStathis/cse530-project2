#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:21:06 2017

@author: kelly
"""

import simpy
import random

RANDOM_SEED = 40
NUM_DATA_BLOCKS = 2
MAX_READ_WRITE_TIME = 200
NUM_REQUESTS = 6
INTERVAL_REQUESTS = 10.0  # Generate new requests roughly every x seconds
numReads = 0
numWrites = 0

env = simpy.Environment()
def source(env, numRequests, interval, readLockArray, writeLockArray):
    """Source generates read/write requests randomly"""
    for i in range(numRequests):
        blockNum = random.randint(0, NUM_DATA_BLOCKS-1)
        readWrite = random.randint(0, 3) # 3/4 probability of read, 1/4 write
        if (readWrite!=0):
            # read block
            c = read(env, 'Read%d Block%d' % (i, blockNum), readLockArray, writeLockArray, blockNum, readTime=20)
        else:
            # write to block
            c = write(env, 'Write%d Block%d' % (i, blockNum), readLockArray, writeLockArray, blockNum, writeTime=100)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, name, readLockArray, writeLockArray, blockNum, readTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))
    
    # Wait for writeLock.count to be 0
    while writeLockArray[blockNum].count != 0:
        yield env.timeout(1)
        
    with readLockArray[blockNum].request() as req:
        yield req
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

    # Wait for readLock.count to be 0
    while readLockArray[blockNum].count != 0:
        yield env.timeout(1)
        
    with writeLockArray[blockNum].request() as req:
        # Wait for the block to be free from reading or writing
        yield req
        wait = env.now - arrive

        # We got to the block
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        
        timeWriting = random.expovariate(1.0 / writeTime)
        if timeWriting > MAX_READ_WRITE_TIME:
            timeWriting = MAX_READ_WRITE_TIME
        
        yield env.timeout(timeWriting)
        print('%7.4f %s: Finished' % (env.now, name))
        

    
# Setup and start the simulation
print('Strategy 1')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
readLockArray = []
writeLockArray = []
for i in range (0,NUM_DATA_BLOCKS):
    readLockArray.append(simpy.Resource(env, capacity=5))
    writeLockArray.append(simpy.Resource(env, capacity=1))
    
env.process(source(env, NUM_REQUESTS, INTERVAL_REQUESTS, readLockArray, writeLockArray))
env.run()