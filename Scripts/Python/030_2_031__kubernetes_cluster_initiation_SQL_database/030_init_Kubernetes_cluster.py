#/usr/bin/python

#script to initiate a Kubernetes Cluster to store a postgreSQL database for TCG_data

import subprocess
import yaml

# Read cluster configuration
with open("clusters.yaml", "r") as file:
    config = yaml.safe_load(file)

cluster_name = "TCG_data_cluster"
# Get existing Kubernetes clusters
result = subprocess.run(
    ["kind", "get", "clusters"],
    capture_output=True,
    text=True
)

existing_clusters = result.stdout.splitlines()


# Create clusters from YAML data
for cluster in config["clusters"]:

    cluster_name = cluster["name"]

    if cluster_name not in existing_clusters:

        subprocess.run(
            ["kind", "create", "cluster", "--name", cluster_name],
            check=True
        )

        print(f"Cluster '{cluster_name}' created.")

    else:

        print(f"Cluster '{cluster_name}' already exists.")
