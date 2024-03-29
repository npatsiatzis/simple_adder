
from cocotb.triggers import RisingEdge,ClockCycles,Timer
from cocotb.queue import QueueEmpty, Queue
from cocotb.result import TestFailure
import cocotb
import enum
import random
from cocotb_coverage import crv 
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db,CoverCheck
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

    async def send_data(self, valid, a, b):
        command_tuple = (valid, a, b)
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
                (valid,a, b) = self.driver_queue.get_nowait()
                self.dut.i_A.value = a
                self.dut.i_B.value = b
                self.dut.i_valid.value = valid
            except QueueEmpty:
                pass

    async def data_mon_bfm(self):
        # await RisingEdge(self.dut.i_valid)
        while True:
            if(self.dut.i_valid == 1):
                data_tuple = (self.dut.i_A.value,self.dut.i_B.value)
                self.data_mon_queue.put_nowait(data_tuple)
            await RisingEdge(self.dut.i_clk)

    async def result_mon_bfm(self):
        # await RisingEdge(self.dut.o_valid)
        while True:
            if(int(self.dut.o_valid.value) == 1):
                self.result_mon_queue.put_nowait(self.dut.o_C.value)
            await RisingEdge(self.dut.i_clk)


    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.data_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())


class AssertionsCheck(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.assertion1 = Assertion_i_valid_impl_o_valid()
        self.assertion2 = Assertion_not_i_valid_impl_stable_o_C()
  
    def start_assertions(self):
        cocotb.start_soon(self.assertion1.assertion_mon_valid_ant())
        cocotb.start_soon(self.assertion2.assertion_mon_not_valid_ant())


class Assertion_i_valid_impl_o_valid(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        # for i_valid |=> o_valid
        self.cycles_to_count_till_consequent_valid = 1
        self.cnt_cycles_since_antecedent_valid = 0

    # assert property (@(posedge i_clk)i_valid |=> o_valid);
    @CoverCheck(
        "assertion.i_valid|=>o_valid",
        f_fail = lambda x : x.o_valid.value == 0,
        f_pass = lambda x : True
    )
    def test_i_valid_impl_o_valid(self,dut):
        pass

    def assert_callback():
        raise TestFailure("Assertion failed!")

    async def assertion_mon_valid_ant(self):
        while True:
            if(self.cnt_cycles_since_antecedent_valid == self.cycles_to_count_till_consequent_valid):
                self.cnt_cycles_since_antecedent_valid = 0
                self.test_i_valid_impl_o_valid(self.dut)
                coverage_db["assertion.i_valid|=>o_valid"].add_bins_callback(self.assert_callback, "FAIL")
            if(self.dut.i_valid.value == 1):
                self.cnt_cycles_since_antecedent_valid += 1

            await RisingEdge(self.dut.i_clk)

class Assertion_not_i_valid_impl_stable_o_C(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top

        #for !ivalid |=> stable(o_C)
        self.cycles_to_count_till_consequent_stable_o_C = 1
        self.cnt_cycles_since_antecedent_not_valid = 0
        self.o_C_prev = 0

    # assert property (@(posedge i_clk) !i_valid |=> $stable(o_C));
    @CoverCheck(
        "assertion.!valid|=>$stable(o_C)",
        f_fail = lambda x,y : (x.o_C.value - y != 0),
        f_pass = lambda x,y : True
    )
    def test_not_i_valid_impl_stable_o_C(self,dut,o_C_prev):
        pass

    def assert_callback(self):
        raise TestFailure("Assertion failed!")

    async def assertion_mon_not_valid_ant(self):
        while True:
            if(self.cnt_cycles_since_antecedent_not_valid == self.cycles_to_count_till_consequent_stable_o_C):
                self.cnt_cycles_since_antecedent_not_valid = 0
                self.test_not_i_valid_impl_stable_o_C(self.dut,self.o_C_prev)
                coverage_db["assertion.!valid|=>$stable(o_C)"].add_bins_callback(self.assert_callback, "FAIL")
            if(self.dut.i_valid.value == 0):
                self.cnt_cycles_since_antecedent_not_valid += 1
                self.o_C_prev =  self.dut.o_C.value

            await RisingEdge(self.dut.i_clk)
