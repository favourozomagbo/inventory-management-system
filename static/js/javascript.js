
// ===============================
//  Customer Search table
// ===============================

const searchInput = document.getElementById("customerSearch");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        const rows = document.querySelectorAll(".customer-table tbody tr");

        rows.forEach(function (row) {

            row.style.display = row.innerText
                .toLowerCase()
                .includes(value)
                ? ""
                : "none";

        });

    });

}

const flashMessages = document.querySelectorAll(".alert");

flashMessages.forEach(function (message) {
    setTimeout(function () {
        message.style.display = "none";
    }, 3000);
});


// ===============================
//  Product Search
// ===============================
document.addEventListener("DOMContentLoaded", function () {

    const productSearch = document.getElementById("productSearch");
    const productResults = document.getElementById("productResults");
    const productOptions = document.querySelectorAll(".product-option");
    const productIdInput = document.getElementById("product_id");

    if (!productSearch || !productResults || !productIdInput) {
        return;
    }


    // Hide product results when the page first loads
    productResults.style.display = "none";


    // Search products
    productSearch.addEventListener("input", function () {

        const searchValue = this.value.toLowerCase().trim();

        // Clear previously selected product
        productIdInput.value = "";


        // If search is empty, hide results
        if (searchValue === "") {

            productResults.style.display = "none";

            productOptions.forEach(function (option) {
                option.style.display = "none";
            });

            return;
        }


        let foundProduct = false;


        productOptions.forEach(function (option) {

            const productName =
                option.dataset.name.toLowerCase();


            if (productName.includes(searchValue)) {

                option.style.display = "flex";

                foundProduct = true;

            } else {

                option.style.display = "none";

            }

        });


        // Show results only when something matches
        if (foundProduct) {

            productResults.style.display = "block";

        } else {

            productResults.style.display = "none";

        }

    });


    // Select product
    productOptions.forEach(function (option) {

        option.addEventListener("click", function () {

            const productId = this.dataset.id;
            const productName = this.dataset.name;
            const productUnit = this.dataset.unit;


            // Put selected product name in search box
            productSearch.value = productName;


            // Put selected product ID in hidden input
            productIdInput.value = productId;


            // Update the unit display
            const unitDisplay =
                document.getElementById("purchaseUnit") ||
                document.getElementById("salesUnit");


            if (unitDisplay) {
                unitDisplay.textContent =
                    `Unit: ${productUnit}`;
            }


            // Hide product results
            productResults.style.display = "none";

        });

    });

});


    // ===============================
    //  Supplier Search
    // ===============================

const supplierSearch = document.getElementById("supplierSearch");
const supplierResults = document.getElementById("supplierResults");
const supplierOptions = document.querySelectorAll(".supplier-option");
const supplierIdInput = document.getElementById("supplier_id");

if (supplierSearch && supplierResults && supplierIdInput) {

    // Hide supplier results when page loads
    supplierResults.style.display = "none";


    // Search suppliers
    supplierSearch.addEventListener("input", function () {

        const searchValue = this.value.toLowerCase().trim();

        // Clear previously selected supplier
        supplierIdInput.value = "";


        // If search is empty, hide results
        if (searchValue === "") {

            supplierResults.style.display = "none";

            supplierOptions.forEach(function (option) {
                option.style.display = "none";
            });

            return;
        }


        let foundSupplier = false;


        supplierOptions.forEach(function (option) {

            const supplierName =
                option.dataset.name.toLowerCase();


            if (supplierName.includes(searchValue)) {

                option.style.display = "flex";

                foundSupplier = true;

            } else {

                option.style.display = "none";

            }

        });


        // Show results only when something matches
        if (foundSupplier) {

            supplierResults.style.display = "block";

        } else {

            supplierResults.style.display = "none";

        }

    });


    // Select supplier
    supplierOptions.forEach(function (option) {

        option.addEventListener("click", function () {

            const supplierId = this.dataset.id;
            const supplierName = this.dataset.name;


            // Put selected supplier name in search box
            supplierSearch.value = supplierName;


            // Put selected supplier ID in hidden input
            supplierIdInput.value = supplierId;


            // Hide supplier results
            supplierResults.style.display = "none";

        });

    });

}


