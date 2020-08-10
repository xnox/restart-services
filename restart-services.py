#!/usr/bin/python3
import os
import glob
import subprocess
import itertools


def list_services_to_restart():
    services_to_restart = []
    for cgroup in glob.iglob("/sys/fs/cgroup/unified/system.slice/*.service"):
        pids = []
        with open(os.path.join(cgroup, "cgroup.procs")) as f:
            pids = f.read().split()

        deleted_files = []
        for p in pids:
            with open("/proc/{p}/smaps".format(p=p)) as f:
                for line in f:
                    if line.endswith(" (deleted)\n"):
                        deleted_files.append(line.rsplit(maxsplit=2)[-2])
        deleted_files_alt = [
            name[4:] for name in deleted_files if name.startswith("/usr/")
        ]
        for filename in itertools.chain(deleted_files, deleted_files_alt):
            try:
                subprocess.check_call(
                    ["dpkg", "-S", filename],
                    stdin=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                continue
            services_to_restart.append(os.path.basename(cgroup))
            break
    return services_to_restart


if __name__ == "__main__":
    services_to_restart = list_services_to_restart()
    if services_to_restart:
        print(' '.join(services_to_restart))
