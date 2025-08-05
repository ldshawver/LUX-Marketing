// Main JavaScript file for Email Marketing Automation Bot
// Handles client-side interactions and UI enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidation();
    
    // Initialize auto-dismiss alerts
    initializeAlerts();
    
    // Initialize campaign preview functionality
    initializeCampaignPreview();
    
    // Initialize contact management features
    initializeContactManagement();
    
    // Initialize template management
    initializeTemplateManagement();
    
    // Initialize analytics charts
    initializeAnalytics();
    
    // Add loading states to forms
    initializeLoadingStates();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Campaign form validation
    const campaignForm = document.querySelector('form[action*="create_campaign"]');
    if (campaignForm) {
        campaignForm.addEventListener('submit', function(e) {
            if (!validateCampaignForm(this)) {
                e.preventDefault();
            }
        });
    }
    
    // Template form validation
    const templateForm = document.querySelector('form[action*="create_template"]');
    if (templateForm) {
        templateForm.addEventListener('submit', function(e) {
            if (!validateTemplateForm(this)) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Validate email address format
 */
function validateEmail(input) {
    const email = input.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        input.classList.add('is-invalid');
        showFieldError(input, 'Please enter a valid email address');
        return false;
    } else {
        input.classList.remove('is-invalid');
        hideFieldError(input);
        return true;
    }
}

/**
 * Validate campaign form
 */
function validateCampaignForm(form) {
    let isValid = true;
    
    // Check required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            hideFieldError(field);
        }
    });
    
    // Validate scheduled date
    const scheduledAt = form.querySelector('#scheduled_at');
    if (scheduledAt && scheduledAt.value) {
        const scheduledDate = new Date(scheduledAt.value);
        const now = new Date();
        
        if (scheduledDate <= now) {
            scheduledAt.classList.add('is-invalid');
            showFieldError(scheduledAt, 'Scheduled time must be in the future');
            isValid = false;
        } else {
            scheduledAt.classList.remove('is-invalid');
            hideFieldError(scheduledAt);
        }
    }
    
    return isValid;
}

/**
 * Validate template form
 */
function validateTemplateForm(form) {
    let isValid = true;
    
    // Check HTML content
    const htmlContent = form.querySelector('#html_content');
    if (htmlContent && htmlContent.value.trim().length < 50) {
        htmlContent.classList.add('is-invalid');
        showFieldError(htmlContent, 'HTML content must be at least 50 characters long');
        isValid = false;
    } else if (htmlContent) {
        htmlContent.classList.remove('is-invalid');
        hideFieldError(htmlContent);
    }
    
    return isValid;
}

/**
 * Show field error message
 */
function showFieldError(field, message) {
    hideFieldError(field); // Remove existing error
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Hide field error message
 */
function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Initialize auto-dismiss alerts
 */
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Initialize campaign preview functionality
 */
function initializeCampaignPreview() {
    // Add preview buttons to campaign rows
    const previewButtons = document.querySelectorAll('[data-action="preview"]');
    previewButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const campaignId = this.dataset.campaignId;
            previewCampaign(campaignId);
        });
    });
}

/**
 * Preview campaign in modal
 */
function previewCampaign(campaignId) {
    // This would typically fetch preview data via AJAX
    // For now, redirect to preview page
    window.location.href = `/campaigns/${campaignId}/preview`;
}

/**
 * Initialize contact management features
 */
function initializeContactManagement() {
    // Bulk contact selection
    const selectAllCheckbox = document.querySelector('#select-all-contacts');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const contactCheckboxes = document.querySelectorAll('.contact-checkbox');
            contactCheckboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateBulkActions();
        });
    }
    
    // Individual contact selection
    const contactCheckboxes = document.querySelectorAll('.contact-checkbox');
    contactCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', updateBulkActions);
    });
    
    // CSV import validation
    const csvFileInput = document.querySelector('#file');
    if (csvFileInput) {
        csvFileInput.addEventListener('change', function() {
            validateCSVFile(this);
        });
    }
    
    // Contact search with debounce
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto-submit search after 500ms of no typing
                if (this.value.length > 2 || this.value.length === 0) {
                    this.form.submit();
                }
            }, 500);
        });
    }
}

/**
 * Update bulk actions based on selected contacts
 */
function updateBulkActions() {
    const selectedContacts = document.querySelectorAll('.contact-checkbox:checked');
    const bulkActionsDiv = document.querySelector('#bulk-actions');
    
    if (bulkActionsDiv) {
        if (selectedContacts.length > 0) {
            bulkActionsDiv.style.display = 'block';
            bulkActionsDiv.querySelector('.selected-count').textContent = selectedContacts.length;
        } else {
            bulkActionsDiv.style.display = 'none';
        }
    }
}

/**
 * Validate CSV file upload
 */
function validateCSVFile(input) {
    const file = input.files[0];
    
    if (file) {
        const fileName = file.name.toLowerCase();
        const fileSize = file.size;
        
        // Check file extension
        if (!fileName.endsWith('.csv')) {
            input.classList.add('is-invalid');
            showFieldError(input, 'Please select a CSV file');
            return false;
        }
        
        // Check file size (max 5MB)
        if (fileSize > 5 * 1024 * 1024) {
            input.classList.add('is-invalid');
            showFieldError(input, 'File size must be less than 5MB');
            return false;
        }
        
        input.classList.remove('is-invalid');
        hideFieldError(input);
        return true;
    }
}

/**
 * Initialize template management
 */
function initializeTemplateManagement() {
    // Template preview functionality
    const previewButtons = document.querySelectorAll('[onclick^="previewTemplate"]');
    previewButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const templateId = this.onclick.toString().match(/\d+/)[0];
            previewTemplate(templateId);
        });
    });
    
    // Template variable insertion
    const variableButtons = document.querySelectorAll('[data-variable]');
    variableButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const variable = this.dataset.variable;
            const htmlContent = document.querySelector('#html_content');
            if (htmlContent) {
                insertAtCursor(htmlContent, `{{${variable}}}`);
            }
        });
    });
}

/**
 * Insert text at cursor position in textarea
 */
function insertAtCursor(textarea, text) {
    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const textAreaValue = textarea.value;
    
    textarea.value = textAreaValue.substring(0, startPos) + text + textAreaValue.substring(endPos);
    textarea.selectionStart = textarea.selectionEnd = startPos + text.length;
    textarea.focus();
}

/**
 * Initialize analytics features
 */
function initializeAnalytics() {
    // Add click tracking for chart interactions
    const charts = document.querySelectorAll('canvas');
    charts.forEach(function(chart) {
        chart.addEventListener('click', function(e) {
            // Chart click handling would go here
            console.log('Chart clicked:', e);
        });
    });
    
    // Auto-refresh analytics data every 30 seconds on analytics page
    if (window.location.pathname.includes('/analytics')) {
        setInterval(function() {
            refreshAnalyticsData();
        }, 30000);
    }
}

/**
 * Refresh analytics data (placeholder for AJAX implementation)
 */
function refreshAnalyticsData() {
    // This would typically make an AJAX call to update analytics
    console.log('Refreshing analytics data...');
}

/**
 * Initialize loading states for forms
 */
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable after 30 seconds as fallback
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
                }, 30000);
            }
        });
    });
}

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('#toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Utility function to confirm dangerous actions
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Initialize keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl+S to save forms
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.click();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showToast('An unexpected error occurred. Please refresh the page.', 'danger');
});

// Global functions for template usage
window.EmailMarketing = {
    showToast: showToast,
    confirmAction: confirmAction,
    validateEmail: validateEmail
};
