from openmm import *
from openmm.app import *
from openmm.unit import *
import numpy as np


forcefield = ForceField("forcefield.xml")
modeller = Modeller(topology=Topology(), positions=[])
modeller.addSolvent(ForceField("tip3p.xml"), model="tip3p", numAdded=256)
with open("input.pdb", "w") as f:
    PDBFile.writeFile(modeller.topology, modeller.positions, file=f)

system = forcefield.createSystem(
    modeller.topology,
    nonbondedMethod=PME,
    nonbondedCutoff=7 * angstrom,
    rigidWater=True,
    constraints="None",
    polarization="direct",
)

with open("system.xml", "w") as f:
    f.write(XmlSerializer.serialize(system))

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
