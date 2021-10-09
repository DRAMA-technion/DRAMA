import math

class Channel:
    def __init__(self, channelID=0, numChannels=0, channelMapping=0, numDimms=0, numRanks=0, numBanks=0, busSize=3,
                 pageSize=3, channelMemorySize=10, addressRange=[[0, 2 ** 10 - 1]], addressMapping=0,
                 cacheBlockSize=6, pageOpenCycles=5, pageClosedCycles=10):
        self.channelID = channelID
        self.numChannels = numChannels
        self.channelMapping = channelMapping  # 0 - MSB, 1 - LSB
        self.numDimms = numDimms
        self.numRanks = numRanks
        self.numBanks = numBanks
        self.busSize = busSize
        self.pageSize = pageSize
        self.channelMemorySize = channelMemorySize
        self.addressRange = addressRange.copy()
        self.addressMapping = addressMapping  # 0 - Row Interleaving, 1 - Cache Block Interleaving
        self.cacheBlockSize = cacheBlockSize
        self.pageOpenCycles = pageOpenCycles
        self.pageClosedCycles = pageClosedCycles

        self.clock = 0
        self.numPages = 2**(channelMemorySize - (pageSize + busSize))
        self.pageArray = [False for page in range(self.numPages)]

        self.numPagesOpened = 0
        self.numRequests = 0
        self.numBytesReturned = 0
        self.busyCycles = 0

    """
    request :
    received args - clock , list of addresses.
    return args - channel clock after finished request, list of handled addresses.
    the addresses that are not in the channel are ignored,
    changes the state of the opened pages according to the handled request
    """
    def request(self,clock,reqAddresses):
        addresses = self.__addressesInChannel(reqAddresses)
        if len(addresses) == 0:
            return clock,[]

        reqPage = list(set([self.__addressToPageNumber(address) for address in addresses]))
        if len(reqPage) > 1:
            raise Exception("Passed more than one page")
        reqBuses = list(set([address >> self.busSize for address in addresses]))
        if len(reqBuses) > 1:
            raise Exception("Addresses are not on the same bus")
        reqPage = reqPage[0]


        self.numRequests = self.numRequests + 1
        if clock < self.clock:
            raise Exception("Channel is busy")
        self.clock = clock;

        #if reqPage >= len(self.pageArray):
            #print(addresses[0],self.channelMemorySize, reqPage, self.numPages, self.channelID, self.addressInChannel(addresses[0]))
        if self.pageArray[reqPage]: #page is open
            self.clock = self.clock + self.pageOpenCycles
            self.busyCycles = self.busyCycles + self.pageOpenCycles
        else: #page is closed
            self.numPagesOpened = self.numPagesOpened + 1
            self.clock = self.clock + self.pageClosedCycles
            self.busyCycles = self.busyCycles + self.pageClosedCycles
            self.__closePagesInSameBank(reqPage)
            self.pageArray[reqPage] = True
        ##should we return only addresses requested or entire bus???
        self.numBytesReturned = self.numBytesReturned + len(addresses)
        return self.clock, addresses


    """
    statistics :
    received args - none.
    returned args - bandwidth , average time of handling a request , number of cycles that state was idle.
    calculate all the returned values for statistics needs.
    """
    def statistics(self):
        bw = self.numBytesReturned / self.clock
        if self.numRequests == 0 :
            avgTimePerReq = 0
        else:
            avgTimePerReq = self.busyCycles / self.numRequests
        idlePerc = 1 - (self.busyCycles / self.clock)
        return bw, avgTimePerReq, idlePerc

    """
    incrementClock :
    received args - new clock of the channel.
    returned args - none.
    increment the current clock of the system according to the new channel clock.
    """
    def incrementClock(self,clock):
        if clock < self.clock:
            #print("Old Clock: ",self.clock, " New Clock: ",clock)
            raise Exception("Clock is too small")
        self.clock = clock

    """
    checkAddressInRange :
    received args - address.
    returned args - true if the received address is in the channel, false - o.w.
    """
    def __checkAddressInRange(self,address):
        #print("checkAddressInRage: ",address)
        for interval in self.addressRange:
            if interval[0] <= address <= interval[1]:
                return True
        return False

    """
    addressesInChannel :
    received args - list of addresses
    returned args - list of addresses that exist in channel.
    """
    def __addressesInChannel(self,addresses):
        return [address for address in addresses if self.__checkAddressInRange(address)]

    """
    addressToPageNumber :
    received args - address.
    returned args - page id of the address.
    """
    def __addressToPageNumber(self,address):
        page = address >> self.busSize

        if self.channelMapping == 0: #channel is MSB
            mask = self.channelID << self.channelMemorySize - self.busSize
            page = page ^ mask
        else: #channel is LSB
            page = page >> self.numChannels

        if self.addressMapping == 0: # row interleaving
            page = page >> self.pageSize
        else: # Cache Block Interleaving
            tmpPage = page >> (self.cacheBlockSize - self.busSize)
            mask = 2**self.numBanks - 1
            lowerBits = tmpPage & mask
            page = page >> (self.pageSize + self.numBanks)
            page = page << self.numBanks
            page = page + lowerBits

        return page

    """
    pageToBankInChannel :
    received args - page.
    returned args - the bank in the channel that belongs to the received page.
    """
    def __pageToBankInChannel(self,page):
        totalDimms = 2**(self.numDimms+self.numRanks)
        pagesPerDimm = self.numPages / totalDimms
        dimm = int(math.floor(page / pagesPerDimm)) << self.numBanks
        mask = 2 ** self.numBanks - 1
        lowerBits = page & mask
        return dimm + lowerBits

    """
    closePagesInSameBank :
    received args - id of the page that needs to be opened.
    returned args - none.
    closes the other pages that are in the bank of the opened page.
    """
    def __closePagesInSameBank(self,pageToOpen):
        bankUsed = self.__pageToBankInChannel(pageToOpen)
        for pageIdx in range(self.numPages):
            if(self.__pageToBankInChannel(pageIdx) == bankUsed):
                self.pageArray[pageIdx] = False

    """
    addressInChannel :
    received args - address.
    returned args - true - the received address is in the channel, false - o.w.
    """
    def addressInChannel(self,address):
        return self.__checkAddressInRange(address)