document.addEventListener('DOMContentLoaded', function () {
    const updateProductModal = document.getElementById('updateProductModal');

    updateProductModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;  // Button that triggered the modal

        // Extract data from data-* attributes
        const productId = button.getAttribute('data-product-id');
        const productInfoId = button.getAttribute('data-product-info-id');
        const productCategory = button.getAttribute('data-product-category');
        const productName = button.getAttribute('data-product-name');
        const productDescription = button.getAttribute('data-product-description');
        const productPrice = button.getAttribute('data-product-price');

        // Populate hidden inputs and other fields in the modal
        document.getElementById('updateProductId').value = productId;
        document.getElementById('updateProductInfoId').value = productInfoId;
        document.getElementById('updateProductCategory').value = productCategory;
        document.getElementById('updateProductName').value = productName;
        document.getElementById('updateProductDescription').value = productDescription;
        document.getElementById('updateProductPrice').value = productPrice;
    });
});


function submitUpdate() {
    // Perform the update action, for example, submitting the form
    document.getElementById('updateProductForm').submit();
}
