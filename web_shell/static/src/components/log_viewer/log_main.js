/** @odoo-module **/
/*
    Part of Web Shell. See LICENSE file for full copyright and licensing details.
    Created by MAIKOL AGUILAR (https://github.com/maikCyphlock)
*/
import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { LogPanel } from "./log_panel";

export class WebClientRoot extends Component {
    static template = "web_shell.WebClientRoot";
    static components = { LogPanel };
}

// Register as a main component in the web client
registry.category("main_components").add("web_shell.LogPanel", {
    Component: LogPanel,
});
