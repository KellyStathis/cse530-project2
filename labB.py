#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:21:06 2017

@author: kelly
"""

import simpy
import random

RANDOM_SEED = 40
NUM_DATA_BLOCKS = 1
MAX_READ_WRITE_TIME = 200
NUM_REQUESTS = 10
INTERVAL_REQUESTS = 5.0  # Generate new requests roughly every x seconds
last_request_num = -1;

"""Use timestamp ordering"""

def source(env, numRequests, interval, lastReadTimeArray, lastWriteTimeArray):
    """Source generates read/write requests randomly"""
    for i in range(numRequests):
        global last_request_num
        requestNum = last_request_num + 1
        last_request_num = requestNum
        blockNum = random.randint(0, NUM_DATA_BLOCKS-1)
        readWrite = random.randint(0, 1) # 1/2 probability of read, 1/2 write
        if (readWrite!=0):
            # read block
            name = 'Read%d Block%d' % (requestNum, blockNum)
            c = read(env, requestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, readTime=20)
        else:
            # write to block
            name = 'Write%d Block%d' % (requestNum, blockNum)
            c = write(env, requestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, writeTime=100)       
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, requestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, readTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))
    
    # Update last read time before read
    #lastReadTimeArray[blockNum] = requestNum
    wait = env.now - arrive
        
    # We got to the block (should be no wait for reading)
    print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
    
    timeReading = random.expovariate(1.0 / readTime)
    if timeReading > MAX_READ_WRITE_TIME:
        timeReading = MAX_READ_WRITE_TIME

    yield env.timeout(timeReading)
    # Update last read time after read
    lastReadTimeArray[blockNum] = requestNum
    print('%7.4f %s: Finished' % (env.now, name))
        
def write(env, requestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, writeTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))
    
    #print('requestNum %d' % requestNum)
    #print('lastReadTimeArray[blockNum] %d' % lastReadTimeArray[blockNum])
    #print('lastWriteTimeArray[blockNum] %d' % lastWriteTimeArray[blockNum])

    # If last read and last write are before current write timestamp
    if (lastReadTimeArray[blockNum] < requestNum and lastWriteTimeArray[blockNum] < requestNum):
        # We can write immediately
        # Update last write time before write
        #lastWriteTimeArray[blockNum] = requestNum
        wait = env.now - arrive

        # We got to the block
        print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
        
        timeWriting = random.expovariate(1.0 / writeTime)
        if timeWriting > MAX_READ_WRITE_TIME:
            timeWriting = MAX_READ_WRITE_TIME
        
        yield env.timeout(timeWriting)
        # Update last write time after write
        lastWriteTimeArray[blockNum] = requestNum
        print('%7.4f %s: Finished' % (env.now, name))
    else:
        # Reissue attempt
        print('Reissue %s' % name)
        global last_request_num
        newRequestNum = last_request_num + 1
        last_request_num = newRequestNum
        name = 'Write%d Block%d' % (newRequestNum, blockNum)
        c = write(env, newRequestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, writeTime=100) 
        env.process(c)
        
# Setup and start the simulation
print('Lab B')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
lastReadTimeArray = []
lastWriteTimeArray = []
for i in range (0,NUM_DATA_BLOCKS):
    lastReadTimeArray.append(-1)
    lastWriteTimeArray.append(-1)
    
env.process(source(env, NUM_REQUESTS, INTERVAL_REQUESTS, lastReadTimeArray, lastWriteTimeArray))
env.run()