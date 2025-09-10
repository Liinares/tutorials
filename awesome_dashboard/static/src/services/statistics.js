import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { memoize } from "@web/core/utils/functions";

const getStatistics = memoize(async () => {
    const result = await rpc("/awesome_dashboard/statistics");
    return result;
});

export const statistics = {
    start(env) {
        return { getStatistics };
    },
};

registry.category("services").add("statistics", statistics);
