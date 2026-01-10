# Web Shell Odoo

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/maikCyphlock/web_shell_odoo/releases/tag/v1.2.0)
[![License](https://img.shields.io/badge/license-LGPL--3-green.svg)](https://github.com/maikCyphlock/web_shell_odoo/blob/main/web_shell/LICENSE)

Frontend Python Shell & Real-time Log Viewer for Odoo.

Provides a powerful terminal interface to execute Python code with full Odoo environment access and monitor server logs in real-time directly from the Odoo web client.

## 🚀 Features

### Python Console
-   **Floating Python Console**: Execute Python code with direct access to the Odoo environment (`env`, `request`, `self`, etc.).
-   **Ace Editor Integration**: Syntax highlighting, auto-completion, and professional code editing experience.
-   **Command History**: Navigate previous commands with up/down arrows.
-   **Auto-completion**: Suggestions for common Odoo objects and methods.
-   **Syntax Highlighting**: Enhanced output formatting for better readability.

### Log Viewer
-   **Real-time Log Streaming**: Monitor Odoo server logs directly from the browser with live updates.
-   **Multiple Log Sources**: Supports standard Odoo log paths and Docker stdout.
-   **Optimized Polling**: Only polls when the panel is visible to reduce server load.
-   **Noise Reduction**: Automatically filters out polling-related log messages.
-   **Resizable Panel**: Adjustable width with persistent settings.
-   **Draggable Interface**: Move the panel anywhere on screen.
-   **Log Level Coloring**: Visual distinction for INFO, WARNING, ERROR, etc.

### Additional Features
-   **Session Management**: Automatic cleanup of inactive sessions and memory limits.
-   **Audit Logging**: All executed commands are logged for security tracking.
-   **Configurable Timeouts**: Prevent long-running commands with customizable limits.
-   **Blocked Patterns**: Security layer to prevent dangerous operations.
-   **Minimalist UI**: Modern, flat design that integrates seamlessly with the Odoo backend.

## 🛠️ Technologies

-   **Backend**: Python, Odoo Framework (compatible with Odoo 14+).
-   **Frontend**: JavaScript (OWL - Odoo Web Library), SCSS.
-   **Editor**: [Ace Editor](https://ace.c9.io/) via CDN for optimal performance.

## 📦 Installation

### Requirements
- Odoo 14.0 or higher
- Administrator access to install modules

### Steps
1.  Download or clone this repository.
2.  Copy the `web_shell` directory into your Odoo `addons` path.
3.  Restart the Odoo server:
    ```bash
    sudo systemctl restart odoo
    ```
4.  Activate developer mode in Odoo (go to Settings → Activate Developer Mode).
5.  Go to **Apps** → **Update Apps List**.
6.  Search for "Web Shell" and click **Install**.
7.  (Optional) Configure security parameters as described in the Security section.

### Docker Installation
If using Docker, mount the module directory and rebuild the container:
```bash
docker-compose up --build
```

## 📖 Usage

### Accessing Web Shell
After installation, access the Web Shell through:
- **Debug Menu**: In any Odoo view, click the bug icon (🪳) → "Web Shell"
- **Systray**: Click the terminal icon in the top-right corner
- **Direct URL**: Navigate to `/web_shell/console`

### Python Console
The Python console provides a full Odoo environment for executing code:

```python
# Example: Get user count
users = env['res.users'].search([])
print(f"Total users: {len(users)}")

# Example: Create a partner
partner = env['res.partner'].create({
    'name': 'Test Partner',
    'email': 'test@example.com'
})
print(f"Created partner: {partner.id}")
```

**Available globals**: `env`, `request`, `self` (current user), `odoo`

**Tips**:
- Use `Ctrl+Enter` or `Shift+Enter` to execute code
- Commands are audited and have timeout limits
- Dangerous operations are blocked by default

### Log Viewer
The log viewer streams real-time logs from Odoo:

1. **Open Log Panel**: Click the log icon in the systray or use the debug menu
2. **Auto-detection**: Automatically finds logs from standard paths:
   - `/var/log/odoo/odoo-server.log`
   - `/var/log/odoo/odoo.log`
   - Docker stdout (`/proc/1/fd/1`)
3. **Features**:
   - **Resize**: Drag the left edge to adjust width
   - **Move**: Drag the header to reposition
   - **Filter**: Only shows relevant logs (polling noise filtered)
   - **Recording**: Toggle live updates on/off
   - **Clear**: Remove all displayed logs

**Log Levels**: Color-coded for easy identification (INFO=blue, WARNING=orange, ERROR=red)

## ⚠️ Security

> **WARNING**: This module allows arbitrary Python code execution. **ONLY use in development environments. NEVER install in production.**

### Security Features

| Feature | Description | Configuration |
|---------|-------------|---------------|
| **Audit Logging** | All executed commands are logged | Automatic (check Odoo logs for `WEB_SHELL AUDIT`) |
| **Timeout** | Commands have a maximum execution time | `ir.config_parameter` → `web_shell.timeout` (default: 30s) |
| **Blocked Patterns** | Dangerous commands are blocked | `ir.config_parameter` → `web_shell.blocked_patterns` |

### Default Blocked Patterns
```
os.system, os.popen, subprocess, shutil.rmtree, __import__
```

### Configuring Parameters
1. Go to **Settings** → **Technical** → **System Parameters**
2. Create/edit the parameter:
    - `web_shell.timeout`: Maximum execution time in seconds (default: `30`)
    - `web_shell.blocked_patterns`: Comma-separated list of blocked patterns (default: `os.system,os.popen,subprocess,shutil.rmtree,__import__`)

### Access Control
Only users with **Administration / Settings** group can access Web Shell. To grant access:
1. Go to **Settings** → **Users & Companies** → **Users**
2. Select the user → **Access Rights** tab
3. Check **Administration / Settings**

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Update CHANGELOG.md if adding features
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/maikCyphlock/web_shell_odoo.git
cd web_shell_odoo
# Install in your Odoo development environment
```

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## 🐛 Troubleshooting

### Common Issues
- **Module not appearing**: Ensure developer mode is activated and apps list is updated
- **Permission denied**: Check user has Administration/Settings access
- **Logs not showing**: Verify log file paths exist and are readable
- **Timeout errors**: Increase `web_shell.timeout` parameter

### Support
- Open an issue on [GitHub](https://github.com/maikCyphlock/web_shell_odoo/issues)
- Check the [CHANGELOG](CHANGELOG.md) for recent fixes

## 👤 Author

**MAIKOL AGUILAR**
-   GitHub: [@maikCyphlock](https://github.com/maikCyphlock)
-   Email: Contact via GitHub

## 📄 License

This project is licensed under the LGPL-3 License - see the [LICENSE](web_shell/LICENSE) file for details.

## 🙏 Acknowledgments

- Odoo Community for the excellent framework
- Ace Editor for the code editing component
- All contributors and users
