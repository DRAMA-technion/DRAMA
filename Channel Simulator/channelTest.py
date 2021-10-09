import Channel as ch
import math
 #
 # (self, channelID=0, numChannels=0, channelMapping=0, numDimms=0, numRanks=0, numBanks=0, busSize=3,
 #                 pageSize=3, channelMemorySize=10, addressRange=[[0, 2 ** 10 - 1]], addressMapping=0,
 #                 cacheBlockSize=6, pageOpenCycles=5, pageClosedCycles=10):
 #

def main():
    print("Start Tests")

    testID = 1
    channelID=0
    numChannels=0
    channelMapping=0
    numDimms=0
    numRanks=0
    numBanks=0
    busSize=3
    pageSize=3
    channelMemorySize=10
    addressRange=[[0, 2 ** 10 - 1]]
    addressMapping=0
    cacheBlockSize=6
    pageOpenCycles=5
    pageClosedCycles=10

    # exp values
    expBusyCycles = 15
    expNumReq = 2
    expNumBytesReturned = 4
    expNumPagesOpened = 1
    # first test : open one page, ask for 3 bytes. then use the same page and ask for 1 more byte.
    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                   channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,testID,
                 expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)
    # second test : Cache Block Interleaving, open new page and use different columns, open page in new row, re-open first page, open page in new dimm, open page in new bank
    testID              = 2
    numChannels         = 1
    numDimms            = 1
    numRanks            = 1
    numBanks            = 2
    busSize             = 2
    pageSize            = 2
    channelMemorySize   = 11
    addressRange        = [[0, 2 ** 11 - 1]]
    addressMapping      = 1
    cacheBlockSize      = 3

    expBusyCycles = 85
    expNumReq = 12
    expNumBytesReturned = 48
    expNumPagesOpened = 5

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    # test 3 : msb, open new page and use different rows
    testID              = 3
    numChannels         = 1
    numDimms            = 1
    numRanks            = 1
    numBanks            = 2
    busSize             = 3
    pageSize            = 2
    channelMemorySize   = 12
    addressRange        = [[0, 2 ** 12 - 1]]
    addressMapping      = 1
    cacheBlockSize      = 3

    expBusyCycles = 70
    expNumReq = 9
    expNumBytesReturned = 36
    expNumPagesOpened = 5

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID,
                 expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    # test 4 : Row Interleaving, open new page and use different columns, open page in new row, re-open first page, open page in new dimm, open page in new bank
    testID = 4
    channelID=0
    numChannels=1
    channelMapping=0
    numDimms=2
    numRanks=1
    numBanks=2
    busSize=2
    pageSize=2
    channelMemorySize=11
    addressRange=[[0, 2 ** 11 - 1]]
    addressMapping=0
    cacheBlockSize=6
    pageOpenCycles=5
    pageClosedCycles=10

    # exp values
    expBusyCycles = 90
    expNumReq = 13
    expNumBytesReturned = 52
    expNumPagesOpened = 5

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    # test 5 : Row Interleaving, different channel
    testID = 5
    channelID = 1
    numChannels = 1
    channelMapping = 0
    numDimms = 2
    numRanks = 1
    numBanks = 2
    busSize = 2
    pageSize = 2
    channelMemorySize = 11
    addressRange = [[2 ** 11, 2 * (2 ** 11) - 1]]
    addressMapping = 0
    cacheBlockSize = 6
    pageOpenCycles = 5
    pageClosedCycles = 10

    # exp values
    expBusyCycles = 90
    expNumReq = 13
    expNumBytesReturned = 52
    expNumPagesOpened = 5

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    # test 6 : Row Interleaving, Channel LSB mapping
    testID = 6
    channelID = 0
    numChannels = 1
    channelMapping = 1
    numDimms = 2
    numRanks = 1
    numBanks = 2
    busSize = 2
    pageSize = 2
    channelMemorySize = 11
    channelAdd = channelID << busSize
    busAdd = (2 ** busSize) - 1
    addressRange = [[(x<<(busSize + numChannels)) + channelAdd, (x<<(busSize + numChannels)) + channelAdd + busAdd]
                    for x in range(2**(channelMemorySize - numChannels))]
    addressMapping = 0
    cacheBlockSize = 6
    pageOpenCycles = 5
    pageClosedCycles = 10

    # exp values
    expBusyCycles = 90
    expNumReq = 13
    expNumBytesReturned = 52
    expNumPagesOpened = 5

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    # test 7 : Row Interleaving, Channel LSB mapping, different channel
    testID = 7
    channelID = 1
    channelAdd = channelID << busSize
    addressRange = [[(x << (busSize + numChannels)) + channelAdd, (x << (busSize + numChannels)) + channelAdd + busAdd]
                    for x in range(2 ** (channelMemorySize - numChannels))]

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    # test 8 : open all pages and check that only one page is open per bank
    testID = 8
    channelID = 0
    numChannels = 1
    channelMapping = 0
    numDimms = 1
    numRanks = 1
    numBanks = 1
    busSize = 1
    pageSize = 1
    channelMemorySize = 6
    addressRange = [[0, 2 ** 6 - 1]]
    addressMapping = 0
    cacheBlockSize = 6
    pageOpenCycles = 1
    pageClosedCycles = 1

    # exp values
    expBusyCycles = 64*2
    expNumReq = 64*2
    expNumBytesReturned = 64*2
    expNumPagesOpened = 16*2

    testSkeleton(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                 channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                 testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened)

    print("EOM")

