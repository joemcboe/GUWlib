"""
Mainly Paramiko wrappers.
"""
import paramiko
import os
import tkinter as tk
from tkinter import simpledialog


class CredentialsDialog(simpledialog.Dialog):
    """
    Class to open a dialog window with two edit fields for username / password.
    """
    def __init__(self, parent, title):
        """
        :param tkinter.Tk parent: Parent object.
        :param str title: Title of the dialog.
        :ivar tkinter.Entry e1: Edit field for username.
        :ivar tkinter.Entry e2: Edit field for password.
        :ivar tuple[str, str]: Tuple with (username, password).
        """

        self.result = None
        self.e2 = None
        self.e1 = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Username:").grid(row=0)
        tk.Label(master, text="Password:").grid(row=1)

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master, show="*")

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1

    def apply(self):
        self.result = (self.e1.get(), self.e2.get())


def get_ssh_credentials(hostname):
    """
    Retrieve SSH credentials either from user environment variables or by prompting the user
    with a tkinter GUI dialog.

    :param str hostname: Name of the SSH host.
    :return: Tuple (username, password)
    """
    username_env_var = 'tubs_username'
    password_env_var = 'tubs_password'

    try:
        ssh_username = os.environ[username_env_var]
        ssh_password = os.environ[password_env_var]
    except KeyError:
        print(f"Please authorize SSH connection to {hostname}. Credentials are requested with a "
              f"dialog box.\n(You can also set the username and password as user environment variables "
              f"{username_env_var} and {password_env_var} to not get asked again next time.)")

        root = tk.Tk()
        root.withdraw()
        dialog = CredentialsDialog(root, 'Enter SSH credentials')
        ssh_username, ssh_password = dialog.result

    return ssh_username, ssh_password


def copy_file_to_remote(local_path, remote_path, ssh_username, ssh_password, hostname, port):
    """
    Copy a file from the local machine to a remote machine via Secure Shell (SSH).

    :param str local_path: The source path of the file on the local machine.
    :param str remote_path: The destination path on the remote machine.
    :param str ssh_username: SSH username.
    :param str ssh_password: SSH password.
    :param str hostname: The hostname or IP address of the remote machine.
    :param int port: The SSH port to use.

    :return: None
    :raise Error: If the SSH connection cannot be established.
    :raise FileNotFoundError: If the local file does not exist.
    """

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


def copy_file_from_remote(remote_path, local_path, ssh_username, ssh_password, hostname, port):
    """
    Copy a file from the remote machine to the local machine via Secure Shell (SSH).

    :param str remote_path: The source path of the file on the remote machine.
    :param str local_path: The destination path on the local machine.
    :param str ssh_username: SSH username.
    :param str ssh_password: SSH password.
    :param str hostname: The hostname or IP address of the remote machine.
    :param int port: The SSH port to use.

    :return: None

    :raise ValueError: If the environment variables (username and password) are not set.
    :raise FileNotFoundError: If the local file does not exist.
    """
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


def run_commands_on_remote(command, ssh_username, ssh_password, hostname, port):
    """
    Run a command on a remote machine via Secure Shell (SSH).

    :param str command: The command to run on the remote machine.
    :param str ssh_username: SSH username.
    :param str ssh_password: SSH password.
    :param str hostname: The hostname or IP address of the remote machine.
    :param int port: The SSH port to use.

    :return: The standard output stream of the executed command.

    :raise ValueError: If the environment variables (username and password) are not set.
    :raise FileNotFoundError: If the local file does not exist.
    """
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
