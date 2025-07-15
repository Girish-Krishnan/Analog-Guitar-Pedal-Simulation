import numpy as np
from PySpice.Logging.Logging import setup_logging
# Import the Circuit class directly.  Using the module alias and then
# accessing ``Circuit`` via ``Netlist.Circuit`` caused an AttributeError
# when running ``python -m guitarpedals.simulate``.  The PySpice package
# exposes ``Circuit`` as a class within ``PySpice.Spice.Netlist`` so we
# import it explicitly here.
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Probe.Plot import plot

logger = setup_logging()


def fuzz_circuit(dc_voltage=9@u_V):
    """Builds a simple fuzz pedal circuit using a transistor."""
    circuit = Circuit('Fuzz')
    circuit.V(1, 'in', circuit.gnd, 0@u_V)
    circuit.V(2, 'batt', circuit.gnd, dc_voltage)
    circuit.R(1, 'in', 'b', 33@u_kOhm)
    circuit.R(2, 'b', 'c', 100@u_kOhm)
    circuit.R(3, 'c', circuit.gnd, 10@u_kOhm)
    circuit.C(1, 'c', 'out', 0.1@u_uF)
    circuit.BJT(1, 'c', 'b', circuit.gnd, model='npn')
    circuit.model('npn', 'NPN', bf=100)
    return circuit


def overdrive_circuit(dc_voltage=9@u_V):
    """A simple diode clipping overdrive."""
    circuit = Circuit('Overdrive')
    circuit.V(1, 'in', circuit.gnd, 0@u_V)
    circuit.V(2, 'batt', circuit.gnd, dc_voltage)
    circuit.R(1, 'in', 'n1', 1@u_kOhm)
    circuit.R(2, 'n1', circuit.gnd, 1@u_kOhm)
    circuit.D(1, 'n1', 'out', model='d1')
    circuit.D(2, 'out', 'n1', model='d1')
    circuit.model('d1', 'D', Is=1e-15, N=1)
    return circuit

