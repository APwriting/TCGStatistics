import subprocess
import sys
import yaml

from sqlalchemy import create_engine, text

# ============================================================
# Configuration
# ============================================================

KUBE_CONTEXT = "kind-carddata"
DATABASE_NAME = "MTGDATA"

DB_PORT = 5436

# PostgreSQL Kubernetes Service
DB_SERVICE = "postgres"

# PostgreSQL credentials
DB_USER = "postgres"
DB_PASSWORD = "postgres"


#Getting User data from deployment YAML:

def get_sql_credentials(deployment_yaml):
    """
    Read PostgreSQL username and password from a Kubernetes
    Deployment YAML file.

    Returns:
        tuple[str, str]: username, password
    """

    with open(deployment_yaml, "r", encoding="utf-8") as file:
        deployment = yaml.safe_load(file)

    containers = deployment["spec"]["template"]["spec"]["containers"]

    for container in containers:
        for env in container.get("env", []):

            if env["name"] == "POSTGRES_USER":
                username = env["value"]

            elif env["name"] == "POSTGRES_PASSWORD":
                password = env["value"]

    return username, password

deploy_yaml_path = "../Kubernetes_cluster_initiation_SQL_database/postgreSQL_deployment__credentials.yaml"
DB_USER, DB_PASSWORD  = get_sql_credentials(deployment_yaml = deploy_yaml_path)

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

def get_service_ip(service_name="postgres"):
    result = subprocess.run(
        [
            "kubectl",
            "get",
            "service",
            service_name,
            "-o",
            "jsonpath={.spec.clusterIP}"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    service_ip = result.stdout.strip()

    if not service_ip:
        raise RuntimeError(
            f"Could not determine IP address of service '{service_name}'."
        )

    return service_ip


# ============================================================
# Main
# ============================================================

def main():

    print(f"Checking database '{DATABASE_NAME}'")
    print(f"Cluster context: {KUBE_CONTEXT}")
    print(f"Service: {DB_SERVICE}")
    print(f"Port: {DB_PORT}")
    print()
    #Updating User data from YAML if necessary



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

    Service_IP = get_service_ip(service_name=DB_SERVICE)

    engine = create_engine(
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{Service_IP}:{DB_PORT}/{DATABASE_NAME}",
        connect_args={"connect_timeout": 5}
    )

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(result.scalar())



    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())