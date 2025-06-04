import { Component } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.todoitem";

    static props = {
        item: { type: Object, optional: false },
        toggleState: { type: Function, optional: false },
        deleteItem: { type: Function, optional: false },
    };

    changeState() {
        this.props.toggleState(this.props.item.id);
    }

    deleteItem() {
        this.props.deleteItem(this.props.item.id);
    }
}
