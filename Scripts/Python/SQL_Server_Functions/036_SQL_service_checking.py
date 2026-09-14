import subprocess
import sys


# ============================================================
# Configuration
# ============================================================

KUBE_CONTEXT = "kind-carddata"
DATABASE_NAME = "carddata"

DB_PORT = 5436

# PostgreSQL Kubernetes Service
DB_SERVICE = "carddata-postgresql"

# PostgreSQL credentials
DB_USER = "postgres"
DB_PASSWORD = "postgres"


# ============================================================
# Status codes
# ============================================================

STATUS_OK = 0
STATUS_CLUSTER_UNAVAILABLE = 1
STATUS_DATABASE_NOT_FOUND = 2
STATUS_PORT_UNREACHABLE = 3
STATUS_DATABASE_CONNECTION_FAILED = 4


# Helper

def run_command(command):

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout.strip(), result.stderr.strip()


# Check Kubernetes context

def check_cluster():

    code, stdout, stderr = run_command([
        "kubectl",
        "--context", KUBE_CONTEXT,
        "cluster-info"
    ])

    if code != 0:
        print("Kubernetes cluster is not reachable.")
        print(stderr)
        return False

    print("Kubernetes cluster is reachable.")
    return True


# Check database service

def check_database_service():

    code, stdout, stderr = run_command([
        "kubectl",
        "--context", KUBE_CONTEXT,
        "get",
        "service",
        DB_SERVICE
    ])

    if code != 0:
        print(f"Database service '{DB_SERVICE}' not found.")
        print(stderr)
        return False

    print(f"Database service '{DB_SERVICE}' found.")
    return True


# ============================================================
# Check PostgreSQL port

def check_port():

    # Execute nc inside the Kubernetes cluster by using
    # a temporary PostgreSQL client container.
    command = [
        "kubectl",
        "--context", KUBE_CONTEXT,
        "run",
        "postgres-port-check",
        "--rm",
        "-i",
        "--restart=Never",
        "--image=postgres:17",
        "--",
        "pg_isready",
        "-h",
        DB_SERVICE,
        "-p",
        str(DB_PORT)
    ]

    code, stdout, stderr = run_command(command)

    print(stdout)

    if code != 0:
        print("PostgreSQL port is not reachable.")
        print(stderr)
        return False

    print("PostgreSQL port is reachable.")
    return True


# ============================================================
# Check actual database connection

def check_database_connection():

    command = [
        "kubectl",
        "--context", KUBE_CONTEXT,
        "run",
        "postgres-db-check",
        "--rm",
        "-i",
        "--restart=Never",
        "--image=postgres:17",
        "--env",
        f"PGPASSWORD={DB_PASSWORD}",
        "--",
        "psql",
        "-h",
        DB_SERVICE,
        "-p",
        str(DB_PORT),
        "-U",
        DB_USER,
        "-d",
        DATABASE_NAME,
        "-c",
        "SELECT 1;"
    ]

    code, stdout, stderr = run_command(command)

    if code != 0:
        print("PostgreSQL server is reachable, but database connection failed.")
        print(stderr)
        return False

    print("Database connection successful.")
    print(stdout)

    return True


# ============================================================
# Main
# ============================================================

def main():

    print(f"Checking database '{DATABASE_NAME}'")
    print(f"Cluster context: {KUBE_CONTEXT}")
    print(f"Service: {DB_SERVICE}")
    print(f"Port: {DB_PORT}")
    print()

    # 1. Kubernetes cluster
    if not check_cluster():
        return STATUS_CLUSTER_UNAVAILABLE

    # 2. Database service
    if not check_database_service():
        return STATUS_DATABASE_NOT_FOUND

    # 3. PostgreSQL port
    if not check_port():
        return STATUS_PORT_UNREACHABLE

    # 4. Actual database connection
    if not check_database_connection():
        return STATUS_DATABASE_CONNECTION_FAILED

    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())