def testSkeleton (channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                   channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles,
                  testID, expBusyCycles, expNumReq, expNumBytesReturned, expNumPagesOpened):

    # creat new channel
    c = ch.Channel(channelID, numChannels, channelMapping, numDimms, numRanks, numBanks, busSize, pageSize,
                   channelMemorySize, addressRange, addressMapping, cacheBlockSize, pageOpenCycles, pageClosedCycles)

    if testID == 1:
        testOne(c)
    elif testID == 2:
        testTwo(c)
    elif testID == 3:
        test3(c)
    elif testID == 4:
        test4(c)
    elif testID == 5:
        test5(c)
    elif testID == 6 or testID == 7:
        test6_7(c)
    elif testID == 8:
        test8(c)

    # timing calc check
    print("Busy Cycles:" , c.busyCycles)
    assert c.busyCycles == expBusyCycles, "timing error"
    # num req check
    print("Requests:", c.numRequests)
    assert c.numRequests == expNumReq, "req counter error"
    # num bytes returned check
    print("Bytes Returend:", c.numBytesReturned)
    assert c.numBytesReturned == expNumBytesReturned, "num bytes returned error"
    # num pages opened
    print("Pages Opened:", c.numPagesOpened)
    assert c.numPagesOpened == expNumPagesOpened, "num pages opened error"

    print("EOT", testID)

def testOne (channel):
    channel.request(0, [0, 1, 2])
    channel.request(10, [3])

def testTwo(channel):
    channel.request(0,[0,1,2,3])
    channel.request(10, [0,1,2,3])
    channel.request(15, [4,5,6,7])
    channel.request(20, [0,1,2,3])
    channel.request(25, [64,65,66,67])
    channel.request(35, [0,1,2,3])
    channel.request(45, [512,513,514,515])
    channel.request(55, [0,1,2,3])
    channel.request(60, [512,513,514,515])
    channel.request(65, [8,9,10,11])
    channel.request(75, [0,1,2,3])
    channel.request(80, [12,13,14,15])
    channel.request(85, [2**11])

def test3(channel):
    channel.request(0,[0,1,2,3])
    channel.request(10, [0,1,2,3])
    channel.request(15, [4,5,6,7])

    channel.request(20, [9,10,11,12])
    #stall
    channel.request(300, [128,129,130,131])
    channel.request(400, [131,132,133,134])

    channel.request(405, [512,513,514,515])

    channel.request(415, [0,1,2,3])

    channel.request(425, [9, 10, 11, 12])

