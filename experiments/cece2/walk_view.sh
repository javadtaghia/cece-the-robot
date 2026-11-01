#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
export GZ_PARTITION="${GZ_PARTITION:-cece2_view}"
cece2_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 "$cece2_dir/focus_gazebo.py"
exec python3 "$cece2_dir/run_gazebo.py" --steps "${1:-40}"
