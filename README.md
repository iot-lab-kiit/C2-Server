# Command and Control (C2) Server Project

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
![Hacktoberfest](https://img.shields.io/badge/hacktoberfest-2025-blueviolet.svg)

A sophisticated Command and Control (C2) server implementation built with Python, featuring both CLI and GUI interfaces for remote system management and administration. This project demonstrates advanced networking concepts, socket programming, and multi-threaded client management.

## 🎯 About the Project

This C2 server project is designed as an educational tool and system administration framework that showcases:

- **Advanced Network Programming**: Implements custom TCP protocol for client-server communication
- **Multi-threaded Architecture**: Handles multiple concurrent client connections seamlessly  
- **Cross-platform Compatibility**: Works on Windows, Linux, and macOS environments
- **Security Implementation**: Includes cryptographic utilities for secure communications
- **Dual Interface Design**: Offers both command-line and graphical user interfaces
- **File Management**: Robust file upload/download capabilities with integrity checking
- **Remote Administration**: Complete remote system control including shell access and screenshots

### Key Features

✅ **Multi-client Connection Handling** - Manage multiple remote agents simultaneously  
✅ **Remote Command Execution** - Execute system commands on connected clients  
✅ **Bidirectional File Transfers** - Upload and download files securely  
✅ **Screenshot Capabilities** - Capture and retrieve screen content from remote systems  
✅ **Interactive Reverse Shell** - Establish real-time shell sessions  
✅ **Modern GUI Interface** - User-friendly graphical management console  
✅ **Automatic Reconnection** - Persistent connections with fault tolerance  
✅ **Encrypted Communications** - Optional cryptographic protection for data in transit

### Project Components

- `c2_server.py` - Command-line server implementation with full feature set
- `c2_server_gui.py` - Graphical user interface for easier server management
- `c2_agent.py` - Lightweight client agent for deployment on target systems
- `crypto_utils.py` - Cryptographic utilities for secure communication protocols
- `requirements.txt` - Python package dependencies

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/Bajinder17/c2-server.git
cd c2-server
pip install -r requirements.txt
```

### Usage
```bash
# Start the CLI server
python c2_server.py

# Start the GUI server  
python c2_server_gui.py

# Connect an agent
python c2_agent.py [server_ip] [server_port]
```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick contribution steps:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

### Tech Stack
- **Language**: Python 3.8+
- **GUI**: Tkinter
- **Networking**: Socket programming, threading
- **Security**: Custom encryption utilities

## 📞 Communication

- **Project Maintainer**: [Bajinder17](https://github.com/Bajinder17)
- **Issues**: Please use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions and ideas

## 🎃 Hacktoberfest Rules

This repository participates in **Hacktoberfest 2025**! To ensure quality contributions:

### Valid Contributions Include:
- ✅ Bug fixes with proper testing
- ✅ New features that enhance functionality
- ✅ Documentation improvements
- ✅ Code optimization and refactoring
- ✅ Security enhancements
- ✅ UI/UX improvements

### Invalid Contributions:
- ❌ Spam pull requests
- ❌ Minor text changes without value
- ❌ Duplicate contributions
- ❌ AI-generated content without review
- ❌ Breaking changes without discussion

### Quality Standards:
- All PRs must pass code review
- Include clear description of changes
- Test your code before submitting
- Follow existing code style and conventions
- Reference related issues when applicable

## 👥 Maintainers

- **@Bajinder17** - Project Owner & Lead Developer
  - Reviews all pull requests
  - Manages project roadmap and releases
  - Final decision on feature implementations

### PR Review Process:
1. **Automated Checks**: Code style and basic functionality
2. **Maintainer Review**: Code quality and project alignment  
3. **Testing**: Manual testing of new features
4. **Merge**: Integration into main branch

## ⚠️ Important Security Notice

This project is designed for **educational purposes** and **legitimate system administration** only. 

**Please ensure:**
- Always obtain proper authorization before deploying on any systems
- Use only in controlled environments or systems you own
- Comply with all applicable laws and regulations
- Implement proper security measures in production environments

## 🌟 Show Your Support

If you found this project helpful, please consider:
- ⭐ Starring this repository
- 🍴 Forking and contributing
- 📢 Sharing with others interested in network programming
- 🐛 Reporting bugs and suggesting improvements

---

**Happy Coding! 🚀**