def test4(channel):
    channel.request(0, [0, 1, 2, 3])
    channel.request(10, [4, 5, 6, 7])
    channel.request(15, [0, 1, 2, 3])
    channel.request(20, [8, 9, 10, 11])
    channel.request(25, [16, 17, 18, 19])
    channel.request(35, [0, 1, 2, 3])
    channel.request(40, [64, 65, 66, 67])
    channel.request(50, [256, 257, 257, 258])
    channel.request(60, [512, 513, 514, 515])
    channel.request(70, [20, 21, 22, 23])
    channel.request(75, [72, 73, 74, 75])
    channel.request(80, [260, 261, 262, 263])
    channel.request(85, [520, 521, 522, 523])
    channel.request(90, [2048])

def test5(channel):
    channel.request(0, [x+2048 for x in [0, 1, 2, 3]])
    channel.request(10, [x+2048 for x in [4, 5, 6, 7]])
    channel.request(15, [x+2048 for x in [0, 1, 2, 3]])
    channel.request(20, [x+2048 for x in [8, 9, 10, 11]])
    channel.request(25, [x+2048 for x in [16, 17, 18, 19]])
    channel.request(35, [x+2048 for x in [0, 1, 2, 3]])
    channel.request(40, [x+2048 for x in [64, 65, 66, 67]])
    channel.request(50, [x+2048 for x in [256, 257, 257, 258]])
    channel.request(60, [x+2048 for x in [512, 513, 514, 515]])
    channel.request(70, [x+2048 for x in [20, 21, 22, 23]])
    channel.request(75, [x+2048 for x in [72, 73, 74, 75]])
    channel.request(80, [x+2048 for x in [260, 261, 262, 263]])
    channel.request(85, [x+2048 for x in [520, 521, 522, 523]])
    channel.request(90, [0])

def test6_7(channel):
    channel.request(0, [lsbTrans(x,channel) for x in [0, 1, 2, 3]])
    channel.request(10, [lsbTrans(x,channel) for x in [4, 5, 6, 7]])
    channel.request(15, [lsbTrans(x,channel) for x in [0, 1, 2, 3]])
    channel.request(20, [lsbTrans(x,channel) for x in [8, 9, 10, 11]])
    channel.request(25, [lsbTrans(x,channel) for x in [16, 17, 18, 19]])
    channel.request(35, [lsbTrans(x,channel) for x in [0, 1, 2, 3]])
    channel.request(40, [lsbTrans(x,channel) for x in [64, 65, 66, 67]])
    channel.request(50, [lsbTrans(x,channel) for x in [256, 257, 257, 258]])
    channel.request(60, [lsbTrans(x,channel) for x in [512, 513, 514, 515]])
    channel.request(70, [lsbTrans(x,channel) for x in [20, 21, 22, 23]])
    channel.request(75, [lsbTrans(x,channel) for x in [72, 73, 74, 75]])
    channel.request(80, [lsbTrans(x,channel) for x in [260, 261, 262, 263]])
    channel.request(85, [lsbTrans(x,channel) for x in [520, 521, 522, 523]])
    if channel.channelID == 0:
        channel.request(90, [4])
    else:
        channel.request(90, [0])

def test8(channel):
    pageOpenInBank = [False]*8
    for i in range(64*2):
        channel.request(i,[i%64])
        if i >= 64 :
            assert sum(channel.pageArray) == 8
        else:
            assert sum(channel.pageArray) <= 8
            pageOpenInBank[pageToBank8(i%64)] = True
            assert sum(channel.pageArray) == sum(pageOpenInBank)

def lsbTrans(address,channel):
    lowerMask =  (2 ** channel.busSize) - 1
    upperBits = ( address >> channel.busSize ) << ( channel.busSize + channel.numChannels )
    lowerBits = address & lowerMask
    channelBits = channel.channelID << channel.busSize
    return upperBits + lowerBits + channelBits

def pageToBank8(address):
    lowerBits = (address >> 2) & 1
    dimm = (address >> 4) & 3
    return (dimm << 1) + lowerBits

if __name__ == "__main__" :
    main()