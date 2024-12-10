import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import subprocess
import win32api
import win32file
import os
import sys
import ctypes

class DriveProtectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drive Protection")
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#f3f3f3")  # Light background color for modern look

        # Load Icons
        self.load_icons()

        # Set up the GUI
        self.create_gui()

    def load_icons(self):
        """Load all icons as PhotoImage objects."""
        self.icons = {
            "lock_green": PhotoImage(file="01.png"),
            "lock_red": PhotoImage(file="02.png"),
            "refresh": PhotoImage(file="06.png"),
            "about": PhotoImage(file="13.png"),
        }

    def create_gui(self):
        """Create the main UI elements."""
        # App Title
        tk.Label(self.root, text="Drive protection", font=("Arial", 16, "bold"), bg="#f3f3f3").pack(pady=10)

        # Target Drive Section
        drive_frame = tk.Frame(self.root, bg="#f3f3f3")
        drive_frame.pack(pady=20)
        tk.Label(drive_frame, text="Target Drive:", font=("Arial", 12), bg="#f3f3f3").grid(row=0, column=0, padx=10, pady=5)
        self.target_drive_combo = ttk.Combobox(drive_frame, state="readonly", width=30)
        self.target_drive_combo.grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(drive_frame, image=self.icons["refresh"], command=self.refresh_drives).grid(row=0, column=2, padx=10)

        # Action Buttons
        button_frame = tk.Frame(self.root, bg="#f3f3f3")
        button_frame.pack(pady=20)
        ttk.Button(
            button_frame,
            text="Start Protection",
            image=self.icons["lock_green"],
            compound="left",
            command=self.start_protection,
            width=20
        ).grid(row=0, column=0, padx=20, pady=5)
        ttk.Button(
            button_frame,
            text="Stop Protection",
            image=self.icons["lock_red"],
            compound="left",
            command=self.stop_protection,
            width=20
        ).grid(row=0, column=1, padx=20, pady=5)

        # About Us Button
        ttk.Button(
            self.root,
            text="About Us",
            command=self.show_about_us,
            width=20
        ).pack(pady=10)

        # Footer
        tk.Label(self.root, text="© 2024 Drive protection", font=("Arial", 10), bg="#f3f3f3").pack(side="bottom", pady=10)

        # Load initial drive list
        self.refresh_drives()

    def get_external_drives(self):
        """Returns a list of external drives with their names and letters."""
        drives = []
        drive_bitmask = win32api.GetLogicalDrives()
        for i in range(26):
            drive_letter = f"{chr(65 + i)}:\\"
            if drive_bitmask & (1 << i):
                drive_type = win32file.GetDriveType(drive_letter)
                if drive_type == win32file.DRIVE_REMOVABLE:
                    try:
                        volume_info = win32api.GetVolumeInformation(drive_letter)
                        drives.append(f"{volume_info[0]} ({drive_letter})")  # Volume name with drive letter
                    except Exception:
                        drives.append(f"Unknown ({drive_letter})")  # Handle drives without volume labels
        return drives

    def refresh_drives(self):
        """Refreshes the list of external drives."""
        external_drives = self.get_external_drives()
        if not external_drives:
            messagebox.showinfo("No Drives Found", "No external drives detected.")
        self.target_drive_combo['values'] = external_drives
        if external_drives:
            self.target_drive_combo.current(0)  # Select the first drive by default

    def start_protection(self):
        """Sets the permissions of the selected drive to grant Read & Execute, Read permissions to Everyone, and Deny Write."""
        selected_drive = self.target_drive_combo.get()
        if not selected_drive:
            messagebox.showerror("Error", "Please select a drive.")
            return
        drive_letter = selected_drive.split("(")[-1][:-1]  # Extract drive letter
        if not drive_letter:
            messagebox.showerror("Error", "Invalid drive selected.")
            return
        try:
            # Check if the drive is accessible before proceeding
            if not os.path.exists(drive_letter + "\\"):
                raise Exception(f"Drive {drive_letter} is not accessible or doesn't exist.")
            
            # Grant Read & Execute and Read permissions, and Deny Write on files and folders
            command_grant = f'icacls {drive_letter}\\ /grant Everyone:(RX) /grant Everyone:(R)'

            # Deny Write permissions on files and subfolders (excluding the root)
            command_deny = f'icacls {drive_letter}\\* /deny Everyone:(W)'

            # Apply the commands
            subprocess.run(command_grant, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(command_deny, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            messagebox.showinfo("Success", f"Permissions updated for {drive_letter}: Read & Execute, Read granted. Write access denied.")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip() if e.stderr else "Unknown error"
            messagebox.showerror("Error", f"Failed to modify the drive: {error_message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def stop_protection(self):
        """Restores Full Control, Modify, Write, and Special Permissions on the selected drive."""
        selected_drive = self.target_drive_combo.get()
        if not selected_drive:
            messagebox.showerror("Error", "Please select a drive.")
            return
        drive_letter = selected_drive.split("(")[-1][:-1]  # Extract drive letter
        if not drive_letter:
            messagebox.showerror("Error", "Invalid drive selected.")
            return
        try:
            # Check if the drive is accessible before proceeding
            if not os.path.exists(drive_letter + "\\"):
                raise Exception(f"Drive {drive_letter} is not accessible or doesn't exist.")
            
            # Grant full control, modify, and write permissions back
            command = f'icacls {drive_letter}\\ /grant Everyone:(F)'
            result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                raise Exception(f"Failed to restore permissions: {result.stderr.decode().strip()}")
            
            messagebox.showinfo("Success", f"Permissions restored for {drive_letter}.")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip() if e.stderr else "Unknown error"
            messagebox.showerror("Error", f"Failed to restore permissions: {error_message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def show_about_us(self):
        """Displays information about the application."""
        messagebox.showinfo("About Us", "Drive Protection tool\n\nDeveloped by [Harish patel & Team].\nProtect your removable drives efficiently.")

# Function to check if the script is running as administrator
def is_admin():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

# Function to restart the script with administrative privileges
def run_as_admin():
    if not is_admin():
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([f'"{param}"' for param in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit(0)

# Run the application
if __name__ == "__main__":
    run_as_admin()
    root = tk.Tk()
    app = DriveProtectionApp(root)
    root.mainloop()
