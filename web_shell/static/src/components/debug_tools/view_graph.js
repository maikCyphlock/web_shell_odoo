/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ViewGraph extends Component {
    static template = "web_shell.ViewGraph";
    static props = {
        initialViewId: { type: [Number, { value: null }], optional: true },
    };

    setup() {
        this.state = useState({
            root: null,
            loading: false,
            error: null,
            mode: 'search', // 'search' or 'tree'
            searchQuery: '',
            searchResults: [],
            selectedView: null,
            selectedNode: null,
            diff: null,
            diffLoading: false,
            showDiffModal: false,
            collapsedNodes: {}, // Track collapsed nodes by ID
        });

        this.orm = useService("orm");
        this.searchInputRef = useRef("searchInput");

        onMounted(() => {
            if (this.props.initialViewId) {
                this.loadGraph(this.props.initialViewId);
            } else {
                if (this.searchInputRef.el) {
                    this.searchInputRef.el.focus();
                }
            }
        });
    }

    async onSearchKeydown(ev) {
        if (ev.key === "Enter") {
            await this.searchViews();
        }
    }

    async searchViews() {
        const query = this.state.searchQuery.trim();
        if (!query) return;

        this.state.loading = true;
        this.state.error = null;
        this.state.searchResults = [];

        try {
            const results = await this.orm.call(
                "web.shell.console",
                "search_views_rpc",
                [query]
            );
            this.state.searchResults = results;
        } catch (e) {
            this.state.error = e.message || "Error searching views";
        } finally {
            this.state.loading = false;
        }
    }

    async selectView(view) {
        this.state.selectedView = view;
        await this.loadGraph(view.id);
    }

    async loadGraph(viewId) {
        this.state.loading = true;
        this.state.error = null;
        this.state.mode = 'tree';
        this.state.selectedNode = null;
        this.state.diff = null;
        this.state.showDiffModal = false;

        try {
            const data = await this.orm.call(
                "web.shell.console",
                "get_view_inheritance_rpc",
                [viewId]
            );
            this.state.root = data;
        } catch (e) {
            this.state.error = e.message || "Error loading graph";
            this.state.mode = 'search';
        } finally {
            this.state.loading = false;
        }
    }

    async loadDiff(viewId) {
        this.state.diffLoading = true;
        this.state.diff = null;

        try {
            const diffLines = await this.orm.call(
                "web.shell.console",
                "get_view_diff_rpc",
                [viewId]
            );
            this.state.diff = diffLines;
        } catch (e) {
            this.state.diff = ["Error loading diff: " + e.message];
        } finally {
            this.state.diffLoading = false;
        }
    }

    backToSearch() {
        this.state.mode = 'search';
        this.state.root = null;
        this.state.selectedView = null;
        this.state.selectedNode = null;
        this.state.diff = null;
        this.state.showDiffModal = false;
    }

    onNodeClick(node) {
        this.state.selectedNode = node;
        this.state.showDiffModal = true;
        this.loadDiff(node.id);
    }

    closeDiffModal() {
        this.state.showDiffModal = false;
        this.state.selectedNode = null;
        this.state.diff = null;
    }

    toggleNode(nodeId, ev) {
        ev.stopPropagation();
        this.state.collapsedNodes[nodeId] = !this.state.collapsedNodes[nodeId];
    }

    isNodeCollapsed(nodeId) {
        return !!this.state.collapsedNodes[nodeId];
    }
}
