#!/usr/bin/env python3
# Copyright (c) 2017 Angel Terrones <aterrones@usb.ve>

import myhdl as hdl
from rtl.utils import createSignal
from rtl.driver7seg import driver7seg
from rtl.clk_div import clk_div


@hdl.block
def banner(clk_i,
           rst_i,
           anodos_o,
           segmentos_o,
           shift_o,
           CLK_XTAL=50000000,
           CLK_DISPLAY=240,
           CLK_BANNER=1,
           RST_NEG=False):
    """
    Banner para mostrar números 0-9, izquierda a derecha
    """
    TXT           = "fedcba9876543210dead"
    NMBR          = int(TXT, base=16)
    NCHAR         = len(TXT)
    NBITS         = 4 * len(TXT)
    clk_display   = createSignal(0, 1)
    clk_banner    = createSignal(0, 1)
    number2show   = createSignal(0, 4)
    table2show    = createSignal(0, NBITS)
    table2off     = createSignal(0, NCHAR)
    index_sel     = createSignal(0, 2)
    anodos        = createSignal(0, len(anodos_o))
    rst_aux_o     = createSignal(0, 1)
    off_driver    = createSignal(0, 1)
    clk_div_d     = clk_div(clk_i, rst_aux_o, clk_display, clk_banner,  # noqa
                            CLK_XTAL=CLK_XTAL, CLK_DISPLAY=CLK_DISPLAY, CLK_BANNER=CLK_BANNER)
    driver        = driver7seg(clk_i, rst_aux_o, clk_display, number2show, off_driver, anodos, segmentos_o)  # noqa

    @hdl.always_comb
    def rst_proc():
        if RST_NEG:
            rst_aux_o.next = not rst_i
        else:
            rst_aux_o.next = rst_i

    @hdl.always(clk_i.posedge)
    def shift_banner_proc():
        if rst_aux_o:
            table2show.next = hdl.modbv(NMBR)[NBITS:]
            table2off.next  = hdl.modbv(0xF)[NCHAR:]
        elif clk_banner:
            table2show.next = hdl.concat(table2show[4:0], table2show[NBITS:4])
            table2off.next  = hdl.concat(table2off[0], table2off[NCHAR:1])

    @hdl.always_comb
    def index_proc():
        if anodos == 0b0001:
            index_sel.next = 0
        elif anodos == 0b0010:
            index_sel.next = 1
        elif anodos == 0b0100:
            index_sel.next = 2
        elif anodos == 0b1000:
            index_sel.next = 3
        else:
            index_sel.next = 0

    @hdl.always_comb
    def select_digit_proc():
        """verilator lint_off WIDTH"""
        number2show.next = (table2show >> (index_sel * 4)) & hdl.modbv(0xf)[4:]
        off_driver.next  = table2off[index_sel]
        """verilator lint_on WIDTH"""
        anodos_o.next    = anodos
        shift_o.next     = clk_banner

    return hdl.instances()

# Local Variables:
# flycheck-flake8-maximum-line-length: 200
# flycheck-flake8rc: ".flake8rc"
# End:
