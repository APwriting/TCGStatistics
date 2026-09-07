import subprocess
import sys
from pathlib import Path



def get_clusters():
    """Get running PostgreSQL clusters from Kubernetes."""

    result = subprocess.run(
        ["kind", "get", "clusters"],
        capture_output=True,
        text=True
    )

    existing_clusters = result.stdout.splitlines()

    # Alphabetical order
    existing_clusters.sort()

    return existing_clusters


# Get running clusters
existing_clusters = get_clusters()

if not existing_clusters:
    print("No PostgreSQL clusters found.")
    sys.exit(0)

existing_clusters.sort()

print("Available Kubernetes clusters:")

for number, cluster in enumerate(existing_clusters, start=1):
    print(f"{number}. {cluster}")

choice = int(input("Select a cluster: "))

selected_cluster = existing_clusters[choice - 1]

print(f"Selected cluster: {selected_cluster}")
sys.exit()


def kubectl_apply(filename):
    result = subprocess.run(
        ["kubectl", "apply", "-f", str(filename)],
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        print(f"Error applying {filename}:")
        print(result.stderr)
        sys.exit(result.returncode)

    print(result.stdout)


# Check that Kubernetes is available
print("Checking Kubernetes...")
result = subprocess.run(
    ["kubectl", "cluster-info"],
    text=True,
    capture_output=True
)

if result.returncode != 0:
    print("Could not connect to Kubernetes.")
    print(result.stderr)
    sys.exit(1)


# Find YAML files relative to this Python script
script_dir = Path(__file__).parent

deployment = script_dir / "postgreSQL_deployment.yaml"
service = script_dir / "postgreSQL_service.yaml"


# Deploy PostgreSQL
print("Deploying PostgreSQL...")
kubectl_apply(deployment)

# Create PostgreSQL service
print("Creating PostgreSQL service...")
kubectl_apply(service)

print("\nPostgreSQL deployment complete!")
