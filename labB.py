#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:21:06 2017

@author: kelly
"""

import simpy
import random
import numpy

RANDOM_SEED = 40
NUM_DATA_BLOCKS = 70
MAX_READ_WRITE_TIME = 100
NUM_REQUESTS = 1400
INTERVAL_REQUESTS = 10.0  # Generate new requests roughly every x seconds
last_request_num = -1
total_writes = 0
invalid_writes = 0
percentage_array = []

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
            global total_writes
            total_writes = total_writes + 1
            c = write(env, requestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, writeTime=100)       
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def read(env, requestNum, name, lastReadTimeArray, lastWriteTimeArray, blockNum, readTime):
    arrive = env.now
    print('%7.4f %s: Received' % (arrive, name))
        
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
    
    timeWriting = random.expovariate(1.0 / writeTime)
    if timeWriting > MAX_READ_WRITE_TIME:
        timeWriting = MAX_READ_WRITE_TIME
    
    yield env.timeout(timeWriting)
  
    # If last read and last write are before current write timestamp
    if (lastReadTimeArray[blockNum] < requestNum and lastWriteTimeArray[blockNum] < requestNum):
        # We can write immediately
        # Update last write time after write
        lastWriteTimeArray[blockNum] = requestNum
        print('%7.4f %s: Finished' % (env.now, name))
    else:
        # Reissue attempt
        global last_request_num
        newRequestNum = last_request_num + 1
        last_request_num = newRequestNum
        newName = 'Write%d Block%d' % (newRequestNum, blockNum)
        global invalid_writes
        invalid_writes = invalid_writes + 1
        print('Reissue %s as %s' % (name, newName))

        c = write(env, newRequestNum, newName, lastReadTimeArray, lastWriteTimeArray, blockNum, writeTime=100) 
        env.process(c)

for rs in range(20, 220, 20):
    # Setup and start the simulation
    print('Lab B')
    random.seed(rs)
    env = simpy.Environment()

    # Start processes and run
    lastReadTimeArray = []
    lastWriteTimeArray = []
    for i in range (0,NUM_DATA_BLOCKS):
        lastReadTimeArray.append(-1)
        lastWriteTimeArray.append(-1)
        
    env.process(source(env, NUM_REQUESTS, INTERVAL_REQUESTS, lastReadTimeArray, lastWriteTimeArray))
    env.run()
    f = open('results.txt', 'a')
    f.write('Run %d:\n' % (rs/20))
    f.write('Total writes: %d\n' % total_writes)
    f.write('Invalid writes: %d\n' % invalid_writes)
    f.write('Percentage of invalid writes: %7.4f%%\n' % (float(invalid_writes*100)/float(total_writes)))
    f.close()
    print('Total writes: %d' % total_writes)
    print('Invalid writes: %d' % invalid_writes)
    print('Percentage of invalid writes: %7.4f%%' % (float(invalid_writes*100)/float(total_writes)))
    percentage_array.append((float(invalid_writes*100)/float(total_writes)))
f = open('results.txt', 'a')
f.write('Total average percentage of invalid writes: %7.4f%%' % numpy.average(percentage_array))
f.close()