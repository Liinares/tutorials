import { Component, onMounted, onWillStart, useRef, onWillUnmount } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";

    setup() {
        // This will reference the <canvas> element in the template
        this.canvasRef = useRef("canvas");

        // This will hold the Chart.js instance
        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));

        // This will run after the component is mounted in the DOM. This is necessary
        // because Chart.js needs the canvas to be in the DOM to render properly.
        onMounted(() => {
            this.renderChart();
        });

        // Clean up the chart instance when the component is unmounted
        onWillUnmount(() => {
            this.chart.destroy();
        });
    }

    renderChart() {
        const labels = Object.keys(this.props.data);
        const data = Object.values(this.props.data);

        this.chart = new Chart(this.canvasRef.el, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [
                    {
                        data: data,
                    },
                ],
            },
        });
    }
}
