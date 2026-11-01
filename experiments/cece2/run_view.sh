#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
export GZ_PARTITION="${GZ_PARTITION:-cece2_view}"
cece2_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 "$cece2_dir/build_gazebo_view.py"
exec gz sim -r "$cece2_dir/generated/cece2_room.sdf"
