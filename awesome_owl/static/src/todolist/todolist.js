import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { TodoItem } from "../todoitem/todoitem.js";

export class TodoList extends Component {
    static template = "awesome_owl.todolist";
    static components = { TodoItem };

    setup() {
        this.myRef = useRef("myInput");
        onMounted(() => {
            this.myRef.el.focus();
        });
    }

    todos = useState([]);

    addTodo(event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            const description = event.target.value;
            event.target.value = ""; // Clear the input field
            if (description === "") {
                return; // Do not add empty todos
            }
            const newTodo = {
                id: this.todos.length + 1,
                description: `Todo ${description}`,
                completed: false,
            };
            this.todos.push(newTodo);
        }
    }

    toggleState(id) {
        const todo = this.todos.find((todo) => todo.id === id);
        if (todo) {
            todo.completed = !todo.completed;
        }
    }

    deleteItem(elemId) {
        const index = this.todos.findIndex((elem) => elem.id === elemId);
        if (index >= 0) {
            // remove the element at index from list
            this.todos.splice(index, 1);
        }
    }
}
