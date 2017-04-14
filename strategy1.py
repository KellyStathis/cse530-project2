#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:21:06 2017

@author: kelly
"""

import simpy
import random

RANDOM_SEED = 40
#SIMULATION_TIME = 15 # not used
#NUM_DATA_BLOCKS = 1 # need to have multiple data blocks
#MAX_READ_WRITE_TIME = 3 # not used
NUM_REQUESTS = 6
INTERVAL_REQUESTS = 10.0  # Generate new requests roughly every x seconds
numReads = 0
numWrites = 0

env = simpy.Environment()
def source(env, numRequests, interval, readLock, writeLock):
    """Source generates read/write requests randomly"""
    for i in range(numRequests):
        #readWrite = 1
        readWrite = random.randint(0, 3) # 3/4 probability of read, 1/4 write
        if (readWrite!=0):
            # read block
            c = read(env, 'Read%d' % i, readLock, writeLock, readTime=20)
        else:
            # write to block
            c = write(env, 'Write%d' % i, readLock, writeLock, writeTime=100)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, name, readLock, writeLock, readTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))
    
    # Wait for writeLock.count to be 0
    while writeLock.count != 0:
        yield env.timeout(1)
        
    with readLock.request() as req:
        yield req
        wait = env.now - arrive
        
        # We got to the block
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        
        timeReading = random.expovariate(1.0 / readTime)
        yield env.timeout(timeReading)
        print('%7.4f %s: Finished' % (env.now, name))
        
def write(env, name, readLock, writeLock, writeTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))

    # Wait for readLock.count to be 0
    while readLock.count != 0:
        yield env.timeout(1)
        
    with writeLock.request() as req:
        # Wait for the block to be free from reading or writing
        yield req
        wait = env.now - arrive

        # We got to the block
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        
        timeWriting = random.expovariate(1.0 / writeTime)
        yield env.timeout(timeWriting)
        print('%7.4f %s: Finished' % (env.now, name))
        

    
# Setup and start the simulation
print('Strategy 1')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
readLock = simpy.Resource(env, capacity=5)
writeLock = simpy.Resource(env, capacity=1)
env.process(source(env, NUM_REQUESTS, INTERVAL_REQUESTS, readLock, writeLock))
env.run()