#/usr/bin/python

#script here to delete Kubernetes clusters

import subprocess
import yaml

# Read YAML
with open("Kubernetes_cluster_names.yaml", "r") as file:
    config = yaml.safe_load(file)


# Get existing kind clusters
result = subprocess.run(
    ["kind", "get", "clusters"],
    capture_output=True,
    text=True
)

existing_clusters = result.stdout.splitlines()


# Delete clusters listed in YAML
for cluster in config["clusters"]:

    cluster_name = cluster["name"]

    if cluster_name in existing_clusters:

        subprocess.run(
            ["kind", "delete", "cluster", "--name", cluster_name],
            check=True
        )

        print(f"Cluster '{cluster_name}' deleted.")

    else:

        print(f"Cluster '{cluster_name}' does not exist.")