import subprocess
import re
import os


def parse_conn_str(conn_str):
    """
    Parse PostgreSQL connection string in form:
    postgresql://user:pass@host:port/dbname
    """
    m = re.match(r'postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)', conn_str)
    if not m:
        raise ValueError("Connection string must be in the form postgresql://user:pass@host:port/dbname")
    return m.groups()

def dump_full_db(db_conn_str, dump_file="dump.sql"):
    user, password, host, port, dbname = parse_conn_str(db_conn_str)



    if os.path.exists(dump_file):
        choice = input(f"Dump file '{dump_file}' already exists. Overwrite it or rename the dump file? \n1: Overwrite 2: Rename \n").strip().lower()
        if choice == '1':
            print(f"Overwriting dump file: {dump_file}")
        elif choice == '2':
            new_name = input("Enter new dump file name: ").strip()
            dump_file = new_name
        else :
            print("Invalid choice. Exiting.")
            return
    dump_cmd = [
        "pg_dump",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", dbname,
        "-f", dump_file
    ]

    env = {"PGPASSWORD": password, **os.environ}
    print(f"Dumping full database '{dbname}' to {dump_file} ...")
    subprocess.run(dump_cmd, check=True, env=env)
    print("Dump completed!")
    return dump_file


def restore_full_db(db_conn_str, dump_file="dump.sql"):
    user, password, host, port, dbname = parse_conn_str(db_conn_str)

    if not os.path.exists(dump_file):
        raise FileNotFoundError(f"Dump file not found: {dump_file}")

    restore_cmd = [
        "psql",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", dbname,
        "-f", dump_file,
    ]

    env = {"PGPASSWORD": password, **os.environ}
    print(f"Restoring full database '{dbname}' from {dump_file} ...")
    subprocess.run(restore_cmd, check=True, env=env)
    os.remove(dump_file)  # Remove the dump file after restore
    print("Restore completed!")


if __name__ == "__main__":
    source_conn = input("Enter source DB connection string (e.g. postgresql://user:pass@host:port/dbname): ").strip()
    dest_conn = input("Enter destination DB connection string (e.g. postgresql://user:pass@host:port/dbname): ").strip()
    dump_file = input("Enter dump file name (default: dump.sql): ").strip() or "dump.sql"

    file = dump_full_db(source_conn, dump_file)
    restore_full_db(dest_conn, file)
