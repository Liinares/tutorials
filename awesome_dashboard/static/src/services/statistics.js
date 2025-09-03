import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const statistics = {
  dependencies: [],
  start(env, {  }) {
    
  },
};

registry.category("services").add("statistics", statistics);

