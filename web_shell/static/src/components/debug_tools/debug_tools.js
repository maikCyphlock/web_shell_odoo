/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { CacheViewer } from "./cache_viewer";
import { ViewGraph } from "./view_graph";
import { ModelGraph } from "./model_graph";
import { ORMProfiler } from "./orm_profiler";

export class DebugTools extends Component {
    static template = "web_shell.DebugTools";
    static components = { CacheViewer, ViewGraph, ModelGraph, ORMProfiler };

    setup() {
        this.state = useState({
            activeTab: 'inspector', // 'inspector', 'graph', 'models', or 'profiler'
            targetViewId: null,
        });
    }

    switchTab(tab) {
        this.state.activeTab = tab;
    }

    openViewGraph(viewId) {
        this.state.targetViewId = Number(viewId);
        this.state.activeTab = 'graph';
    }
}

DebugTools.props = {
    onClose: { type: Function, optional: true }
};
