
from cocotb.triggers import RisingEdge,ClockCycles
from cocotb.queue import QueueEmpty, Queue
import cocotb
import enum
import random
from cocotb_coverage import crv 
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
from pyuvm import utility_classes



class AdderBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.driver_queue = Queue(maxsize=1)
        self.data_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def send_data(self, a, b):
        command_tuple = (a, b)
        await self.driver_queue.put(command_tuple)

    async def get_data(self):
        data = await self.data_mon_queue.get()
        return data

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await Timer(2,units = 'ns')
        self.dut.i_A.value = 0
        self.dut.i_B.value = 0
        await Timer(2,units = 'ns')


    async def driver_bfm(self):
        self.dut.i_A.value = 0
        self.dut.i_B.value = 0
        while True:
            await Timer(2,units = 'ns')
            try:
                (a, b) = self.driver_queue.get_nowait()
                self.dut.i_A.value = a
                self.dut.i_B.value = b
            except QueueEmpty:
                pass

    async def data_mon_bfm(self):
        while True:
            await Timer(2,units = 'ns')
            data_tuple = (self.dut.i_A.value,self.dut.i_B.value)
            self.data_mon_queue.put_nowait(data_tuple)

    async def result_mon_bfm(self):
        while True:
            await Timer(2,units = 'ns')
            self.result_mon_queue.put_nowait(self.dut.o_C.value)


    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.data_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())


class AdderBfmSV(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.driver_queue = Queue(maxsize=1)
        self.data_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def send_data(self, a, b):
        command_tuple = (a, b)
        await self.driver_queue.put(command_tuple)

    async def get_data(self):
        data = await self.data_mon_queue.get()
        return data

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await RisingEdge(self.dut.i_clk)
        self.dut.i_rst.value = 1
        self.dut.i_A.value = 0
        self.dut.i_B.value = 0
        self.dut.i_valid.value = 0
        await ClockCycles(self.dut.i_clk,5)
        self.dut.i_rst.value = 0
        await RisingEdge(self.dut.i_clk)


    async def driver_bfm(self):
        self.dut.i_A.value = 0
        self.dut.i_B.value = 0
        while True:

            await RisingEdge(self.dut.i_clk)
            try:
                (a, b) = self.driver_queue.get_nowait()
                self.dut.i_A.value = a
                self.dut.i_B.value = b
                self.dut.i_valid.value = 1
            except QueueEmpty:
                pass

    async def data_mon_bfm(self):
        await RisingEdge(self.dut.i_valid)
        while True:
            data_tuple = (self.dut.i_A.value,self.dut.i_B.value)
            self.data_mon_queue.put_nowait(data_tuple)
            await RisingEdge(self.dut.i_clk)

    async def result_mon_bfm(self):
        await RisingEdge(self.dut.o_valid)
        while True:
            self.result_mon_queue.put_nowait(self.dut.o_C.value)
            await RisingEdge(self.dut.i_clk)


    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.data_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())