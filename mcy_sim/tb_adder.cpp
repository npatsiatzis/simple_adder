// Verilator Example
#include <stdlib.h>
#include <iostream>
#include <cstdlib>
#include <memory>
#include <set>
#include <deque>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include <verilated_cov.h>
#include "Vmutated.h"
#include<chrono>
// #include "Vmutated_adder.h"   //to get parameter values, after they've been made visible in SV


#define MAX_SIM_TIME 300
#define VERIF_START_TIME 7
vluint64_t sim_time = 0;
vluint64_t posedge_cnt = 0;

// input interface transaction item class
class InTx {
    private:
    public:
        unsigned int A;
        unsigned int B;
};


// output interface transaction item class
class OutTx {
    public:
        unsigned int C;
};

//in domain Coverage
class InCoverage{
    private:
        std::set <std::tuple <unsigned int, unsigned int> > in_cvg;
    
    public:
        void write_coverage(InTx *tx){
            std::tuple<unsigned int,unsigned int> t;
            t = std::make_tuple(tx->A,tx->B);
            in_cvg.insert(t);
        }

        bool is_covered(unsigned int A, unsigned int B){
            std::tuple<unsigned int,unsigned int> t;
            t = std::make_tuple(A,B);            
            return in_cvg.find(t) == in_cvg.end();
        }
};

//out domain Coverage
class OutCoverage {
    private:
        std::set <unsigned int> coverage;

    public:
        void write_coverage(OutTx* tx){
            coverage.insert(tx->C); 
        }

        bool is_full_coverage(){
            return coverage.size() == (1 << 9);
        }
};


// ALU scoreboard
class Scb {
    private:
        std::deque<InTx*> in_q;
        
    public:
        // Input interface monitor port
        void writeIn(InTx *tx){
            // Push the received transaction item into a queue for later
            in_q.push_back(tx);
        }

        // Output interface monitor port
        void writeOut(OutTx* tx){
            // We should never get any data from the output interface
            // before an input gets driven to the input interface
            if(in_q.empty()){
                std::cout <<"Fatal Error in AluScb: empty InTx queue" << std::endl;
                // exit(1);
            }

            // Grab the transaction item from the front of the input item queue
            InTx* in;
            in = in_q.front();
            in_q.pop_front();

            if(in->A + in->B != tx->C){
                std::cout << "Test Failure!" << std::endl;
                std::cout << "Expected : " <<  in->A << "+" << in->B << " = " << in->A+in->B << std::endl;
                std::cout << "Got : " << tx->C << std::endl;
                // exit(1);
            }

            // As the transaction items were allocated on the heap, it's important
            // to free the memory after they have been used
            delete in;    //input monitor transaction
            delete tx;    //output monitor transaction
        }
};

// interface driver
class InDrv {
    private:
        // Vmutated *dut;
        std::shared_ptr<Vmutated> dut;
    public:
        InDrv(std::shared_ptr<Vmutated> dut){
            this->dut = dut;
        }

        void drive(InTx *tx){
            // we always start with in_valid set to 0, and set it to
            // 1 later only if necessary
            dut->i_valid = 0;

            // Don't drive anything if a transaction item doesn't exist
            if(tx != NULL){
                dut->i_valid = 1;
                dut->i_A = tx->A;
                dut->i_B = tx->B;

                // Release the memory by deleting the tx item
                // after it has been consumed
                delete tx;
            }
        }
};

// input interface monitor
class InMon {
    private:
        // Vmutated *dut;
        std::shared_ptr<Vmutated> dut;
        // Scb *scb;
        std::shared_ptr<Scb>  scb;
        // InCoverage *cvg;
        std::shared_ptr<InCoverage> cvg;
    public:
        InMon(std::shared_ptr<Vmutated> dut, std::shared_ptr<Scb>  scb, std::shared_ptr<InCoverage> cvg){
            this->dut = dut;
            this->scb = scb;
            this->cvg = cvg;
        }

        void monitor(){
            if(dut->i_valid == 1){
                InTx *tx = new InTx();
                tx->A = dut->i_A;
                tx->B = dut->i_B;
                // then pass the transaction item to the scoreboard
                scb->writeIn(tx);
                cvg->write_coverage(tx);
            }
        }
};

// ALU output interface monitor
class OutMon {
    private:
        // Vmutated *dut;
        std::shared_ptr<Vmutated> dut;
        // Scb *scb;
        std::shared_ptr<Scb> scb;
        // OutCoverage *cvg;
        std::shared_ptr<OutCoverage> cvg;
    public:
        OutMon(std::shared_ptr<Vmutated> dut, std::shared_ptr<Scb> scb, std::shared_ptr<OutCoverage> cvg){
            this->dut = dut;
            this->scb = scb;
            this->cvg = cvg;
        }

