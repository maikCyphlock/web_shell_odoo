/** @odoo-module **/
/*
    Part of Web Shell. See LICENSE file for full copyright and licensing details.
    Created by MAIKOL AGUILAR (https://github.com/maikol-aguilar)
*/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, useRef, onMounted, onWillDestroy, onWillUnmount, markup } from "@odoo/owl";
import { highlightPython } from "./highlighter";

export class WebShellConsole extends Component {
    static template = "web_shell.Console";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.busService = useService("bus_service");
        this.notification = useService("notification");

        this.outputRef = useRef("outputRef");
        this.logRef = useRef("logRef");
        this.editorRef = useRef("editorRef");
        this.editor = null;

        this.state = useState({
            input: "",
            history: [],
            logs: [],
            commandHistory: [],
            historyIndex: -1,
        });

        onWillStart(() => {
            this.busService.addChannel("web_shell_logs");
        });

        onMounted(() => {
            this.busService.addEventListener("notification", this.onNotification.bind(this));
            this.initializeAceEditor();
        });

        onWillUnmount(() => {
            if (this.editor) {
                this.editor.destroy();
                this.editor = null;
            }
        });

        onWillDestroy(() => {
            if (this.busService) {
                this.busService.removeEventListener("notification", this.onNotification.bind(this));
            }
        });
    }

    initializeAceEditor() {
        if (!window.ace) {
            console.error("Ace Editor not loaded");
            return;
        }

        // Initialize Ace
        this.editor = window.ace.edit(this.editorRef.el);

        // Configure editor
        this.editor.setTheme("ace/theme/monokai");
        this.editor.session.setMode("ace/mode/python");
        this.editor.setOptions({
            fontSize: "14px",
            showPrintMargin: false,
            highlightActiveLine: true,
            tabSize: 4,
            useSoftTabs: true,
        });

        // Set initial value
        this.editor.setValue(this.state.input, -1); // -1 moves cursor to start

        // Bind change event
        this.editor.session.on('change', () => {
            this.state.input = this.editor.getValue();
        });

        // Add custom keyboard shortcuts
        this.editor.commands.addCommand({
            name: 'execute',
            bindKey: { win: 'Ctrl-Enter', mac: 'Cmd-Enter' },
            exec: () => {
                this.executeCommand();
            }
        });

        this.editor.commands.addCommand({
            name: 'historyUp',
            bindKey: { win: 'Ctrl-Up', mac: 'Cmd-Up' },
            exec: () => {
                this.navigateHistory('up');
            }
        });

        this.editor.commands.addCommand({
            name: 'historyDown',
            bindKey: { win: 'Ctrl-Down', mac: 'Cmd-Down' },
            exec: () => {
                this.navigateHistory('down');
            }
        });

        // Focus the editor
        this.editor.focus();
    }

    onNotification({ detail: notifications }) {
        for (const { payload, type } of notifications) {
            if (type === "log_message") {
                this.state.logs.push(payload);
                if (this.state.logs.length > 500) {
                    this.state.logs.shift();
                }
                this.scrollToBottom(this.logRef);
            }
        }
    }

    navigateHistory(direction) {
        if (this.state.commandHistory.length === 0) return;

        if (direction === 'up') {
            if (this.state.historyIndex < this.state.commandHistory.length - 1) {
                this.state.historyIndex++;
            }
        } else {
            if (this.state.historyIndex > -1) {
                this.state.historyIndex--;
            }
        }

        let newVal = "";
        if (this.state.historyIndex === -1) {
            newVal = "";
        } else {
            const idx = this.state.commandHistory.length - 1 - this.state.historyIndex;
            if (idx >= 0 && idx < this.state.commandHistory.length) {
                newVal = this.state.commandHistory[idx];
            }
        }

        if (this.editor) {
            this.editor.setValue(newVal, -1);
        }
        this.state.input = newVal;
    }

    async executeCommand() {
        const cmd = this.state.input;
        if (!cmd || !cmd.trim()) return;

        // Highlight the input code for history display
        const highlighted = markup(highlightPython(cmd));

        // Add to UI history
        this.state.history.push({ type: 'input', text: cmd, highlighted: highlighted });

        // Add to Command history
        this.state.commandHistory.push(cmd);
        this.state.historyIndex = -1;

        // Clear input
        this.state.input = "";
        if (this.editor) {
            this.editor.setValue("", -1);
        }

        try {
            const result = await this.orm.call("web.shell.console", "execute_command", [cmd]);
            if (result) {
                this.state.history.push({ type: 'output', text: result });
            }
        } catch (error) {
            let errMsg = error.data?.message || error.message || String(error);
            this.state.history.push({ type: 'error', text: errMsg });
        }

        this.scrollToBottom(this.outputRef);

        // Refocus editor
        if (this.editor) {
            this.editor.focus();
        }
    }

    scrollToBottom(ref) {
        setTimeout(() => {
            if (ref.el) {
                ref.el.scrollTop = ref.el.scrollHeight;
            }
        }, 50);
    }

    clearLogs() {
        this.state.logs = [];
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

registry.category("actions").add("web_shell.main", WebShellConsole);