// ===============================
// Sales - Multiple Products
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const saleItems = document.getElementById("saleItems");
    const addProductButton = document.getElementById("addProduct");
    const grandTotal = document.getElementById("grandTotal");

    if (!saleItems || !addProductButton || !grandTotal) {
        return;
    }


    function setupSalesProduct(item) {

        const searchInput =
            item.querySelector(".productSearch");

        const resultsBox =
            item.querySelector(".productResults");

        const productIdInput =
            item.querySelector(".product_id");

        const quantityInput =
            item.querySelector(".saleQuantity");

        const unitDisplay =
            item.querySelector(".salesUnit");


        // Hide results initially
        resultsBox.hidden = true;


        // Search products
        searchInput.addEventListener("input", function () {

            const searchValue =
                this.value.toLowerCase().trim();

            productIdInput.value = "";


            if (searchValue === "") {

                resultsBox.hidden = true;

                resultsBox
                    .querySelectorAll(".product-option")
                    .forEach(function (option) {
                        option.style.display = "none";
                    });

                calculateGrandTotal();

                return;
            }


            let foundProduct = false;


            resultsBox
                .querySelectorAll(".product-option")
                .forEach(function (option) {

                    const productName =
                        option.dataset.name.toLowerCase();


                    if (productName.includes(searchValue)) {

                        option.style.display = "flex";

                        foundProduct = true;

                    } else {

                        option.style.display = "none";

                    }

                });


            resultsBox.hidden = !foundProduct;

        });


        // Select product
        resultsBox.addEventListener("click", function (event) {

            const option =
                event.target.closest(".product-option");


            if (!option) {
                return;
            }


            searchInput.value =
                option.dataset.name;

            productIdInput.value =
                option.dataset.id;

            unitDisplay.textContent =
                `Unit: ${option.dataset.unit}`;

            quantityInput.max =
                option.dataset.stock;

            quantityInput.value = 1;

            resultsBox.hidden = true;

            calculateGrandTotal();

        });


        // Quantity changes
        quantityInput.addEventListener("input", function () {

            const stock =
                parseInt(quantityInput.max);

            const quantity =
                parseInt(quantityInput.value) || 0;


            if (quantity > stock) {

                quantityInput.setCustomValidity(
                    "Not enough stock available."
                );

            } else {

                quantityInput.setCustomValidity("");

            }


            calculateGrandTotal();

        });

    }


    function calculateGrandTotal() {

        let total = 0;


        const items =
            saleItems.querySelectorAll(".sale-item");


        items.forEach(function (item) {

            const productId =
                item.querySelector(".product_id").value;

            const quantity =
                parseInt(
                    item.querySelector(".saleQuantity").value
                ) || 0;


            if (!productId || quantity <= 0) {
                return;
            }


            const selectedProduct =
                item.querySelector(
                    `.product-option[data-id="${productId}"]`
                );


            if (!selectedProduct) {
                return;
            }


            const price =
                parseFloat(selectedProduct.dataset.price);


            total += price * quantity;

        });


        grandTotal.textContent =
            total.toLocaleString("en-NG", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

    }


    // Add another product
    addProductButton.addEventListener("click", function () {

        const firstItem =
            saleItems.querySelector(".sale-item");


        const newItem =
            firstItem.cloneNode(true);


        newItem.querySelector(".productSearch").value = "";

        newItem.querySelector(".product_id").value = "";

        newItem.querySelector(".saleQuantity").value = "";

        newItem
            .querySelector(".saleQuantity")
            .removeAttribute("max");

        newItem.querySelector(".salesUnit").textContent = "";

        newItem.querySelector(".productResults").hidden = true;


        newItem
            .querySelectorAll(".product-option")
            .forEach(function (option) {

                option.style.display = "none";

            });


        saleItems.appendChild(newItem);

        setupSalesProduct(newItem);

    });


    // Remove product
    saleItems.addEventListener("click", function (event) {

        const removeButton =
            event.target.closest(".remove-item");


        if (!removeButton) {
            return;
        }


        const items =
            saleItems.querySelectorAll(".sale-item");


        if (items.length === 1) {

            alert("At least one product is required.");

            return;

        }


        removeButton
            .closest(".sale-item")
            .remove();


        calculateGrandTotal();

    });


    // Setup first product row
    const firstItem =
        saleItems.querySelector(".sale-item");


    if (firstItem) {
        setupSalesProduct(firstItem);
    }


    // Close product results when clicking outside
    document.addEventListener("click", function (event) {

        if (!event.target.closest(".sale-item")) {

            saleItems
                .querySelectorAll(".productResults")
                .forEach(function (results) {

                    results.hidden = true;

                });

        }

    });

});


