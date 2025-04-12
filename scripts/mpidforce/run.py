import os
import mpidplugin
from mpidplugin import MPIDForce
from openmm import *
from openmm.app import *
from openmm.unit import *
import numpy as np
from openff.toolkit import ForceField as OForceField
from openff.toolkit import Topology as OTopology
from openff.toolkit import Molecule as OMolecule

temperature = 298 * kelvin

modeller = Modeller(Topology(), [])
modeller.addSolvent(
    ForceField("tip3p.xml"),
    numAdded=256,
)
with open("input.pdb", "w") as f:
    PDBFile.writeFile(modeller.getTopology(), modeller.getPositions(), f)

off_top = OTopology.from_pdb("input.pdb")
off_forcefield = OForceField("forcefield.offxml", load_plugins=True)
interchange = off_forcefield.create_interchange(topology=off_top)

system = interchange.to_openmm_system(combine_nonbonded_forces=True)

with open("system.xml", "w") as f:
    f.write(XmlSerializer.serialize(system))

system.addForce(MonteCarloBarostat(1 * bar, temperature, 25))
system.addForce(CMMotionRemover())

topology = interchange.to_openmm_topology()
position = interchange.get_positions()

timestep = 2 * femtosecond
# integrator = LangevinIntegrator(temperature, 1.0 / picosecond, timestep)
integrator = LangevinMiddleIntegrator(temperature, 1.0 / picosecond, timestep)
simulation = Simulation(topology, system, integrator)
simulation.context.setPositions(position.to("nanometer").magnitude * nanometer)
simulation.minimizeEnergy()

nsteps = 25000000
n_save = 2000
n_save_steps = int(nsteps / n_save)

simulation.reporters.append(
    StateDataReporter(
        file="simulation.csv",
        reportInterval=50000,
        step=True,
        potentialEnergy=True,
        temperature=True,
        volume=True,
        density=True,
        speed=True,
    )
)
simulation.reporters.append(PDBReporter("output.pdb", nsteps))
simulation.reporters.append(
    DCDReporter("trajectory.dcd", reportInterval=n_save_steps, enforcePeriodicBox=False)
)
try:
    simulation.step(nsteps)
    simulation.saveState("output.xml")
except Exception as e:
    print(e)
    simulation.saveState("restart.xml")
    simulation.saveCheckpoint("checkpoint.chk")
