/** @odoo-module **/
/*
    Part of Web Shell. See LICENSE file for full copyright and licensing details.
    Created by MAIKOL AGUILAR (https://github.com/maikol-aguilar)
*/

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LogPanel extends Component {
    static template = "web_shell.LogPanel";
    static props = ["*"];

    setup() {
        this.panelRef = useRef("panelRef");
        this.orm = useService("orm");

        this.state = useState({
            visible: false,
            logs: [],
            position: this.loadPosition(),
            dragging: false,
            recording: true,
            error: null,
        });

        this.dragStart = { x: 0, y: 0 };
        this.onWindowMouseUp = this.onDragEnd.bind(this);
        this.onWindowMouseMove = this.onDragMove.bind(this);
        this.lastPosition = 0;
        this.pollInterval = null;

        onMounted(() => {
            window.addEventListener('toggle_log_panel', this.togglePanel.bind(this));
            // Start polling when mounted
            this.startPolling();
        });

        onWillUnmount(() => {
            window.removeEventListener('toggle_log_panel', this.togglePanel.bind(this));
            this.stopPolling();
            this.cleanupDragListeners();
        });
    }

    startPolling() {
        if (this.pollInterval) return;
        this.pollInterval = setInterval(() => this.fetchLogs(), 2000);
        // Fetch immediately
        this.fetchLogs();
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async fetchLogs() {
        if (!this.state.recording) return;

        try {
            const result = await this.orm.call("web.shell.console", "read_logs", [], {
                last_position: this.lastPosition,
                max_lines: 100
            });

            if (result.error) {
                this.state.error = result.error;
                return;
            }

            this.state.error = null;

            if (result.lines && result.lines.length > 0) {
                // Append new logs
                for (const log of result.lines) {
                    this.state.logs.push(log);
                }
                // Limit total logs
                while (this.state.logs.length > 500) {
                    this.state.logs.shift();
                }
                this.lastPosition = result.position;

                if (this.state.visible) {
                    this.scrollToBottom();
                }
            }
        } catch (e) {
            console.error('Log fetch error:', e);
            this.state.error = e.message || 'Connection error';
        }
    }

    loadPosition() {
        const saved = localStorage.getItem('web_shell_log_panel_position');
        if (saved) {
            return JSON.parse(saved);
        }
        return { top: 100, right: 20 };
    }

    savePosition() {
        localStorage.setItem('web_shell_log_panel_position', JSON.stringify(this.state.position));
    }

    togglePanel() {
        this.state.visible = !this.state.visible;
    }

    closePanel() {
        this.state.visible = false;
    }

    toggleRecording() {
        this.state.recording = !this.state.recording;
    }

    clearLogs() {
        this.state.logs = [];
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            const panel = this.panelRef.el;
            if (panel) {
                const logContent = panel.querySelector('.o_log_panel_content');
                if (logContent) {
                    logContent.scrollTop = logContent.scrollHeight;
                }
            }
        });
    }

    // Dragging Logic
    onDragStart(ev) {
        if (ev.target.closest('button')) return;

        this.state.dragging = true;
        this.dragStart.x = ev.clientX;
        this.dragStart.y = ev.clientY;
        this.initialRight = this.state.position.right;
        this.initialTop = this.state.position.top;

        window.addEventListener('mousemove', this.onWindowMouseMove);
        window.addEventListener('mouseup', this.onWindowMouseUp);
        ev.preventDefault();
    }

    onDragMove(ev) {
        if (!this.state.dragging) return;

        const dx = this.dragStart.x - ev.clientX;
        const dy = ev.clientY - this.dragStart.y;

        let newRight = this.initialRight + dx;
        let newTop = this.initialTop + dy;

        newRight = Math.max(0, Math.min(newRight, window.innerWidth - 300));
        newTop = Math.max(0, Math.min(newTop, window.innerHeight - 50));

        this.state.position.right = newRight;
        this.state.position.top = newTop;
    }

    onDragEnd() {
        this.state.dragging = false;
        this.cleanupDragListeners();
        this.savePosition();
    }

    cleanupDragListeners() {
        window.removeEventListener('mousemove', this.onWindowMouseMove);
        window.removeEventListener('mouseup', this.onWindowMouseUp);
    }

    getLogLevelClass(level) {
        switch (level) {
            case 'INFO': return 'text-info';
            case 'WARNING': return 'text-warning';
            case 'ERROR': return 'text-danger';
            case 'CRITICAL': return 'text-danger fw-bolder';
            case 'DEBUG': return 'text-muted';
            default: return 'text-white';
        }
    }
}
