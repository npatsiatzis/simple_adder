from cocotb.triggers import Timer,Combine,Join
from pyuvm import *
import random
import cocotb
import pyuvm
from utils import AdderBfm
from cocotb_coverage import crv
from adder_model import adder_model
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db


g_data_width = int(cocotb.top.g_data_width)
covered_values = []


#at_least = value is superfluous, just shows how you can determine the amount of times that
#a bin must be hit to considered covered
@CoverPoint("top.a",xf = lambda A,B : A, bins = list(range(2**g_data_width)), at_least=1)
@CoverPoint("top.b",xf = lambda A,B : B, bins = list(range(2**g_data_width)), at_least=1)
@CoverCross("top.cross", items = ["top.a","top.b"], at_least=1)
def io_cover(A,B):
    pass


class crv_inputs(crv.Randomized):
    def __init__(self,x,y):
        crv.Randomized.__init__(self)
        self.x = x 
        self.y = y 
        self.add_rand("x",list(range(2**g_data_width)))
        self.add_rand("y",list(range(2**g_data_width)))


# Sequence classes
class SeqItem(uvm_sequence_item):

    def __init__(self, name, a, b):
        super().__init__(name)
        self.i_crv = crv_inputs(a,b)

    def randomize_operands(self):
        self.i_crv.randomize()

    def __eq__(self, other):
        same = self.A == other.A and self.B == other.B 
        return same

    def __str__(self):
        return f"{self.get_name()} : A: 0x{self.A:02x} \
        B: 0x{self.B:02x}"


class RandomSeq(uvm_sequence):
    async def body(self):
        while(len(covered_values) != 2**(2*g_data_width)):
            data_tr = SeqItem("data_tr", None, None)
            await self.start_item(data_tr)
            data_tr.randomize_operands()
            while((data_tr.i_crv.x,data_tr.i_crv.y) in covered_values):
                data_tr.randomize_operands()
            covered_values.append((data_tr.i_crv.x,data_tr.i_crv.y))
            await self.finish_item(data_tr)

#this sequence is superfluous here. It just 
#demonstrates a strategy for directed testing
#apart from the constrained random testing
class MinMaxSeq(uvm_sequence):
    async def body(self):
        data_tr = SeqItem("data_tr",0,0)
        await self.start_item(data_tr)
        await self.finish_item(data_tr)

        data_tr = SeqItem("data_tr",2**g_data_width-1,2**g_data_width-1)
        await self.start_item(data_tr)
        await self.finish_item(data_tr)


class TestAllSeq(uvm_sequence):

    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = RandomSeq("random")
        mix_max = MinMaxSeq("min_max")
        await random.start(seqr)
        await mix_max.start(seqr)

class TestAllForkSeq(uvm_sequence):

    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = RandomSeq("random")
        mix_max = MinMaxSeq("min_max")
        random_task = cocotb.start_soon(random.start(seqr))
        min_max_task = cocotb.start_soon(mix_max.start(seqr))
        await Combine(Join(random_task), Join(min_max_task))

class Driver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    def start_of_simulation_phase(self):
        self.bfm = AdderBfm()

    async def launch_tb(self):
        await self.bfm.reset()
        self.bfm.start_bfm()

    async def run_phase(self):
        await self.launch_tb()
        while True:
            data = await self.seq_item_port.get_next_item()
            await self.bfm.send_data(data.i_crv.x, data.i_crv.y)
            result = await self.bfm.get_result()
            self.ap.write(result)
            data.result = result
            self.seq_item_port.item_done()


class Coverage(uvm_subscriber):

    def end_of_elaboration_phase(self):
        self.cvg = set()

    def write(self, data):
        (a, b) = data
        io_cover(a,b)
        if((int(a),int(b)) not in self.cvg):
            self.cvg.add((int(a),int(b)))

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(
                self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False
        if not disable_errors:
            if len(set(covered_values) - self.cvg) > 0:
                self.logger.error(
                    f"Functional coverage error. Missed: {set(covered_values)-self.cvg}")   
                assert False
            else:
                self.logger.info("Covered all input space")
                assert True


class Scoreboard(uvm_component):

    def build_phase(self):
        self.data_fifo = uvm_tlm_analysis_fifo("data_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.data_get_port = uvm_get_port("data_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.data_export = self.data_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

    def connect_phase(self):
        self.data_get_port.connect(self.data_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        passed = True
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False
        while self.result_get_port.can_get():
            _, actual_result = self.result_get_port.try_get()
            data_success, data = self.data_get_port.try_get()
            if not data_success:
                self.logger.critical(f"result {actual_result} had no command")
            else:
                (A, B) = data
                predicted_result = adder_model(A, B)
                if predicted_result == actual_result:
                    pass
                    self.logger.info("PASSED: {} + {} = {}".format(int(A),int(B),int(actual_result)))
                else:
                    self.logger.error("FAILED: {} + {} = {}, exepcted {}"\
                        .format(int(A),int(B),int(actual_result),predicted_result))

                    passed = False
        assert passed


class Monitor(uvm_component):
    def __init__(self, name, parent, method_name):
        super().__init__(name, parent)
        self.method_name = method_name

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = AdderBfm()
        # self.bfm = TinyAluBfm()
        self.get_method = getattr(self.bfm, self.method_name)

    async def run_phase(self):
        while True:
            datum = await self.get_method()
            self.logger.debug(f"MONITORED {datum}")
            self.ap.write(datum)


class Env(uvm_env):

    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = Driver.create("driver", self)
        self.data_mon = Monitor("data_mon", self, "get_data")
        self.coverage = Coverage("coverage", self)
        self.scoreboard = Scoreboard("scoreboard", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.data_mon.ap.connect(self.scoreboard.data_export)
        self.data_mon.ap.connect(self.coverage.analysis_export)
        self.driver.ap.connect(self.scoreboard.result_export)


@pyuvm.test()
class Test(uvm_test):
    """Test ALU with random values"""

    def build_phase(self):
        self.env = Env("env", self)

    def end_of_elaboration_phase(self):
        # self.test_all = TestAllSeq.create("test_all")
        self.test_all = TestAllForkSeq.create("test_random_min_max")

    async def run_phase(self):
        self.raise_objection()
        await self.test_all.start()
        await Timer(2,units = 'ns') # to do last transaction


        coverage_db.report_coverage(cocotb.log.info,bins=True)
        coverage_db.export_to_xml(filename="coverage_pyuvm.xml")
        self.drop_objection()
