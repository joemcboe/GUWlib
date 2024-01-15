import paramiko
import os
import re
import time
import sys


def copy_file_to_remote(local_path, remote_path, username_env_var, password_env_var,
                        hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Copy a file from the local machine to a remote machine using SSH.

    Args:
    --------------
        local_path (str): The path of the file on the local machine.
        remote_path (str): The destination path on the remote machine.
        username_env_var (str): The environment variable containing the SSH username.
        password_env_var (str): The environment variable containing the SSH password.
        hostname (str): The hostname or IP address of the remote machine. Default is 'phoenix.hlr.rz.tu-bs.de'.
        port (int): The SSH port. Default is 22.

    Returns:
    ----------------
        None

    Raises:
    ----------------
        ValueError: If the required environment variables (username and password) are not set.
        FileNotFoundError: If the local file does not exist.
    """
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError as e:
        raise ValueError(f"Error: Missing environment variable {e}. Please set {username_env_var}"
                         f"and {password_env_var} before running the script.")

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, port, ssh_username, ssh_password)
        sftp = ssh_client.open_sftp()
        remote_directory, file_name = os.path.split(remote_path)

        try:
            sftp.stat(remote_directory)
        except FileNotFoundError:
            sftp.mkdir(remote_directory)

        sftp.put(local_path, remote_path.replace('\\', '/'))
        sftp.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssh_client.close()


def copy_file_from_remote(remote_path, local_path, username_env_var, password_env_var,
                          hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Copy a file from a remote machine (UNIX) to the local machine (WINDOWS) using SSH.

    Args:
        remote_path (str): The path of the file on the remote machine.
        local_path (str): The destination path on the local machine.
        username_env_var (str): The environment variable containing the SSH username.
        password_env_var (str): The environment variable containing the SSH password.
        hostname (str): The hostname or IP address of the remote machine. Default is 'phoenix.hlr.rz.tu-bs.de'.
        port (int): The SSH port. Default is 22.

    Returns:
        None
    """
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError as e:
        raise ValueError(f"Error: Missing environment variable {e}. Please set {username_env_var}"
                         f"and {password_env_var} before running the script.")

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, port, ssh_username, ssh_password)
        sftp = ssh_client.open_sftp()

        # Check if the remote file exists
        try:
            sftp.stat(remote_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Remote file '{remote_path}' not found.")

        # Create the local directory if it doesn't exist
        local_directory = os.path.dirname(local_path)
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        # Download the file
        sftp.get(remote_path, local_path)
        sftp.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssh_client.close()


def run_commands_on_remote(command, username_env_var, password_env_var,
                           hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Run a command on a remote machine via SSH.

    Args:
        command (str): Command to be executed on the remote machine.
        username_env_var (str): The environment variable containing the SSH username.
        password_env_var (str): The environment variable containing the SSH password.
        hostname (str): The hostname or IP address of the remote machine. Default is 'phoenix.hlr.rz.tu-bs.de'.
        port (int): The SSH port of the remote machine. Default is 22.

    Returns:
        None
    """
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError as e:
        raise ValueError(f"Error: Missing environment variable {e}. Please set {username_env_var}"
                         f" and {password_env_var} before running the script.")

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    output = ''
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, port, ssh_username, ssh_password)

        print(f"Executing command: {command}")

        # Execute the command on the remote machine
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Print the command output
        output = stdout.read().decode('utf-8')
        print(output)

        # Print any errors
        if stderr:
            print(stderr.read().decode())

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssh_client.close()
        return output


def tail_log_file_with_regex_trigger(username_env_var, password_env_var, regex_patterns, log_file_path,
                                     hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError as e:
        raise ValueError(f"Error: Missing environment variable {e}. "
                         f"Please set {username_env_var} and {password_env_var} before running the script.")

    # Create an SSH client
    ssh = paramiko.SSHClient()

    try:
        # Connect to the remote server
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, ssh_username, ssh_password)
        # ssh.connect(hostname, username=ssh_username, password=ssh_password)

        # Start an interactive shell
        ssh_shell = ssh.invoke_shell()

        # Send the 'tail -f' command to the shell
        ssh_shell.send("tail -f {}\n".format(log_file_path).encode('utf-8'))

        # Wait for the command to start producing output
        time.sleep(2)

        # Accumulate the content of the log file
        log_content = ""

        # Compile the regex patterns
        compiled_patterns = [re.compile(pattern) for pattern in regex_patterns]

        # Read and print the output continuously
        while True:
            if ssh_shell.recv_ready():
                output = ssh_shell.recv(1024).decode('utf-8')
                sys.stdout.write(output)
                sys.stdout.flush()

                # Accumulate the content of the log file
                log_content += output

                # Check if any of the regex patterns match the log content
                if any(pattern.search(log_content) for pattern in compiled_patterns):
                    break

    finally:
        # Close the SSH connection
        ssh.close()

    # Return the accumulated content of the log file
    return log_content
