# Changelog

All notable changes to Web Shell Odoo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ORM Profiler for analyzing query performance
- Environment Explorer for navigating Odoo data structures
- Cache Viewer for inspecting and debugging Odoo cache
- Model Graph Viewer for visualizing model relationships
- View Graph Viewer for visualizing view architecture
- Real-time log streaming from Docker stdout
- Syntax highlighting for Python console output
- Command history with up/down arrow navigation
- Auto-completion suggestions for common Odoo objects
- **Session management improvements** - Automatic cleanup of inactive sessions and memory limits
- **API endpoint for session cleanup** (`/web_shell/session/cleanup`) for manual session management
- **Frontend memory management** - Configurable limits for logs, history, and command history
- **Session metadata tracking** - Track last activity time for each user session

### Changed
- Improved Ace Editor integration via CDN for better performance
- Enhanced UI with modern flat design
- Refactored log viewer to support multiple log sources
- Updated dependency requirements for Odoo 14+
- Optimized log viewer polling to only run when panel is visible, reducing server load
- Added filtering of polling-related log messages in the log viewer to reduce noise
- Prevented server-side logging of log polling requests by setting nolog flag
- Added resizable width functionality to the log panel with persistent storage

### Fixed
- Fixed console output encoding issues with special characters
- Resolved timeout not being respected for long-running commands
- Fixed log viewer not updating when log files are rotated
- Corrected access control for non-admin users
- **Fixed memory leaks in session management** - Added automatic cleanup of inactive sessions after 1 hour
- **Fixed memory leaks in frontend logs** - Enforced limits on log history (max 300 entries)
- **Fixed memory leaks in command history** - Added limits on UI history (max 200) and command history (max 100)
- **Fixed session accumulation** - Added session cleanup on component unmount and API endpoint for manual cleanup

### Security
- Added audit logging for all executed commands with `WEB_SHELL AUDIT` prefix
- Added configurable timeout via `web_shell.timeout` parameter (default: 30s)
- Added configurable blocked patterns via `web_shell.blocked_patterns` parameter
- Restricted shell access to users with 'Administration / Settings' group only
- Enhanced input validation to prevent code injection attacks

## [1.1.0] - 2025-01-XX

### Added
- Initial release of Web Shell Odoo
- Floating Python Console with full Odoo environment access
- Real-time Log Viewer supporting standard Odoo log paths
- Ace Editor integration for syntax highlighting
- Minimalist UI that integrates with Odoo backend
- Security features: audit logging, timeout, and blocked patterns

### Security
- Default blocked patterns: `os.system, os.popen, subprocess, shutil.rmtree, __import__`
- Automatic audit logging of all executed commands
- 30-second default timeout for command execution
### Documentation
- Complete README with installation and usage instructions
- Security warning for production environments

[Unreleased]: https://github.com/maikCyphlock/web_shell_odoo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/maikCyphlock/web_shell_odoo/releases/tag/v1.1.0
