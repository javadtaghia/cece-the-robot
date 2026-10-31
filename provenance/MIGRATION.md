# Cece consolidation

The main project studies were copied from `javadtaghia/xgoduck_hardware`
branch `codex/cece-consolidated-prototype`, commit `fe68231`. The new
repository has its own history; this was a file transfer, not a Git fork or
history import.

The transfer included all 514 tracked files in the old `experiments/cece`
and `experiments/otto` directories. Before committing, each copied file was
compared with the source using SHA-256. Nine text files were deliberately
updated to use the new checkout or local relative paths; the remaining files
matched. These counts describe the source at the time of migration, not future
changes.

Additional relevant material that was outside that Git checkout was copied
from the local workspace to [archive/workspace](../archive/workspace/README.md):
earlier CAD, KiCad drafts, prototype print plates, actuator and balance studies,
and reference data. Thirteen FreeCAD automatic backup documents from both
locations are preserved as files in the repository. Python caches, executable
environments, downloaded language models, credentials and transient logs were
not imported.

The former `simple_robot` workspace contained another copy of the selected
legacy Cece and KiCad folders; a SHA-256 comparison found those selected files
identical to the ones copied from the consolidated workspace.

Locally generated Wokwi firmware binaries and Gazebo files are not versioned:
they are built from the source using [the setup guide](../experiments/cece/START_HERE.md).
Earlier simulation results and design assessments remain historical evidence,
not proof of physical performance.
