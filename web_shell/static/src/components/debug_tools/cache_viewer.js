/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

export class CacheViewer extends Component {
    setup() {
        this.state = useState({
            model: this.props.initialModel || 'res.partner',
            recordId: this.props.initialRecordId || 1,
            fields: [],
            loading: false,
            error: null,
            searched: false,
            history: [], // Stack of {model, recordId}
        });

        this.orm = useService("orm");

        if (this.props.initialRecordId) {
            this.inspectCache();
        }
    }

    async inspectCache(resetHistory = true) {
        if (!this.state.model || !this.state.recordId) {
            this.state.error = "Please provide Model and Record ID";
            return;
        }

        this.state.loading = true;
        this.state.error = null;
        this.state.searched = true;
        if (resetHistory) {
            this.state.history = [{ model: this.state.model, recordId: this.state.recordId }];
        }

        this.state.fields = [];

        try {
            const result = await this.orm.call("web.shell.console", "get_cache_info_rpc", [], {
                model: this.state.model,
                record_id: Number(this.state.recordId)
            });

            console.log("WebShell: Cache Info Result", result);

            if (result.error) {
                this.state.error = result.error;
            } else {
                this.state.fields = result.fields || [];
            }
        } catch (e) {
            this.state.error = "Error fetching cache info: " + e.message;
        } finally {
            this.state.loading = false;
        }
    }

    async navigateToRelation(model, id) {
        this.state.model = model;
        this.state.recordId = id;
        this.state.history.push({ model, recordId: id });
        await this.inspectCache(false);
    }

    async goBack() {
        if (this.state.history.length > 1) {
            this.state.history.pop();
            const prev = this.state.history[this.state.history.length - 1];
            this.state.model = prev.model;
            this.state.recordId = prev.recordId;
            await this.inspectCache(false);
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            this.inspectCache();
        }
    }
}

CacheViewer.template = "web_shell.CacheViewer";
