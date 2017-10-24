#!/usr/bin/env python3
# Copyright (c) 2017 Angel Terrones <aterrones@usb.ve>

import myhdl as hdl
from rtl.utils import createSignal
from rtl.utils import log2up


@hdl.block
def clk_div(clk_xtal_i,
            rst_i,
            clk_display_o,
            clk_banner_o,
            CLK_XTAL=50000000,
            CLK_DISPLAY=60,
            CLK_BANNER=1):
    assert ((CLK_DISPLAY / CLK_BANNER) % 4 == 0), "[clk_div] Error: (CLK_DISPLAY / CLK_BANNER) debe ser múltiplo de 4 para evitar display glitches"
    MAX_CNT_DISPLAY = int(CLK_XTAL / CLK_DISPLAY)
    MAX_CNT_BANNER  = int(CLK_XTAL / CLK_BANNER)

    cnt_display = createSignal(0, log2up(MAX_CNT_DISPLAY))
    cnt_banner  = createSignal(0, log2up(MAX_CNT_BANNER))

    @hdl.always(clk_xtal_i.posedge)
    def clk_display_proc():
        if rst_i:
            cnt_display.next = 0
            clk_display_o.next = 0
        elif cnt_display == MAX_CNT_DISPLAY - 1:
            cnt_display.next = 0
            clk_display_o.next = 1
        else:
            cnt_display.next = cnt_display + 1
            clk_display_o.next = 0

    @hdl.always(clk_xtal_i.posedge)
    def clk_banner_proc():
        if rst_i:
            cnt_banner.next = 0
            clk_banner_o.next = 0
        elif cnt_banner == MAX_CNT_BANNER - 1:
            cnt_banner.next = 0
            clk_banner_o.next = 1
        else:
            cnt_banner.next = cnt_banner + 1
            clk_banner_o.next = 0

    return hdl.instances()

# Local Variables:
# flycheck-flake8-maximum-line-length: 200
# flycheck-flake8rc: ".flake8rc"
# End:
