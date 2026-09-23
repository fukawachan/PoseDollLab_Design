# Hardware compatibility snapshot

This folder contains only the protocol/kinematics/diagnostics/transport Python modules and their existing tests used by the hardware project. It does not contain the simulator GUI or its environment. The running simulator remains in the original DollSimulation project.

Provenance and byte hashes: [software_snapshot.json](../../docs/software_snapshot.json). Keep the existing folder layout because profile lookup and historical checks depend on it. Do not silently overwrite this snapshot when updating the UE project; compare protocol/profile hashes and rerun the hardware offline tests.
