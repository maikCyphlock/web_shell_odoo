/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class EnvExplorer extends Component {
    static template = "web_shell.EnvExplorer";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            data: null,
            loading: true,
            error: null,
        });

        onMounted(() => {
            this.loadEnvInfo();
        });
    }

    async loadEnvInfo() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const result = await this.orm.call("web.shell.console", "get_environment_info_rpc", []);
            this.state.data = result;
        } catch (e) {
            this.state.error = e.message || "Error loading environment info";
        } finally {
            this.state.loading = false;
        }
    }

    formatContext() {
        if (!this.state.data || !this.state.data.context) {
            return "{}";
        }
        return JSON.stringify(this.state.data.context, null, 2);
    }
}
