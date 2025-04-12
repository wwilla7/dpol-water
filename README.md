# dpol-water
This repository contains scripts to use the dPol (direct polarization) water model.
```
scripts:
        mpidforce:
                    forcefield.offxml: force field to run dPol water with MPIDForce.
                    run.py: script to run basic MD with OpenMM.
        amoebamultipoleforce:
                    forcefield.xml: OpenMM force field file to run dPol water with AmeobaMultipleForce.
                    run.py: script to run basic MD with OpenMM.
```

To run dPol water with MPIDForce, you need:
[MPIFOpenMMPlugin](https://github.com/andysim/MPIDOpenMMPlugin),
[openff-toolkit](https://github.com/openforcefield/openff-toolkit),
[openff-interchange](https://github.com/openforcefield/openff-interchange),
[dPol_plugin](https://github.com/wwilla7/dPol_plugin).
