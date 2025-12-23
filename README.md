# Web Shell Odoo

Frontend Python Shell & Log Viewer for Odoo.

Provides a powerful terminal interface to execute Python code and view logs in real-time directly from the Odoo web client.

## 🚀 Features

-   **Floating Python Console**: Execute Python code with direct access to the Odoo environment (`env`, `request`, etc.).
-   **Real-time Log Viewer**: Monitor Odoo server logs directly from the browser.
-   **Ace Editor Integration**: Syntax highlighting and a professional code editing experience.
-   **Minimalist UI**: Modern, flat design that integrates seamlessly with the Odoo backend.

## 🛠️ Technologies

-   **Backend**: Python, Odoo Framework.
-   **Frontend**: JavaScript (OWL - Odoo Web Library).
-   **Editor**: [Ace Editor](https://ace.c9.io/) via CDN.

## 📦 Installation

1.  Copy the `web_shell` directory into your Odoo `addons` path.
2.  Restart the Odoo server.
3.  Activate developer mode in Odoo.
4.  Go to **Apps** -> **Update Apps List**.
5.  Search for "Web Shell" and click **Install**.

## 📖 Usage

### Python Console
Once installed, you can access the Web Shell from the debug menu or via the dedicated console view. It allows you to run Python snippets against the current Odoo database.

### Log Viewer
The log viewer automatically finds and streams Odoo logs (supporting standard paths and Docker stdout). Access it via the dashboard to monitor system activity in real-time.

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
   - `web_shell.timeout`: Set to number of seconds (e.g., `60`)
   - `web_shell.blocked_patterns`: Comma-separated list (e.g., `os.system,subprocess`)

## 👤 Author

**MAIKOL AGUILAR**
-   GitHub: [@maikCyphlock](https://github.com/maikCyphlock)

## 📄 License

This project is licensed under the OPL-1 License - see the [LICENSE](web_shell/LICENSE) file for details.
