// Verilator Example
// Norbertas Kremeris 2021
#include <stdlib.h>
#include <iostream>
#include <cstdlib>
#include <memory>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vadder.h"
#include "Vadder_adder.h"   //to get parameter values, after they've been made visible in SV


#define MAX_SIM_TIME 300
#define VERIF_START_TIME 7
vluint64_t sim_time = 0;
vluint64_t posedge_cnt = 0;

// input interface transaction item class
class InTx {
    private:
    public:
        uint8_t A;
        uint8_t B;
};


// output interface transaction item class
class OutTx {
    public:
        uint16_t C;
};

//in domain Coverage
class InCoverage{
    private:
        std::set <std::tuple <uint8_t, uint8_t> > in_cvg;
    
    public:
        void write_coverage(InTx *tx){
            std::tuple<uint8_t,uint8_t> t;
            t = std::make_tuple(tx->A,tx->B);
            in_cvg.insert(t);
        }

        bool is_covered(uint8_t A, uint8_t B){
            std::tuple<uint8_t,uint8_t> t;
            t = std::make_tuple(A,B);            
            return in_cvg.find(t) == in_cvg.end();
        }
};

//out domain Coverage
class OutCoverage {
    private:
        std::set <uint16_t> coverage;

    public:
        void write_coverage(OutTx* tx){
            coverage.insert(tx->C);
        }

        bool is_full_coverage(){
            return coverage.size() == (2 << (Vadder_adder::g_data_width+1));
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
                exit(1);
            }

            // Grab the transaction item from the front of the input item queue
            InTx* in;
            in = in_q.front();
            in_q.pop_front();

            if(in->A + in->B != tx->C){
                std::cout << "Test Failure!" << std::endl;
                std::cout << "Expected : " <<  in->A << "+" << in->B << " = " << in->A+in->B << std::endl;
                std::cout << "Got : " << tx->C << std::endl;
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
        Vadder *dut;
    public:
        InDrv(Vadder *dut){
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
        Vadder *dut;
        Scb *scb;
        InCoverage *cvg;
    public:
        InMon(Vadder *dut, Scb *scb, InCoverage *cvg){
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
        Vadder *dut;
        Scb *scb;
        OutCoverage *cvg;
    public:
        OutMon(Vadder *dut, Scb *scb, OutCoverage *cvg){
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

// coverage-driven random transaction generator
// This will allocate memory for an InTx
// transaction item, randomise the data, until it gets
// input values that have yet to be covered and
// return a pointer to the transaction item object
// InTx* rndInTx(InCoverage *cvg){
//     InTx *tx = new InTx();
//     // InCoverage *cvg = new InCoverage();

//     if(rand()%2 == 0){
//         tx->A = rand() % (2 << Vadder_adder::g_data_width);  
//         tx->B = rand() % (2 << Vadder_adder::g_data_width);  

//         while(cvg->is_covered(tx->A,tx->B) == false){
//             tx->A = rand() % (2 << Vadder_adder::g_data_width);  
//             tx->B = rand() % (2 << Vadder_adder::g_data_width); 
//         }
//         return tx;
//     } else {
//         return NULL;
//     }
// }


//sequence (transaction generator)
// coverage-driven random transaction generator
// This will allocate memory for an InTx
// transaction item, randomise the data, until it gets
// input values that have yet to be covered and
// return a pointer to the transaction item object
class Sequence{
    private:
        InTx* in;
        InCoverage *cvg;
    public:
        Sequence(InCoverage *cvg){
            this->cvg = cvg;
        }

        InTx* genTx(){
            in = new InTx();
            if(rand()%5 == 0){
                if(rand()%2 == 0){
                    in->A = rand() % (2 << Vadder_adder::g_data_width);  
                    in->B = rand() % (2 << Vadder_adder::g_data_width);  

                    while(cvg->is_covered(in->A,in->B) == false){
                        in->A = rand() % (2 << Vadder_adder::g_data_width);  
                        in->B = rand() % (2 << Vadder_adder::g_data_width); 
                    }
                }
                return in;
            } else {
                return NULL;
            }
        }
};


void dut_reset (Vadder *dut, vluint64_t &sim_time){
    dut->i_rst = 0;
    if(sim_time >= 3 && sim_time < 6){
        dut->i_rst = 1;
    }
}

int main(int argc, char** argv, char** env) {
    srand (time(NULL));
    Verilated::commandArgs(argc, argv);
    Vadder *dut = new Vadder;

    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    dut->trace(m_trace, 5);
    m_trace->open("waveform.vcd");

    InTx   *tx;

    // Here we create the driver, scoreboard, input and output monitor and coverage blocks
    InDrv  *drv    = new InDrv(dut);
    Scb    *scb    = new Scb();
    InCoverage *inCoverage = new InCoverage();
    OutCoverage *outCoverage = new OutCoverage(); 
    InMon  *inMon  = new InMon(dut, scb, inCoverage);
    OutMon *outMon = new OutMon(dut, scb, outCoverage);
    Sequence *sequence = new Sequence(inCoverage);

    while (outCoverage->is_full_coverage() == false) {
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
    }

    m_trace->close();
    delete dut;
    delete outMon;
    delete inMon;
    delete scb;
    delete drv;
    delete inCoverage;
    delete outCoverage;
    delete sequence;    
    exit(EXIT_SUCCESS);
}
