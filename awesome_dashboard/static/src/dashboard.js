/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";

import { Layout } from "@web/search/layout";
import { DashboardItem } from "./dashboardItem";
import { PieChart } from "./graphs/pie_chart";

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";

    static components = {
        Layout,
        DashboardItem,
        PieChart,
    };

    setup() {
        this.action = useService("action");
        this.statics = useService("statistics");

        onWillStart(async () => {
            const result = await this.statics.getStatistics();

            this.items = result;
            console.log(this.items);
        });
    }

    openCustomerView() {
        this.action.doAction("base.action_partner_form");
    }

    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "All leads",
            res_model: "crm.lead",
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
