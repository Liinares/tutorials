import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { memoize } from "@web/core/utils/functions";
import { reactive } from "@odoo/owl";

export const statistics = {
    start(env) {
        let statistics = reactive({});

        const loadData = async () => {
            let data = await rpc("/awesome_dashboard/statistics");
            Object.assign(statistics, data);
        };

        setInterval(loadData, 3000);
        loadData();

        return statistics;
    },
};

registry.category("services").add("statistics", statistics);
