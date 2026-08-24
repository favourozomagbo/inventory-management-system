const canvas = document.getElementById("salesChart");

if (canvas && typeof chartProducts !== "undefined") {

    const labels = [];
    const sales = [];

    chartProducts.forEach(product => {

        labels.push(product.name);

        sales.push(product.total_sold);

    });

    new Chart(canvas, {

        type: "bar",

        data: {

            labels: labels,

            datasets: [

                {

                    label: "Units Sold",

                    data: sales,

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            scales: {

                y: {

                    beginAtZero: true

                }

            }

        }

    });

}