// ===============================
//  Customer Search                                
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const customerSearch = document.getElementById("customerSearch");
    const customerResults = document.getElementById("customerResults");
    const customerOptions = document.querySelectorAll(".customer-option");
    const customerIdInput = document.getElementById("customer_id");

    if (!customerSearch || !customerResults || !customerIdInput) {
        return;
    }


    // Hide customer results when the page first loads
    customerResults.style.display = "none";


    // Search customers
    customerSearch.addEventListener("input", function () {

        const searchValue = this.value.toLowerCase().trim();

        // Clear previously selected customer
        customerIdInput.value = "";


        // If search is empty, hide results
        if (searchValue === "") {

            customerResults.style.display = "none";

            customerOptions.forEach(function (option) {
                option.style.display = "none";
            });

            return;
        }


        let foundCustomer = false;


        customerOptions.forEach(function (option) {

            const customerName =
                option.dataset.name.toLowerCase();


            if (customerName.includes(searchValue)) {

                option.style.display = "flex";

                foundCustomer = true;

            } else {

                option.style.display = "none";

            }

        });


        // Show results only when something matches
        if (foundCustomer) {

            customerResults.style.display = "block";

        } else {

            customerResults.style.display = "none";

        }

    });


    // Select customer
    customerOptions.forEach(function (option) {

        option.addEventListener("click", function () {

            const customerId = this.dataset.id;
            const customerName = this.dataset.name;


            // Put selected customer name in search box
            customerSearch.value = customerName;


            // Put selected customer ID in hidden input
            customerIdInput.value = customerId;


            // Hide customer results
            customerResults.style.display = "none";

        });

    });

});


// ========================================
// CONFIRMATION MODAL
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    const confirmationModal =
        document.getElementById("confirmation-modal");

    const confirmationMessage =
        document.getElementById("confirmation-message");

    const confirmationCancel =
        document.getElementById("confirmation-cancel");

    const confirmationOk =
        document.getElementById("confirmation-ok");

    let formToSubmit = null;


    // Make sure the modal exists on this page
    if (
        !confirmationModal ||
        !confirmationMessage ||
        !confirmationCancel ||
        !confirmationOk
    ) {
        return;
    }


    // Find all forms that require confirmation
    const confirmationForms =
        document.querySelectorAll("form[data-confirm]");


    confirmationForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            event.preventDefault();

            formToSubmit = this;

            const message =
                this.dataset.message ||
                "Are you sure you want to continue?";

            confirmationMessage.textContent = message;

            confirmationModal.classList.add("show");

        });

    });


    // Cancel
    confirmationCancel.addEventListener("click", function () {

        confirmationModal.classList.remove("show");

        formToSubmit = null;

    });


    // Confirm
    confirmationOk.addEventListener("click", function () {

        if (formToSubmit) {

            formToSubmit.submit();

        }

    });


    // Click outside modal
    confirmationModal.addEventListener("click", function (event) {

        if (event.target === confirmationModal) {

            confirmationModal.classList.remove("show");

            formToSubmit = null;

        }

    });

});


// ========================================
// DARK MODE TOGGLE
// ========================================

const themeToggle = document.getElementById("theme-toggle");

const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {

    document.documentElement.setAttribute("data-theme", "dark");

}

function updateThemeIcon() {

    if (!themeToggle) {
        return;
    }

    const icon = themeToggle.querySelector("i");

    if (!icon) {
        return;
    }

    const currentTheme =
        document.documentElement.getAttribute("data-theme");

    if (currentTheme === "dark") {

        icon.classList.remove("fa-moon");

        icon.classList.add("fa-sun");

        themeToggle.setAttribute(
            "aria-label",
            "Switch to light mode"
        );

    } else {

        icon.classList.remove("fa-sun");

        icon.classList.add("fa-moon");

        themeToggle.setAttribute(
            "aria-label",
            "Switch to dark mode"
        );

    }

}

updateThemeIcon();


if (themeToggle) {

    themeToggle.addEventListener("click", function () {

        const currentTheme =
            document.documentElement.getAttribute("data-theme");

        if (currentTheme === "dark") {

            document.documentElement.removeAttribute("data-theme");

            localStorage.setItem("theme", "light");

        } else {

            document.documentElement.setAttribute("data-theme", "dark");

            localStorage.setItem("theme", "dark");

        }

        updateThemeIcon();

    });

}