## **Overview**

This documentation provides a comprehensive guide to the custom Command & Control (C2) server implementation we've developed. The system consists of a server component that can receive connections from multiple client agents, allowing for remote command execution, file transfers, screenshot capture, and interactive shell sessions.

## **Architecture**

The C2 system follows a client-server architecture with the following components:

1. **C2 Server**: Central command center that accepts connections from multiple agents
2. **C2 Agent**: Client-side component that runs on target systems and connects back to the server
3. **Communication Protocol**: Socket-based protocol for command transmission and data exchange
4. **Optional Encryption**: AES encryption utilities for securing communication channels

The system is available in two interfaces:

- Command-line interface (CLI) for traditional terminal-based operation
- Graphical user interface (GUI) for intuitive user interaction

## **Components**

### Server (c2_server.py)

The core server component that handles:

- Listening for incoming connections
- Maintaining client sessions
- Command dispatching
- File uploads/downloads
- Screenshot capture
- Reverse shell sessions

### Agent (c2_agent.py)

The client-side component that:

- Connects to the C2 server
- Executes commands received from the server
- Sends command output back to server
- Handles file transfers
- Captures screenshots
- Provides shell access
- Automatically reconnects if connection is lost

### GUI Interface (c2_server_gui.py)

Provides a user-friendly interface for:

- Server management with visual indicators
- Client connection visualization
- Command execution through tabbed interface
- Simplified file operations with file browser
- Screenshot capture with visual elements
- Streamlined shell access
- Command history and log viewing

### Encryption Utilities (crypto_utils.py)

Offers optional encryption capabilities using:

- AES-CBC encryption for secure communication
- Key generation and management
- Base64 encoding for transmission

## **Features**

### Connection Management

- Multiple simultaneous client connections
- Persistent connections with automatic reconnection
- Client identification via hostname and username

### Command Execution

- Remote command execution on target systems
- Command output capture and display
- Error handling and reporting

### File Operations

- Upload files to target systems
- Download files from target systems
- Progress tracking for large files

### Screenshot Capture

- Remote screenshot capability
- Automatic saving with timestamped filenames
- Custom save locations

### Shell Access

- Interactive shell sessions
- Command history
- Session management

### Security Features

- Optional AES encryption for communications
- Connection verification
- Proper resource cleanup

## **Technical Implementation**

### Communication Protocol

The C2 server and agent communicate using a straightforward protocol:

1. **Connection Initiation**:
    - Agent connects to server
    - Agent sends system information (hostname, username)
    - Server acknowledges connection
2. **Command Execution**:
    - Server sends command string
    - Agent executes command
    - Agent returns output
3. **File Transfers**:
    - Sender indicates file size
    - Receiver acknowledges readiness
    - File data is transmitted in chunks
    - Confirmation is sent upon completion
4. **Shell Sessions**:
    - Server initiates shell mode
    - Commands and responses flow continuously
    - Special "exit_shell" command terminates the session

### Error Handling

The system implements robust error handling:

- Socket timeouts to detect lost connections
- Exception catching for command execution
- Reconnection attempts for dropped connections
- Resource cleanup on termination

### Performance Considerations

- Non-blocking server design using threading
- Chunked file transfers to handle large files
- Configurable timeouts for various operations

## **Using the C2 Server**

### CLI Version

1. **Starting the server**:
    
    python c2_server.py
    
2. **Basic commands**:
    - `help`: Display available commands
    - `list`: List connected clients
    - `select <id>`: Select a client to interact with
    - `upload <src> <dst>`: Upload a file to client
    - `download <src> <dst>`: Download a file from client
    - `screenshot <path>`: Take a screenshot
    - `shell`: Start a reverse shell session
    - `exit`: Disconnect from current client
    - `quit`: Exit the C2 server

### GUI Version

1. **Starting the server**:
    
    python c2_server_gui.py
    
2. **Using the interface**:
    - Server Control: Start/stop the server
    - Client List: View and select connected clients
    - Command Tabs: Execute different types of operations
    - Log Section: View operation history and results

### Agent Deployment

1. **Starting the agent**:
    
    python c2_agent.py [server_ip] [server_port]
    
2. **Deployment considerations**:
    - Default connection to 127.0.0.1:4444
    - Can be configured for external IP
    - Automatic reconnection attempts
    - Requires Python environment with dependencies

## **Security Considerations**

- This tool is designed for educational purposes and authorized security testing only.
- Usage on systems without explicit permission is illegal.
- The system does not include advanced obfuscation or anti-forensics capabilities.
- Communications can be encrypted using the provided crypto_utils.py module.

## **Requirements**

The system requires the following Python packages:

- pycryptodome==3.19.0 (for encryption)
- pyautogui==0.9.54 (for screenshots)
- Pillow==10.0.0 (image processing)

These can be installed using the provided requirements.txt file:

pip install -r requirements.txt
