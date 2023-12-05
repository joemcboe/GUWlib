import paramiko
import os
import textwrap
import re


def copy_file_to_remote(local_path, remote_path, username_env_var, password_env_var,
                        hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """

    Args:
        local_path:
        remote_path:
        username_env_var:
        password_env_var:
        hostname:
        port:

    Returns:

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


def run_commands_on_remote(command, username_env_var, password_env_var,
                           hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Run multiple commands on a remote machine via SSH.

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


def run_command_with_output_trigger(command, username_env_var, password_env_var,
                                    trigger_string, hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Run a command on a remote machine via SSH and monitor the output until a trigger string is found.

    Args:
        command (str): Command to be executed on the remote machine.
        username_env_var (str): The environment variable containing the SSH username.
        password_env_var (str): The environment variable containing the SSH password.
        trigger_string (str): The string to monitor in the command output.
        hostname (str): The hostname or IP address of the remote machine. Default is 'phoenix.hlr.rz.tu-bs.de'.
        port (int): The SSH port of the remote machine. Default is 22.

    Returns:
        str: Output of the command until the trigger string is found.
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
        stdin, stdout, stderr = ssh_client.exec_command(command, bufsize=1)

        # Monitor the output until the trigger string is found
        while True:
            line = stdout.readline()
            if not line:
                break  # Break if no more output

            print(line, end='')  # Print the output in real-time

            output += line

            if re.search(trigger_string, line):
                print(f"Trigger string '{trigger_string}' found in the output.")
                break

        # Print any errors
        if stderr:
            print(stderr.read().decode())

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssh_client.close()
        return output
