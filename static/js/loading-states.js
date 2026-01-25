// Loading states for forms
document.addEventListener('DOMContentLoaded', function() {
    // Add loading state to all forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            
            submitButtons.forEach(button => {
                // Store original content
                button.dataset.originalContent = button.innerHTML;
                
                // Add loading state
                button.disabled = true;
                
                // Add spinner if button contains text
                if (button.innerHTML.trim()) {
                    button.innerHTML = `
                        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>${button.dataset.originalContent.includes('>') ? 'Enviando...' : button.textContent}</span>
                    `;
                }
            });
        });
    });
    
    // Add skeleton screens to list containers
    const listContainers = document.querySelectorAll('.list-skeleton');
    listContainers.forEach(container => {
        // This would be triggered when loading data dynamically
        // For now, we'll just add a function to enable skeleton screens
        container.classList.add('opacity-100');
    });
});

// Function to show/hide loading state on specific button
function setLoadingState(button, isLoading) {
    if (isLoading) {
        // Store original content
        button.dataset.originalContent = button.innerHTML;
        button.disabled = true;
        
        // Add spinner
        button.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Enviando...</span>
        `;
    } else {
        // Restore original content
        button.disabled = false;
        button.innerHTML = button.dataset.originalContent || button.innerHTML;
    }
}