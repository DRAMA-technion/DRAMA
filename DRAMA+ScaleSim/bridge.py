import configparser as cp
import Channel as ch


def sort_list(entry):
    return entry[0]


class Bridge:
    def __init__(self, dram_config_file, dram_ifmap_trace_file, dram_filter_trace_file, dram_ofmap_trace_file,file_prefix):
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
        self.channel_clock = []
        self.channel_clock_offset = 0
        self.stall_penalty = 0
        self.last_penalty_clock = 0
        self.channel_arbitrator = []
        for i in range(2 ** self.numChannels):
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
                addressRange=self.__channelAddressRange(i),
                addressMapping=self.addressMapping,
                cacheBlockSize=self.cacheBlockSize,
                pageOpenCycles=self.pageOpenCycles,
                pageClosedCycles=self.pageClosedCycles
            ))
            self.channel_clock.append(0)
            self.channel_arbitrator.append(0)

        self.ifmap_file = open(dram_ifmap_trace_file, 'r')
        self.filter_file = open(dram_filter_trace_file, 'r')
        self.ofmap_file = open(dram_ofmap_trace_file, 'r')
        self.dram_file = open(file_prefix + "_DRAMA_dram_requests_trace.csv", 'w')
        self.file_prefix = file_prefix

        self.ifmap_context = []
        self.filter_context = []
        self.ofmap_context = []

        self.ifmap_context_clock = [-1, -1]
        self.filter_context_clock = [-1, -1]
        self.ofmap_context_clock = [-1, -1]

    def __del__(self):
        self.ifmap_file.close()
        self.filter_file.close()
        self.ofmap_file.close()
        self.dram_file.close()


    """
    write_dram_traces :
    Performs arbitration by channel and requests. For each request, sends to channel and writes to trace. 
    """
    def write_dram_traces(self):
        self.__handleFirstCS()
        done = False

        while not done:
            channel_id = self.__arbitrateChannel()
            req, arb = self.__arbitrateRequests(channel_id)
            if len(req) == 0:
                if self.ifmap_context_clock[1] == -2 and self.filter_context_clock[1] == -2 and \
                        self.ofmap_context_clock[1] == -2:
                    done = True
                    for channel in self.channels:
                        channel.incrementClock(max(self.channel_clock))
                elif self.__allChannelsEmpty():
                    #print("All Channels Empty")
                    clocks = [self.ifmap_context_clock, self.filter_context_clock, self.ofmap_context_clock]
                    curr_clock = min([clock[0] for clock in clocks if clock[1] != -2]) + self.channel_clock_offset
                    #self.channel_clock = [curr_clock] * len(self.channel_clock)
                    for id, channel in enumerate(self.channels):
                        if curr_clock > channel.clock:
                            channel.incrementClock(curr_clock)
                            self.channel_clock[id] = curr_clock
                else:
                    self.channel_clock[channel_id] = max(self.channel_clock) + 1
            else:
                curr_clock, req = self.channels[channel_id].request(self.channel_clock[channel_id], req)
                self.__checkStallArray(curr_clock, arb)
                trace = str(self.channel_clock[channel_id] - self.channel_clock_offset)
                for address in req:
                    trace += ", " + str(address)
                trace += "\n"
                self.dram_file.write(trace)
                self.channel_clock[channel_id] = curr_clock
            self.__loadAllContexts()  # update offset

    """
    statistics :
    received args - network name and layer name
    Writes statistics per channel for the given layer to <network name>_dram_stats.csv
    """
    def statistics(self,net_name,layer_name):
        stat_file = open(net_name + '_DRAMA_dram_stats.csv', 'a')
        stat_file.write(layer_name + "\n")
        for channel in self.channels:
            bw, avgTimePerReq, idlePerc = channel.statistics()
            trace = "Channel, " + str(channel.channelID) + "\n"
            trace += "Bandwidth [Bytes/Cycles], " + str(round(bw,3)) + "\n"
            trace += "Average Cycles Per Request, " + str(round(avgTimePerReq,10)) + "\n"
            trace += "Idle Percentage, " + str(round(idlePerc * 100,3)) + "\n"
            trace += "Pages Opened, " + str(channel.numPagesOpened) + "\n"
            trace += "Busy Cycles, " + str(channel.busyCycles) + "\n"
            trace += "Number of Requests, " + str(channel.numRequests) + "\n"
            trace += "Bytes Returned, " + str(channel.numBytesReturned) + "\n"
            stat_file.write(trace)
        trace = "General \n"
        trace += "Total Cycles, " + str(max(self.channel_clock)) + "\n"
        trace += "Systolic Array Stalls [Cycles], " + str(self.stall_penalty) + "\n"
        stat_file.write(trace)

        stat_file.close()

    """
    prune :
    received args - list of inputs
    returned args - list of inputs without whitespaces
    """
    def __prune(self, input_list):
        l = []

        for e in input_list:
            e = e.strip()
            if e != '' and e != ' ':
                l.append(e)

        return l

    """
    handleFirstCS :
    Reads and handles first context of ifmap and filter, such that all requests are done before cycle 0.
    Once done, loads next contexts for ifmap, filter and ofmap.
    """
    def __handleFirstCS(self):
        cs_line = self.__prune(self.ifmap_file.readline().strip().split(','))
        self.ifmap_context_clock[1] = int(float(cs_line[1]))
        cs_line = self.__prune(self.filter_file.readline().strip().split(','))
        self.filter_context_clock[1] = int(float(cs_line[1]))
        cs_line = self.__prune(self.ofmap_file.readline().strip().split(','))
        self.ofmap_context_clock[1] = int(float(cs_line[1]))

        self.__readContext("ifmap")
        self.__readContext("filter")
        csv_write = []

        for c, channel in enumerate(self.channels):
            last_clock = self.channel_clock[c]
            for req in self.ifmap_context[c]:
                if len(req) > 0:
                    self.channel_clock[c], req = channel.request(self.channel_clock[c], req)
                    req.insert(0, last_clock)
                    last_clock = self.channel_clock[c]
                    csv_write.append(req)
            for req in self.filter_context[c]:
                if len(req) > 0:
                    self.channel_clock[c], req = channel.request(self.channel_clock[c], req)
                    req.insert(0, last_clock)
                    last_clock = self.channel_clock[c]
                    csv_write.append(req)
        csv_write.sort(key=sort_list)
        max_clock = max(self.channel_clock) + 1
        self.channel_clock = [max(self.channel_clock) for c in self.channel_clock]  # sync clocks
        self.channel_clock_offset = max(self.channel_clock)
        for channel in self.channels:
            channel.incrementClock(max(self.channel_clock))
        for line in csv_write:
            trace = str(line[0] - max_clock)
            for address in line[1:]:
                trace += ", " + str(address)
            trace += "\n"
            self.dram_file.write(trace)

        self.__readContext("ifmap")
        self.__readContext("filter")
        self.__readContext("ofmap")

    """
    readContext :
    received args - type (ifmap, filter, ofmap)
    Loads context from relevant trace file and sorts context into requests using __sortContext.
    If last context, loads -2 to <type>_context_clock.
    """
    def __readContext(self, type):
        if type == "ifmap":
            file = self.ifmap_file
            context = self.ifmap_context
            context_clock = self.ifmap_context_clock
        elif type == "filter":
            file = self.filter_file
            context = self.filter_context
            context_clock = self.filter_context_clock
        else:
            file = self.ofmap_file
            context = self.ofmap_context
            context_clock = self.ofmap_context_clock

        context.clear()
        line = self.__prune(file.readline().strip().split(','))
        while len(line) > 0 and line[0] != "CS":
            for address in line[1:]:
                context.append(int(float(address)))

            line = self.__prune(file.readline().strip().split(','))

        self.__sortContext(context, type)

        context_clock[0] = context_clock[1]
        if len(line) > 0:
            context_clock[1] = int(float(line[1]))
        else:
            context_clock[1] = -2

    """
    sortContext :
    received args - context (list of addresses), type (ifmap, filter, ofmap)
    Sorts context into requests grouped by channel and by bus mapping.
    Requests per channel are ordered in a numerically increasing order.
    Loads sorted context by channel and requests to <type>_context.
    """
    def __sortContext(self, context, type):
        context.sort()
        new_context = []
        for channel in self.channels:
            channel_context = [address for address in sorted(set(context)) if channel.addressInChannel(address)] #filter duplicate addresses (read/write most up to date)
            new_channel_context = []
            first_in_bus = True
            bus_id = None
            bus_context = []
            for address in channel_context:
                add_bus_id = address >> channel.busSize
                if add_bus_id != bus_id:
                    first_in_bus = True
                if first_in_bus:
                    if bus_id is not None:
                        new_channel_context.append(bus_context)
                    bus_context = []
                    first_in_bus = False
                    bus_id = add_bus_id
                bus_context.append(address)
            new_channel_context.append(bus_context)
            new_context.append(new_channel_context)
        if type == "ifmap":
            self.ifmap_context = new_context
        elif type == "filter":
            self.filter_context = new_context
        else:
            self.ofmap_context = new_context

    """
    arbitrateChannel :
    received args - none.
    returned args - the channel with the earliest channel clock.
    """
    def __arbitrateChannel(self):
        return self.channel_clock.index(min(self.channel_clock))

    """
    arbitrateRequests :
    received args - channel id
    returned args - request and type (ifmap/ofmap/filter).
    the arbitrator is using round robin between types.
    """
    def __arbitrateRequests(self, channel_id):
        arb = self.channel_arbitrator[channel_id]

        arb = (arb + 1) % 3
        if not self.__checkAvailableRequests(channel_id, arb):
            arb = (arb + 1) % 3
            if not self.__checkAvailableRequests(channel_id, arb):
                arb = (arb + 1) % 3
                if not self.__checkAvailableRequests(channel_id, arb):
                    return [], arb

        self.channel_arbitrator[channel_id] = arb

        if arb == 0:
            req = self.ifmap_context[channel_id].pop(0)
        elif arb == 1:
            req = self.filter_context[channel_id].pop(0)
        else:
            req = self.ofmap_context[channel_id].pop(0)

        return req, arb

    """
    checkAvailableRequests :
    received args - channel id and type (ifmap/ofmap/filter).
    returned args - true - if any request is ready, false - o.w
    """
    def __checkAvailableRequests(self, channel_id, arb):
        if arb == 0 and self.channel_clock[channel_id] >= self.ifmap_context_clock[
            0] + self.channel_clock_offset - self.stall_penalty and len(self.ifmap_context[channel_id]) > 0 and len(
                self.ifmap_context[channel_id][0]) > 0:
            return True
        if arb == 1 and self.channel_clock[channel_id] >= self.filter_context_clock[
            0] + self.channel_clock_offset - self.stall_penalty and len(self.filter_context[channel_id]) > 0 and len(
                self.filter_context[channel_id][0]) > 0:
            return True
        if arb == 2 and self.channel_clock[channel_id] >= self.ofmap_context_clock[
            0] + self.channel_clock_offset - self.stall_penalty and len(self.ofmap_context[channel_id]) > 0 and len(
                self.ofmap_context[channel_id][0]) > 0:
            return True
        return False

    """
    loadAllContexts :
    received args - none.
    returned args - none.
    for each type check if the context in empty, and if so read a new context.
    """
    def __loadAllContexts(self):
        if self.ifmap_context_clock[1] != -2:
            if self.__checkContextIsEmpty(self.ifmap_context):
                self.__readContext("ifmap")
                #print("Loading Ifmap Context", self.ifmap_context_clock)
        if self.filter_context_clock[1] != -2:
            if self.__checkContextIsEmpty(self.filter_context):
                self.__readContext("filter")
                #print("Loading Filter Context")
        if self.ofmap_context_clock[1] != -2:
            if self.__checkContextIsEmpty(self.ofmap_context):
                self.__readContext("ofmap")
                #print("Loading Ofmap Context", self.ofmap_context_clock)

    """
    checkContextIsEmpty :
    received args - context
    returned args - true - if the context is empty. false - o.w
    """
    def __checkContextIsEmpty(self, context):
        for channel_id, channel_context in enumerate(context):
            if len(channel_context) > 0 and len(channel_context[0]) > 0:
                return False
        return True

    """
    allChannelsEmpty :
    received args - none.
    returned args - true - if all channels are empty. false - o.w
    """
    def __allChannelsEmpty(self):
        for channel_id in range(2 ** self.numChannels):
            for arb in range(3):
                if self.__checkAvailableRequests(channel_id, arb):
                    return False
        return True

    """
    checkStallArray :
    received args - current time and type.
    returned args - none.
    if the current time is beyond the context limit, adding stall.
    """
    def __checkStallArray(self, curr_clock, arb):
        if arb == 0:
            context_clock = self.ifmap_context_clock
        elif arb == 1:
            context_clock = self.filter_context_clock
        else:
            context_clock = self.ofmap_context_clock

        if context_clock[1] != -2 and curr_clock > context_clock[1] + self.channel_clock_offset:
            self.stall_penalty += min(curr_clock - self.last_penalty_clock, curr_clock - self.channel_clock_offset - context_clock[1])
            #self.stall_penalty += max(0, curr_clock - self.channel_clock_offset - max(context_clock[1], self.channel_clock[channel_id] - self.channel_clock_offset))
            #print("Stall Penalty")
            #print(self.stall_penalty,arb,curr_clock, self.channel_clock_offset, context_clock[1], self.last_penalty_clock)
            self.last_penalty_clock = curr_clock

    """
    channelAddressRange :
    received args - channel id.
    returned args - array of address ranges for the channel id.
    based on channel mapping (MSB/LSB).
    """
    def __channelAddressRange(self,channel_id):
        if self.channelMapping == 0: #MSB
            return [[channel_id * (2 ** self.channelMemorySize), (channel_id + 1) * (2 ** self.channelMemorySize) - 1]]
        else: #LSB
            channelAdd = channel_id << self.busSize
            busAdd = (2 ** self.busSize) - 1
            return [[(x<<(self.busSize + self.numChannels)) + channelAdd, (x<<(self.busSize + self.numChannels)) + channelAdd + busAdd]
                    for x in range(2**(self.channelMemorySize - self.numChannels))]