// Wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Handle recipe search form
    const searchTypeSelect = document.getElementById('search_type');
    if (searchTypeSelect) {
        // Set search type from URL parameter if available
        const urlParams = new URLSearchParams(window.location.search);
        const searchType = urlParams.get('search_type');
        if (searchType) {
            searchTypeSelect.value = searchType;
        }
    }
    
    // Preview image upload (for recipe form)
    const imageInput = document.querySelector('input[type="file"]');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Check if there's already a preview
                    let preview = document.querySelector('.image-preview');
                    
                    // If no preview exists, create one
                    if (!preview) {
                        const previewContainer = document.createElement('div');
                        previewContainer.className = 'mt-3';
                        previewContainer.innerHTML = `
                            <label class="form-label">Image Preview</label>
                            <img src="${e.target.result}" class="img-fluid rounded image-preview" alt="Recipe preview">
                        `;
                        
                        // Insert after the file input
                        imageInput.parentNode.appendChild(previewContainer);
                    } else {
                        // Update existing preview
                        preview.src = e.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Print recipe functionality
    const printButtons = document.querySelectorAll('.print-recipe');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
});
