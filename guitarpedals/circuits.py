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
from graphviz import Graph

logger = setup_logging()


def fuzz_circuit(dc_voltage=9 @ u_V):
    """Builds a simple fuzz pedal circuit using a transistor."""
    circuit = Circuit("Fuzz")
    # The input node will be driven by the simulation function so we don't add
    # a fixed DC source here. Having two voltage sources connected to the same
    # node causes ngspice to fail with a singular matrix error.
    circuit.V(2, "batt", circuit.gnd, dc_voltage)
    circuit.R(1, "in", "b", 33 @ u_kOhm)
    circuit.R(2, "b", "c", 100 @ u_kOhm)
    circuit.R(3, "c", circuit.gnd, 10 @ u_kOhm)
    circuit.C(1, "c", "out", 0.1 @ u_uF)
    # Provide a load so that the output node isn't left floating which can
    # otherwise lead to a singular matrix during simulation.
    circuit.R("load", "out", circuit.gnd, 100 @ u_kOhm)
    circuit.BJT(1, "c", "b", circuit.gnd, model="npn")
    circuit.model("npn", "NPN", bf=100)
    return circuit


def overdrive_circuit(dc_voltage=9 @ u_V):
    """A simple diode clipping overdrive."""
    circuit = Circuit("Overdrive")
    # See fuzz_circuit() above for why we omit a fixed DC source on the input.
    circuit.V(2, "batt", circuit.gnd, dc_voltage)
    circuit.R(1, "in", "n1", 1 @ u_kOhm)
    circuit.R(2, "n1", circuit.gnd, 1 @ u_kOhm)
    circuit.D(1, "n1", "out", model="d1")
    circuit.D(2, "out", "n1", model="d1")
    # Add a high value load to ground so the output node is defined.
    circuit.R("load", "out", circuit.gnd, 100 @ u_kOhm)
    circuit.model("d1", "D", Is=1e-15, N=1)
    return circuit


def save_circuit_diagram(circuit, filename):
    """Save a very simple diagram of ``circuit`` using Graphviz.

    This utility is not intended to produce an accurate schematic but rather
    a quick visual showing how nodes are connected. Each circuit element is
    drawn as an edge labelled with the element name. The generated file format
    is inferred from ``filename`` (e.g. ``.png`` or ``.pdf``)."""

    graph = Graph("circuit", format=filename.split(".")[-1])

    for element in circuit.elements:
        node_names = [node.name for node in element.nodes]
        if len(node_names) < 2:
            continue

        label = element.name
        # Append component value if available (resistance, capacitance, etc.)
        for attr in ("resistance", "capacitance", "inductance", "dc_value"):
            value = getattr(element, attr, None)
            if value is not None:
                label += f"\\n{value}"
                break

        # Draw edges between sequential nodes
        for start, end in zip(node_names[:-1], node_names[1:]):
            graph.edge(start, end, label=label)

    graph.render(filename, cleanup=True)
