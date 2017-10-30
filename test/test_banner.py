#!/usr/bin/env python3
# Copyright (c) 2017 Angel Terrones <aterrones@usb.ve>

import myhdl as hdl
from rtl.utils import createSignal
from rtl.utils import log2up
from rtl.banner import banner

# Constantes
TIMEOUT     = 70000
TICK_PERIOD = 10
RESET_TIME  = 5
CLK_XTAL    = 600
CLK_DISPLAY = 60
CLK_BANNER  = 5
ROTATIONS   = 5


@hdl.block
def banner_testbench():
    clk       = createSignal(0, 1)
    rst       = createSignal(0, 1)
    anodos    = createSignal(0, 4)
    segmentos = createSignal(0, 8)
    shift     = createSignal(0, 1)
    dut       = banner(clk_i=clk,  # noqa
                       rst_i=rst,
                       anodos_o=anodos,
                       segmentos_o=segmentos,
                       shift_o=shift,
                       CLK_XTAL=CLK_XTAL,
                       CLK_DISPLAY=CLK_DISPLAY,
                       CLK_BANNER=CLK_BANNER,
                       RST_NEG=False)
    text        = ('off', 'off', 'off', 'off', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    segment_ROM = (0x03, 0x9f, 0x25, 0x0d, 0x99, 0x49, 0x41, 0x1f,
                   0x01, 0x09, 0x11, 0xc1, 0x63, 0x85, 0x61, 0x71)
    index_text  = createSignal(0, log2up(len(text)))

    def get_segment_out(idx):
        _idx = text[idx]
        if _idx == 'off':
            return 0xff
        else:
            return segment_ROM[_idx]

    # generate clk
    @hdl.always(hdl.delay(int(TICK_PERIOD / 2)))
    def gen_clock():
        clk.next = not clk

    # shift the text to show 1 position to the right
    @hdl.always(shift.posedge)
    def shit_text_proc():
        index_text.next = (index_text + 1) % len(text)

    @hdl.instance
    def check_segment_output_proc():
        while True:
            yield anodos
            yield hdl.delay(1)  # wait for combinatorial outputs
            if anodos == 0b0001:
                assert segmentos == get_segment_out(index_text), "Error: output mismatch. Index = {0}, anodos = {1}, segment_o = {2}".format(index_text, anodos, hex(segmentos))
            elif anodos == 0b0010:
                assert segmentos == get_segment_out((index_text + 1) % len(text)), "Error: output mismatch. Index = {0}".format(index_text)
            elif anodos == 0b0100:
                assert segmentos == get_segment_out((index_text + 2) % len(text)), "Error: output mismatch. Index = {0}".format(index_text)
            elif anodos == 0b1000:
                assert segmentos == get_segment_out((index_text + 3) % len(text)), "Error: output mismatch. Index = {0}".format(index_text)
            else:
                yield hdl.Error("Invalid patter for anodos: {}".format(hdl.bin(anodos, width=4)))

    # run the test for N full rotations
    @hdl.instance
    def run_n_rotations_proc():
        for i in range(ROTATIONS):
            for j in range(len(text)):
                yield shift.posedge

        raise hdl.StopSimulation

    # timeout. I dont want to die waiting for results in case of errors
    @hdl.instance
    def timeout():
        rst.next = True
        yield hdl.delay(RESET_TIME * TICK_PERIOD)
        rst.next = False
        yield hdl.delay(TIMEOUT * TICK_PERIOD)
        raise hdl.Error("Test failed: TIMEOUT")

    return hdl.instances()


def test_banner():
    tb = banner_testbench()
    tb.config_sim(trace=True)
    tb.run_sim()
