/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ModelGraph extends Component {
    static template = "web_shell.ModelGraph";

    setup() {
        this.state = useState({
            loading: false,
            error: null,
            searchQuery: '',
            searchResults: [],
            activeModel: null, // Current central model info
            history: [],       // History of navigated models
        });

        this.orm = useService("orm");
        this.searchInputRef = useRef("searchInput");

        onMounted(() => {
            if (this.searchInputRef.el) {
                this.searchInputRef.el.focus();
            }
        });
    }

    async onSearchKeydown(ev) {
        if (ev.key === "Enter") {
            await this.searchModels();
        }
    }

    async searchModels() {
        const query = this.state.searchQuery.trim().toLowerCase();
        if (!query) return;

        this.state.loading = true;
        this.state.error = null;

        try {
            // Internal Odoo search for models
            const results = await this.orm.searchRead(
                "ir.model",
                [["model", "ilike", query]],
                ["model", "name"]
            );
            this.state.searchResults = results;
        } catch (e) {
            this.state.error = e.message || "Error searching models";
        } finally {
            this.state.loading = false;
        }
    }

    async selectModel(modelName) {
        this.state.loading = true;
        this.state.error = null;

        try {
            const data = await this.orm.call(
                "web.shell.console",
                "get_model_relations_rpc",
                [modelName]
            );

            if (data.error) {
                this.state.error = data.error;
            } else {
                if (this.state.activeModel) {
                    this.state.history.push(this.state.activeModel.model);
                }
                this.state.activeModel = data;
                this.state.searchResults = [];
                this.state.searchQuery = '';
            }
        } catch (e) {
            this.state.error = e.message || "Error loading model relations";
        } finally {
            this.state.loading = false;
        }
    }

    goBack() {
        if (this.state.history.length > 0) {
            const prevModel = this.state.history.pop();
            // We need to reload to avoid recursive history push in selectModel
            this.loadModelWithoutHistory(prevModel);
        } else {
            this.state.activeModel = null;
        }
    }

    async loadModelWithoutHistory(modelName) {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "web.shell.console",
                "get_model_relations_rpc",
                [modelName]
            );
            this.state.activeModel = data;
        } finally {
            this.state.loading = false;
        }
    }

    reset() {
        this.state.activeModel = null;
        this.state.history = [];
        this.state.searchResults = [];
    }
}
