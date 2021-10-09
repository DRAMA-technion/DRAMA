import configparser as cp
import Channel as ch


class Bridge:
    def __init__(self, dram_config_file, dram_ifmap_trace_file, dram_filter_trace_file, dram_ofmap_trace_file):
        dram_sec = 'dram_presets'

        config = cp.ConfigParser()
        config.read(dram_config_file)

        self.numChannels = int(config.get(dram_sec, 'NumberOfChannels').strip())
        self.channelMapping = config.get(dram_sec, 'ChannelMapping').strip()
        if self.channelMapping == "MSB":
            self.channelMapping = 0
        else:
            self.channelMapping = 1
        self.numDimms = int(config.get(dram_sec, 'NumberOfDimms').strip())
        self.numRanks = int(config.get(dram_sec, 'NumberOfRanks').strip())
        self.numBanks = int(config.get(dram_sec, 'NumberOfBanks').strip())
        self.busSize = int(config.get(dram_sec, 'BusSize').strip())
        self.pageSize = int(config.get(dram_sec, 'PageSize').strip())
        self.channelMemorySize = int(config.get(dram_sec, 'ChannelMemorySize').strip())
        self.addressMapping = config.get(dram_sec, 'AddressMapping').strip()
        if self.addressMapping == "RI":
            self.addressMapping = 0
        else:
            self.addressMapping = 1
        self.cacheBlockSize = int(config.get(dram_sec, 'CacheBlockSize').strip())
        self.pageOpenCycles = int(config.get(dram_sec, 'PageOpenCycles').strip())
        self.pageClosedCycles = int(config.get(dram_sec, 'PageClosedCycles').strip())

        self.channels = []
        for i in range(self.numChannels):
            self.channels.append(ch.Channel(
                channelID=i,
                numChannels=self.numChannels,
                channelMapping=self.channelMapping,
                numDimms=self.numDimms,
                numRanks=self.numRanks,
                numBanks=self.numBanks,
                busSize=self.busSize,
                pageSize=self.pageSize,
                channelMemorySize=self.channelMemorySize,
                addressRange=[[i*(2**self.channelMemorySize), (i+1)*(2**self.channelMemorySize) - 1]],
                addressMapping=self.addressMapping,
                cacheBlockSize=self.cacheBlockSize,
                pageOpenCycles=self.pageOpenCycles,
                pageClosedCycles=self.pageClosedCycles
            ))

        self.ifmap_file=dram_ifmap_trace_file
        self.filter_file=dram_filter_trace_file
        self.ofmap_file=dram_ofmap_trace_file

        self.ifmap_start = self.filter_start = -1
        self.ifmap_finish = self.filter_finish = self.ofmap_finish = 0

    def __prune(input_list):
        l = []

        for e in input_list:
            e = e.strip()
            if e != '' and e != ' ':
                l.append(e)

        return l

    def __find_first_request(self,ifmap_req,filter_req,ofmap_req):
        if len(ifmap_req) == 0:
            if len(filter_req) == 0:
                return 2 # ofmap
            elif len(ofmap_req) == 0:
                return 1 # filter
            else:
                filter_clock = int(filter_req[0])
                ofmap_clock = int(ofmap_req[0])

                if filter_clock <= ofmap_clock:
                    return 1 # filter
                else:
                    return 2 # ofmap

        elif len(filter_req) == 0:
            if len(ofmap_req) == 0:
                return 0 # ifmap
            else:
                ifmap_clock = int(ifmap_req[0])
                ofmap_clock = int(ofmap_req[0])

                if ifmap_clock <= ofmap_clock:
                    return 0 # ifmap
                else:
                    return 2 # ofmap

        elif len(ofmap_req):
            ifmap_clock = int(ifmap_req[0])
            filter_clock = int(filter_req[0])

            if ifmap_clock <= filter_clock:
                return 0 # ifmap
            else:
                retrun 1 # filter

        else:
            ifmap_clock = int(ifmap_req[0])
            filter_clock = int(filter_req[0])
            ofmap_clock = int(ofmap_req[0])

            if ifmap_clock <= filter_clock and ifmap_clock <= ofmap_clock:
                return 0 # ifmap
            elif filter_clock <= ofmap_clock:
                return 1 # filter
            else
                return 2 # ofmap

    def __checkBufferSwitch(self,ifmap_req,filter_req,ofmap_req):
        ifmap_req_new = ifmap_req
        filter_req_new = filter_req
        ofmap_req_new = ofmap_req
        if ifmap_req[0] == "CS":
            self.ifmap_start = int(ifmap_req[1])
            self.ifmap_finish = int(ifmap_req[2])
            ifmap_req_new = __prune(ifmap.readline().strip().split(','))

        if filter_req[0] == "CS":
            self.filter_req = int(filter_req[1])
            self.filter_req = int(filter_req[2])
            filter_req_new = __prune(filter.readline().strip().split(','))

        if ofmap_req[0] == "CS":
            self.ofmap_finish = inter(ofmap_req[1])
            ofmap_req_new = __prune(ofmap.readline().strip().split(','))

        return ifmap_req_new,filter_req_new,ofmap_req_new

    def write_dram_traces(self):
        ifmap=open(self.ifmap_file, 'r')
        filter=open(self.filter_file, 'r')
        ofmap=open(self.ofmap_file, 'r')

        ifmap_req = __prune(ifmap.readline().strip().split(','))
        filter_req = __prune(filter.readline().strip().split(','))
        ofmap_req = __prune(ofmap.readline().strip().split(','))

        while len(ifmap_req) + len(filter_req) + len(ofmap_req) > 0:
            first_req = self.__find_first_request(ifmap_req,filter_req,ofmap_req)

            if first_req == 0:

            elif first_req == 1:

            else:

            ifmap_req,filter_req,ofmap_req = self.__checkBufferSwitch(ifmap_req,filter_req,ofmap_req)

        ifmap.close()
        filter.close()
        ofmap.close()

