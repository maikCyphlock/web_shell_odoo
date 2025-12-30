/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ORMProfiler extends Component {
    static template = "web_shell.ORMProfiler";

    setup() {
        this.state = useState({
            loading: false,
            results: null,
            code: "# Example: Profiling a search and read\nfor p in env['res.partner'].search([], limit=5):\n    print(p.name)",
        });

        this.orm = useService("orm");
        this.editorRef = useRef("editor");
        this.aceEditor = null;

        onMounted(() => {
            this.initEditor();
        });
    }

    initEditor() {
        if (!this.editorRef.el) return;

        this.aceEditor = ace.edit(this.editorRef.el);
        this.aceEditor.setTheme("ace/theme/chrome");
        this.aceEditor.session.setMode("ace/mode/python");
        this.aceEditor.setOptions({
            fontSize: "13px",
            showPrintMargin: false,
            minLines: 10,
            maxLines: 20,
        });
        this.aceEditor.setValue(this.state.code, -1);
    }

    async runProfile() {
        const code = this.aceEditor.getValue();
        this.state.loading = true;
        this.state.results = null;

        try {
            const data = await this.orm.call(
                "web.shell.console",
                "profile_rpc",
                [code]
            );

            // Detect N+1 or duplicates
            if (data.queries) {
                const queryMap = {};
                data.queries.forEach(q => {
                    const normalized = q.sql.replace(/\d+/g, '?');
                    queryMap[normalized] = (queryMap[normalized] || 0) + 1;
                    q.duplicateCount = queryMap[normalized];
                });

                data.alerts = Object.entries(queryMap)
                    .filter(([sql, count]) => count > 1)
                    .map(([sql, count]) => ({
                        type: 'warning',
                        message: `Potential N+1 detected: ${count} similar queries for: ${sql.substring(0, 100)}...`
                    }));
            }

            this.state.results = data;
        } catch (e) {
            this.state.results = { error: e.message || "Error during profiling" };
        } finally {
            this.state.loading = false;
        }
    }

    clear() {
        this.state.results = null;
    }
}
