#/usr/bin/python

#script to initiate a Kubernetes Cluster to store a postgreSQL database for TCG_data

import subprocess

cluster_name = "TCG_data_cluster"

result = subprocess.run(
    ["kind", "get", "clusters"],
    capture_output=True,
    text=True
)

if cluster_name not in result.stdout.splitlines():
    subprocess.run(
        ["kind", "create", "cluster", "--name", cluster_name],
        check=True
    )
    print("Cluster created.")
else:
    print("Cluster already exists.")
