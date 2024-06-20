#!/bin/bash

# Crie diretórios para cada cgroup necessário
sudo mkdir -p /sys/fs/cgroup/cpu
sudo mkdir -p /sys/fs/cgroup/cpuacct
sudo mkdir -p /sys/fs/cgroup/cpuset
sudo mkdir -p /sys/fs/cgroup/devices
sudo mkdir -p /sys/fs/cgroup/freezer
sudo mkdir -p /sys/fs/cgroup/memory
sudo mkdir -p /sys/fs/cgroup/blkio
sudo mkdir -p /sys/fs/cgroup/perf_event

# Adicione entradas ao /etc/fstab
echo 'cgroup  /sys/fs/cgroup/cpu         cgroup  cpu         0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/cpuacct     cgroup  cpuacct     0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/cpuset      cgroup  cpuset      0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/devices     cgroup  devices     0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/freezer     cgroup  freezer     0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/memory      cgroup  memory      0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/blkio       cgroup  blkio       0  0' | sudo tee -a /etc/fstab >/dev/null
echo 'cgroup  /sys/fs/cgroup/perf_event  cgroup  perf_event  0  0' | sudo tee -a /etc/fstab >/dev/null

# Monte todos os cgroups

sudo mount -a

# Verifique se os cgroups foram montados corretamente

sudo ls -l /sys/fs/cgroup