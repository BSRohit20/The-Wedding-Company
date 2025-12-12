// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let authToken = null;
let currentUser = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check if there's a saved token
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        updateAuthStatus(true);
    }
    
    updateAuthWarnings();
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Clear previous responses
    clearAllResponses();
}

// Clear all response boxes
function clearAllResponses() {
    const responses = document.querySelectorAll('.response-box');
    responses.forEach(resp => {
        resp.classList.remove('visible', 'success', 'error');
        resp.innerHTML = '';
    });
}

// Display response
function displayResponse(elementId, data, isSuccess = true) {
    const element = document.getElementById(elementId);
    element.classList.add('visible', isSuccess ? 'success' : 'error');
    
    const title = isSuccess ? '✅ Success' : '❌ Error';
    const jsonString = JSON.stringify(data, null, 2);
    
    element.innerHTML = `
        <h3>${title}</h3>
        <pre>${jsonString}</pre>
    `;
}

// Update auth status
function updateAuthStatus(isAuthenticated) {
    const statusElement = document.getElementById('authStatus');
    const indicator = statusElement.querySelector('.status-indicator');
    const text = statusElement.querySelector('span:last-child');
    
    if (isAuthenticated && currentUser) {
        indicator.classList.remove('offline');
        indicator.classList.add('online');
        text.textContent = `Logged in as ${currentUser.admin_email}`;
    } else {
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        text.textContent = 'Not Authenticated';
    }
    
    updateAuthWarnings();
}

// Update auth warnings
function updateAuthWarnings() {
    const updateWarning = document.getElementById('updateAuthWarning');
    const deleteWarning = document.getElementById('deleteAuthWarning');
    
    if (authToken) {
        updateWarning.classList.remove('visible');
        deleteWarning.classList.remove('visible');
    } else {
        updateWarning.classList.add('visible');
        deleteWarning.classList.add('visible');
    }
}

// Create Organization
async function createOrganization(event) {
    event.preventDefault();
    
    const orgName = document.getElementById('create_org_name').value;
    const email = document.getElementById('create_email').value;
    const password = document.getElementById('create_password').value;
    
    const button = event.target.querySelector('button');
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Creating...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/org/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                organization_name: orgName,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResponse('createResponse', data, true);
            event.target.reset();
        } else {
            displayResponse('createResponse', data, false);
        }
    } catch (error) {
        displayResponse('createResponse', { error: error.message }, false);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Admin Login
async function adminLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login_email').value;
    const password = document.getElementById('login_password').value;
    
    const button = event.target.querySelector('button');
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Logging in...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save token and user info
            authToken = data.access_token;
            currentUser = {
                admin_email: data.admin_email,
                organization_name: data.organization_name
            };
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            updateAuthStatus(true);
            displayResponse('loginResponse', data, true);
            event.target.reset();
        } else {
            displayResponse('loginResponse', data, false);
        }
    } catch (error) {
        displayResponse('loginResponse', { error: error.message }, false);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// View Organization
async function viewOrganization(event) {
    event.preventDefault();
    
    const orgName = document.getElementById('view_org_name').value;
    
    const button = event.target.querySelector('button');
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Loading...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/org/get?organization_name=${orgName}`);
        const data = await response.json();
        
        if (response.ok) {
            displayResponse('viewResponse', data, true);
        } else {
            displayResponse('viewResponse', data, false);
        }
    } catch (error) {
        displayResponse('viewResponse', { error: error.message }, false);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Update Organization
async function updateOrganization(event) {
    event.preventDefault();
    
    if (!authToken) {
        displayResponse('updateResponse', { error: 'Please login first' }, false);
        return;
    }
    
    const oldName = document.getElementById('update_old_name').value;
    const newName = document.getElementById('update_new_name').value;
    
    const button = event.target.querySelector('button');
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Updating...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/org/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                organization_name: oldName,
                new_organization_name: newName
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResponse('updateResponse', data, true);
            event.target.reset();
            
            // Update current user if they updated their own org
            if (currentUser && currentUser.organization_name === oldName) {
                currentUser.organization_name = newName;
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                updateAuthStatus(true);
            }
        } else {
            displayResponse('updateResponse', data, false);
            
            // Handle token expiration
            if (response.status === 401) {
                handleLogout();
            }
        }
    } catch (error) {
        displayResponse('updateResponse', { error: error.message }, false);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Delete Organization
async function deleteOrganization(event) {
    event.preventDefault();
    
    if (!authToken) {
        displayResponse('deleteResponse', { error: 'Please login first' }, false);
        return;
    }
    
    const orgName = document.getElementById('delete_org_name').value;
    
    // Confirmation
    if (!confirm(`Are you sure you want to delete "${orgName}"? This action cannot be undone.`)) {
        return;
    }
    
    const button = event.target.querySelector('button');
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Deleting...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/org/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                organization_name: orgName
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResponse('deleteResponse', data, true);
            event.target.reset();
            
            // If user deleted their own organization, logout
            if (currentUser && currentUser.organization_name === orgName) {
                setTimeout(() => {
                    handleLogout();
                    alert('Your organization has been deleted. You have been logged out.');
                }, 2000);
            }
        } else {
            displayResponse('deleteResponse', data, false);
            
            // Handle token expiration
            if (response.status === 401) {
                handleLogout();
            }
        }
    } catch (error) {
        displayResponse('deleteResponse', { error: error.message }, false);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Handle Logout
function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    updateAuthStatus(false);
}

// Add logout button functionality (optional - you can add this to the header)
window.logout = function() {
    if (confirm('Are you sure you want to logout?')) {
        handleLogout();
        alert('Logged out successfully');
    }
};
