import paramiko
import os
import re
import time
import sys
import tkinter as tk
from tkinter import simpledialog


def prompt_for_credentials():
    """
    Prompt the user for SSH credentials using a tkinter GUI dialog.

    :return: Tuple (username, password)
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    ssh_username = simpledialog.askstring("SSH Credentials", "Enter SSH username:")
    ssh_password = simpledialog.askstring("SSH Credentials", "Enter SSH password:", show='*')

    return ssh_username, ssh_password


def copy_file_to_remote(local_path, remote_path, username_env_var='tubs_username', password_env_var='tubs_password',
                        hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Copy a file from the local machine to a remote machine via Secure Shell (SSH).

    :param str local_path: The source path of the file on the local machine.
    :param str remote_path: The destination path on the remote machine.
    :param str username_env_var: The environment variable containing the SSH username (optional).
    :param str password_env_var: The environment variable containing the SSH password (optional).
    :param str hostname: The hostname or IP address of the remote machine.
    :param int port: The SSH port to use.

    :return: None

    :raise ValueError: If the environment variables (username and password) are not set.
    :raise FileNotFoundError: If the local file does not exist.
    """
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError:
        print(f"Please authorize SSH connection. Credentials are requested with a dialog box. (You can also set the "
              f"username and password as user environment variables {username_env_var} and {password_env_var} to "
              f"not get asked again next time.)")
        ssh_username, ssh_password = prompt_for_credentials()

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


def copy_file_from_remote(remote_path, local_path, username_env_var='tubs_username', password_env_var='tubs_password',
                          hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Copy a file from the remote machine to the local machine via Secure Shell (SSH).

    :param str remote_path: The source path of the file on the remote machine.
    :param str local_path: The destination path on the local machine.
    :param str username_env_var: The environment variable containing the SSH username (optional).
    :param str password_env_var: The environment variable containing the SSH password (optional).
    :param str hostname: The hostname or IP address of the remote machine.
    :param int port: The SSH port to use.

    :return: None

    :raise ValueError: If the environment variables (username and password) are not set.
    :raise FileNotFoundError: If the local file does not exist.
    """
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError:
        print(f"Please authorize SSH connection. Credentials are requested with a dialog box. (You can also set the "
              f"username and password as user environment variables {username_env_var} and {password_env_var} to "
              f"not get asked again next time.)")
        ssh_username, ssh_password = prompt_for_credentials()

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
        if not os.path.exists(local_directory) and not local_directory == '':
            os.makedirs(local_directory)

        # Download the file
        sftp.get(remote_path, local_path)
        sftp.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssh_client.close()


def run_commands_on_remote(command, username_env_var='tubs_username', password_env_var='tubs_password',
                           hostname='phoenix.hlr.rz.tu-bs.de', port=22):
    """
    Run a command on a remote machine via Secure Shell (SSH).

    :param str command: The command to run on the remote machine.
    :param str username_env_var: The environment variable containing the SSH username (optional).
    :param str password_env_var: The environment variable containing the SSH password (optional).
    :param str hostname: The hostname or IP address of the remote machine.
    :param int port: The SSH port to use.

    :return: The standard output stream of the executed command.

    :raise ValueError: If the environment variables (username and password) are not set.
    :raise FileNotFoundError: If the local file does not exist.
    """
    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError:
        print(f"Please authorize SSH connection. Credentials are requested with a dialog box. (You can also set the "
              f"username and password as user environment variables {username_env_var} and {password_env_var} to "
              f"not get asked again next time.)")
        ssh_username, ssh_password = prompt_for_credentials()

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
