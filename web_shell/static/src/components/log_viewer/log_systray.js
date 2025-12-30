/** @odoo-module **/
/*
    Part of Web Shell. See LICENSE file for full copyright and licensing details.
    Created by MAIKOL AGUILAR (https://github.com/maikCyphlock)
*/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LogViewerSystray extends Component {
    static template = "web_shell.LogViewerSystray";
    static props = ["*"];

    setup() {
        this.action = useService("action");
    }

    onClick() {
        // Dispatch custom event to toggle the floating panel
        window.dispatchEvent(new CustomEvent('toggle_log_panel'));
    }
}

export const systrayItem = {
    Component: LogViewerSystray,
    isDisplayed: (env) => {
        // Only show in debug mode
        return Boolean(odoo.debug);
    },
};

registry.category("systray").add("web_shell.log_viewer", systrayItem, { sequence: 100 });
