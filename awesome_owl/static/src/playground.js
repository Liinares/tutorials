/** @odoo-module **/

import { Component, useState, markup } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todolist/todolist";

export class Playground extends Component {
    static template = "awesome_owl.playground";

    string1 = "<div class='text-primary'>This is a string</div>";
    string2 = markup("<div class='text-danger'>This is another string</div>");

    sum = useState({ value: 0 });

    static components = { Counter, Card, TodoList };

    incrementSum() {
        this.sum.value += 1;
    }
}
