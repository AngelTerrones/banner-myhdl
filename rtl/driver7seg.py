#!/usr/bin/env python3
# Copyright (c) 2017 Angel Terrones <aterrones@usb.ve>

import myhdl as hdl
from rtl.utils import createSignal


@hdl.block
def driver7seg(clk_i,
               rst_i,
               tick_i,
               valor_i,
               off_i,
               anodos_o,
               segmentos_o):
    """
    Driver para manejar display de 7 segmentos
    """
    assert len(valor_i) == 4, "[driver7seg] Error: longitud de valor_i debe ser 4. Valor actual: {0}".format(len(valor_i))
    assert len(anodos_o) == 4, "[driver7seg] Error: longitud de anodos_o debe ser 4. Valor actual: {0}".format(len(anodos_o))
    assert len(segmentos_o) == 8, "[driver7seg] Error: longitud de segmentos_o debe ser 8. Valor actual: {0}".format(len(segmentos_o))

    anodos      = createSignal(0, len(anodos_o))
    segment_ROM = (0x03, 0x9f, 0x25, 0x0d, 0x99, 0x49, 0x41, 0x1f,
                   0x01, 0x09, 0x11, 0xc1, 0x63, 0x85, 0x61, 0x71)

    @hdl.always(clk_i.posedge)
    def anodos_proc():
        if rst_i:
            anodos.next = hdl.modbv(1)[4:]
        elif tick_i:
            anodos.next = hdl.concat(anodos[3:0], anodos[3])

    @hdl.always_comb
    def segmentos_proc():
        if off_i:
            segmentos_o.next = hdl.modbv(0xff)[len(segmentos_o):]
        else:
            segmentos_o.next = segment_ROM[valor_i]
        anodos_o.next    = anodos

    return hdl.instances()

# Local Variables:
# flycheck-flake8-maximum-line-length: 200
# flycheck-flake8rc: ".flake8rc"
# End:
