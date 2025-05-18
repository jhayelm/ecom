function nextStep() {
    var step1 = document.getElementById('step1');
    var step2 = document.getElementById('step2');
    var step3 = document.getElementById('step3');
    var step4 = document.getElementById('step4');
    var step5 = document.getElementById('step5');

    // Check each step and trigger necessary actions or flash messages
    if (step1.style.display !== 'none') {
        var category = document.getElementById('productCategory').value;
        if (category) {
            step1.style.display = 'none';
            step2.style.display = 'block';
        } else {
            // Trigger a flash message if category is missing
            showFlashMessage('Please select a category.', 'danger');
        }
    } else if (step2.style.display !== 'none') {
            step2.style.display = 'none';
            step3.style.display = 'block';

    } else if (step3.style.display !== 'none') {
        var specifications = document.querySelectorAll('[name="specType[]"]').length;
        var validSpecifications = true;

        // Check if specifications are filled properly
        for (var i = 0; i < specifications; i++) {
            var specType = document.querySelectorAll('[name="specType[]"]')[i].value;
            var specContent = document.querySelectorAll('[name="specContent[]"]')[i].value;
            if (!specType || !specContent) {
                validSpecifications = false;
                break;
            }
        }

        if (validSpecifications) {
            step3.style.display = 'none';
            step4.style.display = 'block';
        } else {
            // Trigger a flash message if specifications are not complete
            showFlashMessage('Please fill specifications for product.', 'danger');
        }
    } else if (step4.style.display !== 'none') {
        var colorVariants = document.querySelectorAll('[name="colorVariant[]"]').length;
        var validColors = true;

        // Check if color variants are filled properly
        for (var i = 0; i < colorVariants; i++) {
            var color = document.querySelectorAll('[name="colorVariant[]"]')[i].value;
            if (!color) {
                validColors = false;
                break;
            }
        }

        if (validColors) {
            step4.style.display = 'none';
            step5.style.display = 'block';
        } else {
            // Trigger a flash message if color variants are not complete
            showFlashMessage('Please enter color variants.', 'danger');
        }
    } else if (step5.style.display !== 'none') {
        var productImages = document.getElementById('productImages').files.length;

        if (productImages > 0) {
            // All fields are validated, submit the form
            document.forms[0].submit();
        } else {
            // Trigger a flash message if images are missing
            showFlashMessage('Please upload product images.', 'danger');
        }
    }
}


function previousStep() {
    var step1 = document.getElementById('step1');
    var step2 = document.getElementById('step2');
    var step3 = document.getElementById('step3');
    var step4 = document.getElementById('step4');
    var step5 = document.getElementById('step5');
    
    // Check if we are on Step 1
    if (step1.style.display !== 'none') {
        var modal = new bootstrap.Modal(document.getElementById('addProductModal'));
        modal.hide();  // Close the modal
    } else if (step2.style.display !== 'none') {
        step2.style.display = 'none';
        step1.style.display = 'block';
    } else if (step3.style.display !== 'none') {
        step3.style.display = 'none';
        step2.style.display = 'block';
    } else if (step4.style.display !== 'none') {
        step4.style.display = 'none';
        step3.style.display = 'block';
    } else if (step5.style.display !== 'none') {
        step5.style.display = 'none';
        step4.style.display = 'block';
    }
}


function showFlashMessage(message, category) {
    var flashMessageContainer = document.getElementById('flash-message-container');
    
    var flashMessageHTML = `
        <div class="alert alert-${category} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    flashMessageContainer.innerHTML = flashMessageHTML;
    flashMessageContainer.style.display = 'block';

    // Automatically hide the message after 5 seconds
    setTimeout(function() {
        flashMessageContainer.style.display = 'none';
    }, 5000);
}



// Function to add a new specification field dynamically
function addSpecification() {
    var container = document.getElementById('specificationsContainer');
    var newSpec = document.createElement('div');
    newSpec.classList.add('specification', 'mb-3');
    newSpec.innerHTML = `
        <div class="row w-100">
            <div class="col-md-5">
                <label class="form-label">Specs Type</label>
                <input type="text" class="form-control" name="specType[]" placeholder="ex. CPU">
            </div>
            <div class="col-md-5">
                <label class="form-label">Specs Content</label>
                <input type="text" class="form-control" name="specContent[]" placeholder="ex. Intel i5">
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button type="button" class="btn btn-danger" onclick="removeSpecification(this)">Delete</button>
            </div>
        </div>
    `;
    container.appendChild(newSpec);
}

// Function to remove a specification field
function removeSpecification(button) {
    var spec = button.closest('.specification');
    spec.remove();
}

// Function to remove a color variant field
function removeColorVariant(button) {
    const colorVariant = button.closest('.color-variant');
    colorVariant.remove();
}

// Image preview functionality for product images
document.getElementById('productImages').addEventListener('change', function(event) {
    var files = event.target.files;
    var previewContainer = document.getElementById('imagePreviewContainer');
    previewContainer.innerHTML = ''; // Clear previous previews

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var reader = new FileReader();

        reader.onload = function(e) {
            var img = document.createElement('img');
            img.src = e.target.result;
            img.classList.add('img-thumbnail', 'm-2');
            img.style.maxWidth = '150px';
            img.style.maxHeight = '150px';
            previewContainer.appendChild(img);
        };

        reader.readAsDataURL(file);
    }
});

// Function to handle product submission
function submitProduct() {
    // Close the add product modal
    var addProductModal = document.getElementById('addProductModal');
    var addProductInstance = bootstrap.Modal.getInstance(addProductModal);
    addProductInstance.hide();

    // Show the confirmation modal
    var confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
    confirmationModal.show();

    // Reset the modal to Step 1
    resetAddProductModal();
}

// Function to reset the modal and return to Step 1
function resetAddProductModal() {
    // Display Step 1 and hide all other steps
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('step3').style.display = 'none';
    document.getElementById('step4').style.display = 'none';

    // Reset form inputs (optional)
    document.getElementById('productCategory').value = '';
    document.getElementById('productName').value = '';
    document.getElementById('productDescription').value = '';
    document.getElementById('productPrice').value = '';
    document.getElementById('productImage').value = '';

    // Clear dynamically added specifications and color variants
    document.getElementById('specificationsContainer').innerHTML = '';
    document.getElementById('colorVariantsContainer').innerHTML = '';
}



function addSpecField() {
        var specsDiv = document.getElementById("specs-section");
        var newSpecType = document.createElement("input");
        newSpecType.type = "text";
        newSpecType.name = "specType[]";
        newSpecType.placeholder = "Specification Type";
        specsDiv.appendChild(newSpecType);

        var newSpecContent = document.createElement("input");
        newSpecContent.type = "text";
        newSpecContent.name = "specContent[]";
        newSpecContent.placeholder = "Specification Content";
        specsDiv.appendChild(newSpecContent);
    }

function addColorField() {
    var colorDiv = document.getElementById("color-section");
    var newColor = document.createElement("input");
    newColor.type = "text";
    newColor.name = "colorVariant[]";
    newColor.placeholder = "Color Variant";
    colorDiv.appendChild(newColor);
}



function addColorVariant() {
    const container = document.getElementById("colorVariantsContainer");
    var newColor = document.createElement('div');
    newColor.classList.add('color-variant', 'mb-3'); // Ensure this class matches
    const colorVariantHTML = `
        <div class="row w-100">
            <div class="col-md-10">
                <label class="form-label">Choose Color</label>
                <input type="text" class="form-control" name="colorVariant[]" placeholder="Enter color (ex. Red)" required>
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button type="button" class="btn btn-danger" onclick="removeColorVariant(this)">Delete</button>
            </div>
        </div>
    `;
    
    newColor.innerHTML = colorVariantHTML;
    container.appendChild(newColor);
}

