import subprocess

from migen import *
from migen.fhdl.verilog import convert, convert_hierarchial

# Create a parent module with two instances of a child module.
# Bind input ports to first module and output ports to second,
# and create internal signals to connect the first module to the
# second.
class ParentModule(Module):
    def __init__(self):
        self.inputs  = [Signal(x+1, name="input{}".format(x)) for x in range(4)]
        self.outputs = [Signal(x+1, name="output{}".format(x)) for x in range(4)]

        trans = [Signal(x+1) for x in range(4)]

        i = ChildModule(2)
        self.comb += [
            Cat(i.inputs[0], i.inputs[1]).eq(Cat(self.inputs[0], self.inputs[1])),
            i.inputs[2].eq(self.inputs[2]),
            i.inputs[3].eq(self.inputs[3]),
            trans[0].eq(i.outputs[0]),
            trans[1].eq(i.outputs[1]),
            trans[2].eq(i.outputs[2]),
            trans[3].eq(i.outputs[3])
        ]

        j = ChildModule(4)
        self.comb += [
            j.inputs[0].eq(trans[0]),
            j.inputs[1].eq(trans[1]),
            j.inputs[2].eq(trans[2]),
            j.inputs[3].eq(trans[3]),
            self.outputs[0].eq(j.outputs[0]),
            self.outputs[1].eq(j.outputs[1]),
            self.outputs[2].eq(j.outputs[2]),
            self.outputs[3].eq(j.outputs[3])
        ]

        self.submodules += i, j

class ChildModule(Module):
    def __init__(self, param):
        self.inputs = [Signal(x+1, name_override="input{}".format(x)) for x in range(4)]
        self.outputs = [Signal(x+1, name_override="output{}".format(x)) for x in range(4)]
        self.paramout = Signal(param)
        for x in range(4):
            self.sync += self.outputs[x].eq(self.inputs[x])
        self.comb += self.paramout.eq(Constant(2**param - 1))

def test_hierarchial():
    im = ParentModule()
    r = convert_hierarchial(im, set(im.inputs + im.outputs))
    fnames = []
    for k,v in r.items():
        fname = k + ".v"
        fnames.append(fname)
        v.write(fname)

    subprocess.check_call(["iverilog", "-W", "all", *fnames])


if __name__ == "__main__":
    test_hierarchial()
