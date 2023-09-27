import tkinter as tk
from tkinter import messagebox, simpledialog, Menu
import os
import sys
import subprocess
import requests
from bs4 import BeautifulSoup
import webbrowser

class ProgramInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Package Manager")
        self.geometry("800x400")
        self.minsize(500, 300)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.installed_programs = self.get_installed_programs()
        self.search_cache = {}

        # Frame for the installed apps list
        self.installed_frame = tk.Frame(self)
        self.installed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.installed_label = tk.Label(self.installed_frame, text="Installed Programs:")
        self.installed_label.pack(pady=10)

        self.installed_listbox = tk.Listbox(self.installed_frame, width=40, height=15)
        self.installed_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.installed_listbox.bind("<Button-3>", self.show_remove_menu)
        self.installed_listbox_scrollbar = tk.Scrollbar(self.installed_frame, command=self.installed_listbox.yview)
        self.installed_listbox.config(yscrollcommand=self.installed_listbox_scrollbar.set)
        self.installed_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame for the searched apps list
        self.searched_frame = tk.Frame(self)
        self.searched_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.search_label = tk.Label(self.searched_frame, text="Search for Programs:")
        self.search_label.pack(pady=10)

        self.search_entry = tk.Entry(self.searched_frame)
        self.search_entry.pack(fill=tk.X, padx=10)

        self.search_button = tk.Button(self.searched_frame, text="Search", command=self.search_programs)
        self.search_button.pack(pady=5)

        self.searched_label = tk.Label(self.searched_frame, text="Searched Programs:")
        self.searched_label.pack(pady=10)

        self.searched_listbox = tk.Listbox(self.searched_frame, width=40, height=15)
        self.searched_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.searched_listbox.bind("<Button-3>", self.show_install_menu)
        self.searched_listbox_scrollbar = tk.Scrollbar(self.searched_frame, command=self.searched_listbox.yview)
        self.searched_listbox.config(yscrollcommand=self.searched_listbox_scrollbar.set)
        self.searched_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.install_menu = tk.Menu(self, tearoff=0)
        self.install_menu.add_command(label="Install", command=self.install_selected)

        self.remove_menu = tk.Menu(self, tearoff=0)
        self.remove_menu.add_command(label="Remove", command=self.remove_selected)

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Update Pip", command=self.update_pip)
        self.file_menu.add_command(label="Upgrade Pip", command=self.upgrade_pip)
        self.file_menu.add_command(label="Fix Issues", command=self.fix_issues)
        self.file_menu.add_command(label="Update Python", command=self.update_python)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.update_installed_list()

    def get_installed_programs(self):
        try:
            installed_programs = subprocess.check_output([sys.executable, '-m', 'pip', 'list'])
            return installed_programs.decode("utf-8")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to fetch installed programs.")
            return ""

    def update_installed_list(self):
        self.installed_listbox.delete(0, tk.END)
        self.installed_listbox.insert(tk.END, *self.installed_programs.splitlines())

    def search_programs(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return

        if query in self.search_cache:
            search_result = self.search_cache[query]
        else:
            search_result = self.perform_search(query)
            self.search_cache[query] = search_result

        self.searched_listbox.delete(0, tk.END)
        self.searched_listbox.insert(tk.END, *search_result.splitlines())

    def perform_search(self, query):
        try:
            search_result = subprocess.check_output([sys.executable, '-m', 'pip', 'search', query])
            return search_result.decode("utf-8")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to search for programs.")
            return ""

    def install_selected(self):
        selected_program = self.searched_listbox.get(tk.ACTIVE)
        if not selected_program:
            messagebox.showwarning("Warning", "Please select a program to install.")
            return

        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', selected_program.split()[0]], check=True)
            messagebox.showinfo("Success", f"{selected_program.split()[0]} installed successfully.")
            self.installed_programs = self.get_installed_programs()
            self.update_installed_list()
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"Failed to install {selected_program.split()[0]}.")

    def remove_selected(self):
        selected_program = self.installed_listbox.get(tk.ACTIVE)
        if not selected_program:
            messagebox.showwarning("Warning", "Please select a program to remove.")
            return

        try:
            subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', selected_program.split()[0]], check=True)
            messagebox.showinfo("Success", f"{selected_program.split()[0]} removed successfully.")
            self.installed_programs = self.get_installed_programs()
            self.update_installed_list()
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"Failed to remove {selected_program.split()[0]}.")

    def show_install_menu(self, event):
        self.install_menu.post(event.x_root, event.y_root)

    def show_remove_menu(self, event):
        self.remove_menu.post(event.x_root, event.y_root)

    def update_pip(self):
        try:
            pip_commands = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip']
            subprocess.run(pip_commands, check=True)
            messagebox.showinfo("Success", "Pip updated successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to update pip.")

    def upgrade_pip(self):
        try:
            pip_commands = [sys.executable, '-m', 'pip', 'list', '--outdated']
            result = subprocess.run(pip_commands, capture_output=True, text=True, check=True)
            if result.stdout:
                packages_to_update = result.stdout.splitlines()[2:]
                for package_info in packages_to_update:
                    package_name, _, latest_version, _ = package_info.split()
                    pip_commands = [sys.executable, '-m', 'pip', 'install', '--upgrade', package_name]
                    subprocess.run(pip_commands, check=True)
                messagebox.showinfo("Success", "All packages updated successfully.")
            else:
                messagebox.showinfo("Info", "No outdated packages found.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to upgrade packages.")

    def fix_issues(self):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'check'], capture_output=True, text=True)
            if result.stdout:
                messagebox.showinfo("Info", result.stdout)
            else:
                messagebox.showinfo("Info", "No issues found.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to check issues.")

    def get_python_versions(self):
        url = "https://www.python.org/downloads/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        versions = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith("/downloads/release/python-"):
                version = href.split("-")[2]
                if version.startswith(("2", "3")):  # Filter out pre-releases and other versions
                    versions.append(version)

        return versions

    def update_python(self):
        python_versions = self.get_python_versions()
        if not python_versions:
            messagebox.showwarning("Warning", "No Python versions found.")
            return

        version = python_versions[-1]
        if len(python_versions) > 1:
            version = simpledialog.askstring("Install Python", "Enter Python version to install:", initialvalue=version)

        if version:
            try:
                url = f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe" if sys.platform.startswith('win') else f"https://www.python.org/ftp/python/{version}/Python-{version}.tgz"
                webbrowser.open(url)
                messagebox.showinfo("Info", f"Please download and install Python {version}.")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening browser: {e}")

if __name__ == "__main__":
    app = ProgramInstaller()
    app.mainloop()