        void monitor(){
            if(dut->o_valid == 1){
                OutTx *tx = new OutTx();
                tx->C = dut->o_C;

                // then pass the transaction item to the scoreboard
                scb->writeOut(tx);
                cvg->write_coverage(tx);
            }
        }
};

//sequence (transaction generator)
// coverage-driven random transaction generator
// This will allocate memory for an InTx
// transaction item, randomise the data, until it gets
// input values that have yet to be covered and
// return a pointer to the transaction item object
class Sequence{
    private:
        InTx* in;
        // InCoverage *cvg;
        std::shared_ptr<InCoverage> cvg;
    public:
        Sequence(std::shared_ptr<InCoverage> cvg){
            this->cvg = cvg;
        }

        InTx* genTx(){
            in = new InTx();
            // std::shared_ptr<InTx> in(new InTx());
            if(rand()%5 == 0){
                // Vmutated_adder::G_DATA_WIDTH = 8, here 
                in->A = rand() % (1 <<8);  
                in->B = rand() % (1 <<8);  

                while(cvg->is_covered(in->A,in->B) == false){
                    in->A = rand() % (1 <<8);  
                    in->B = rand() % (1 <<8); 
                }
                return in;
            } else {
                return NULL;
            }
        }
};


void dut_reset (std::shared_ptr<Vmutated> dut, vluint64_t &sim_time){
    dut->i_rst = 0;
    if(sim_time >= 3 && sim_time < 6){
        dut->i_rst = 1;
    }
}

// double f() {
//   using namespace std;
//   clock_t begin = clock();

//   code_to_time();

//   clock_t end = clock();
//   return elapsed_secs = double(end - begin) / CLOCKS_PER_SEC;
// }

int main(int argc, char** argv, char** env) {
    srand (time(NULL));
    Verilated::commandArgs(argc, argv);
    // Vmutated *dut = new Vmutated;
    std::shared_ptr<Vmutated> dut(new Vmutated);

    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    dut->trace(m_trace, 5);
    m_trace->open("waveform.vcd");

    InTx   *tx;

    // Here we create the driver, scoreboard, input and output monitor and coverage blocks
    std::unique_ptr<InDrv> drv(new InDrv(dut));
    std::shared_ptr<Scb> scb(new Scb());
    std::shared_ptr<InCoverage> inCoverage(new InCoverage());
    std::shared_ptr<OutCoverage> outCoverage(new OutCoverage());
    std::unique_ptr<InMon> inMon(new InMon(dut,scb,inCoverage));
    std::unique_ptr<OutMon> outMon(new OutMon(dut,scb,outCoverage));
    std::unique_ptr<Sequence> sequence(new Sequence(inCoverage));

    using namespace std;
    auto start = std::chrono::steady_clock::now();
    int elapsed_sec = 0;

    while (outCoverage->is_full_coverage() == false) {
        // random reset 
        // 0-> all 0s
        // 1 -> all 1s
        // 2 -> all random
        Verilated::randReset(2);       
        dut_reset(dut, sim_time);
        dut->i_clk ^= 1;
        dut->eval();

        // Do all the driving/monitoring on a positive edge
        if (dut->i_clk == 1){

            if (sim_time >= VERIF_START_TIME) {
                // Generate a randomised transaction item 
                // tx = rndInTx(inCoverage);
                tx = sequence->genTx();

                // Pass the generated transaction item in the driver
                //to convert it to pin wiggles
                //operation similar to than of a connection between
                //a sequencer and a driver in a UVM tb
                drv->drive(tx);

                // Monitor the input interface
                // also writes recovered transaction to
                // input coverage and scoreboard
                inMon->monitor();

                // Monitor the output interface
                // also writes recovered result (out transaction) to
                // output coverage and scoreboard 
                outMon->monitor();
            }
        }
        // end of positive edge processing

        m_trace->dump(sim_time);
        sim_time++;
    
        auto end = std::chrono::steady_clock::now();
        auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        elapsed_sec = elapsed_ms.count() / 1000;
        std::cout << "elapsed sec = " << elapsed_sec << std::endl;
        if (elapsed_sec >=4) {
                std::cout << "Test Failure!" << std::endl;
                VerilatedCov::write();
                m_trace->close();  
                exit(EXIT_SUCCESS);
        }



    }

    VerilatedCov::write();
    m_trace->close();  
    exit(EXIT_SUCCESS);
}
