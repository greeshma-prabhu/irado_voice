// Irado Chatbot Dashboard JavaScript

let currentData = [];
let currentPage = 1;
let itemsPerPage = 50;
let currentSearch = '';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    // Don't load all data by default - only show search prompt
    showSearchPrompt();
    setupEventListeners();
    
    // Initialize chat tab when clicked
    document.getElementById('chat-tab').addEventListener('click', function() {
        loadChatStats();
        loadChatSessions();
    });
    
    // Initialize system prompt tab when clicked
    document.getElementById('prompt-tab').addEventListener('click', function() {
        loadSystemPrompts();
        loadActivePrompt();
    });
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    
    // Form submissions
    document.getElementById('add-entry-form').addEventListener('submit', function(e) {
        e.preventDefault();
        addEntry();
    });
    
    document.getElementById('edit-entry-form').addEventListener('submit', function(e) {
        e.preventDefault();
        updateEntry();
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();
        
        if (result.success) {
            const stats = result.data;
            document.getElementById('total-entries').textContent = stats.total_entries.toLocaleString();
            document.getElementById('active-entries').textContent = stats.active_entries.toLocaleString();
            document.getElementById('unique-postcodes').textContent = stats.unique_postcodes.toLocaleString();
            document.getElementById('unique-streets').textContent = stats.unique_streets.toLocaleString();
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Error loading statistics', 'error');
    }
}

// Show search prompt instead of loading all data
function showSearchPrompt() {
    const tbody = document.getElementById('koad-table-body');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center text-muted py-5">
                <i class="fas fa-search fa-3x mb-3 d-block"></i>
                       <h5>Zoek in Bedrijfsklanten</h5>
                       <p class="mb-0">Gebruik het zoekveld hierboven om entries te vinden</p>
                       <small class="text-muted">Voer een straat, postcode, huisnummer of naam in</small>
            </td>
        </tr>
    `;
    updateTableInfo(0, 'Gebruik zoekfunctie om entries te vinden');
}

// Load data is removed - use search instead (128k records is too much to load all at once)

// Search functionality
async function handleSearch(event) {
    const query = event.target.value.trim();
    currentSearch = query;
    
    if (query === '') {
        showSearchPrompt();
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`/api/koad/search?q=${encodeURIComponent(query)}`);
        
        // Check if response is ok
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse JSON response
        const result = await response.json();
        
        if (result.success) {
            displayData(result.data);
            updateTableInfo(result.total, query);
        } else {
            showToast('Search error: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search error: ' + error.message, 'error');
        showSearchPrompt(); // Go back to search prompt on error
    } finally {
        hideLoading();
    }
}

// Display data in table
function displayData(data) {
    const tbody = document.getElementById('koad-table-body');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Geen data gevonden</td></tr>';
        return;
    }
    
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index}</td>
            <td>${item['KOAD-str'] || '-'}</td>
            <td>${item['KOAD-pc'] || '-'}</td>
            <td>${item['KOAD-huisnr'] || '-'}</td>
            <td>${item['KOAD-naam'] || '-'}</td>
            <td>
                <span class="badge ${item['KOAD-actief'] === '1' ? 'bg-success' : 'bg-danger'}">
                    ${item['KOAD-actief'] === '1' ? 'Actief' : 'Inactief'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary btn-action" onclick="editEntry(${index})" title="Bewerken">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteEntry(${index})" title="Verwijderen">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update table info
function updateTableInfo(total = null, query = null) {
    const info = document.getElementById('table-info');
    const count = total || currentData.length;
    
    if (query) {
        info.textContent = `${count} resultaten voor "${query}"`;
    } else {
        info.textContent = `${count} entries geladen`;
    }
}

// Add new entry
async function addEntry() {
    const form = document.getElementById('add-entry-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/koad/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Entry succesvol toegevoegd', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addEntryModal')).hide();
            form.reset();
            loadData();
            loadStats();
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error adding entry:', error);
        showToast('Error adding entry', 'error');
    }
}

// Edit entry
function editEntry(index) {
    const item = currentData[index];
    
    // Populate edit form
    document.getElementById('edit-entry-id').value = index;
    document.getElementById('edit-koad-nummer').value = item['KOAD-nummer'] || '';
    document.getElementById('edit-koad-str').value = item['KOAD-str'] || '';
    document.getElementById('edit-koad-pc').value = item['KOAD-pc'] || '';
    document.getElementById('edit-koad-huisnr').value = item['KOAD-huisnr'] || '';
    document.getElementById('edit-koad-huisaand').value = item['KOAD-huisaand'] || '';
    document.getElementById('edit-koad-etage').value = item['KOAD-etage'] || '';
    document.getElementById('edit-koad-naam').value = item['KOAD-naam'] || '';
    document.getElementById('edit-koad-actief').value = item['KOAD-actief'] || '1';
    document.getElementById('edit-koad-inwoner').value = item['KOAD-inwoner'] || '1';
    
    // Show modal
    new bootstrap.Modal(document.getElementById('editEntryModal')).show();
}

// Update entry
async function updateEntry() {
    const form = document.getElementById('edit-entry-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const entryId = parseInt(data.id);
    
    try {
        const response = await fetch('/api/koad/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Entry succesvol bijgewerkt', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editEntryModal')).hide();
            loadData();
            loadStats();
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error updating entry:', error);
        showToast('Error updating entry', 'error');
    }
}

// Delete entry
async function deleteEntry(index) {
    if (!confirm('Weet je zeker dat je deze entry wilt verwijderen?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/koad/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: index })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Entry succesvol verwijderd', 'success');
            loadData();
            loadStats();
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting entry:', error);
        showToast('Error deleting entry', 'error');
    }
}

// Upload CSV with progress bar
async function uploadCSV() {
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Selecteer eerst een bestand', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Create progress modal
    const progressHTML = `
        <div class="modal fade" id="uploadProgressModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-upload me-2"></i>CSV KOAD Upload
                        </h5>
                    </div>
                    <div class="modal-body">
                        <div id="upload-status" class="mb-3">
                            <div class="d-flex align-items-center">
                                <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                                <span id="upload-message">Uploading...</span>
                            </div>
                        </div>
                        <div class="progress" style="height: 30px;">
                            <div id="upload-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated" 
                                 role="progressbar" style="width: 0%">
                                <span id="upload-progress-text">0%</span>
                            </div>
                        </div>
                        <div id="upload-details" class="mt-3 small text-muted">
                            <div id="upload-stats" class="row">
                                <div class="col-6">
                                    <strong>Records:</strong> <span id="record-count">-</span>
                                </div>
                                <div class="col-6">
                                    <strong>Batches:</strong> <span id="batch-count">-</span>
                                </div>
                            </div>
                            <div id="upload-timing" class="mt-2">
                                <strong>Geschatte tijd:</strong> <span id="estimated-time">-</span> | 
                                <strong>Verstreken:</strong> <span id="elapsed-time">00:00</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove old progress modal if exists
    const oldModal = document.getElementById('uploadProgressModal');
    if (oldModal) oldModal.remove();
    
    // Add new progress modal
    document.body.insertAdjacentHTML('beforeend', progressHTML);
    const progressModal = new bootstrap.Modal(document.getElementById('uploadProgressModal'));
    
    try {
        // Hide upload modal, show progress modal
        bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
        progressModal.show();
        
        updateUploadProgress(10, 'Bestand wordt gelezen...');
        
        // Create XMLHttpRequest for progress tracking
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 50); // Upload is 50% of total
                updateUploadProgress(percentComplete, `Uploading: ${Math.round(e.loaded / 1024)}KB / ${Math.round(e.total / 1024)}KB`);
            }
        });
        
        // Handle completion
        xhr.addEventListener('load', () => {
            console.log('XHR Response:', xhr.status, xhr.responseText);
            
            if (xhr.status === 200) {
                try {
                    const result = JSON.parse(xhr.responseText);
                    console.log('Parsed result:', result);
                    
                    if (result.success) {
                        updateUploadProgress(100, `✅ Succesvol! ${result.total} records geïmporteerd`, 'success');
                        
                        setTimeout(() => {
                            progressModal.hide();
                            showToast(`CSV succesvol geüpload: ${result.total} entries`, 'success');
                            fileInput.value = '';
                            loadData();
                            loadStats();
                        }, 2000);
                    } else {
                        console.error('Upload failed:', result.error);
                        updateUploadProgress(100, `❌ Error: ${result.error}`, 'error');
                        
                        // Show detailed error info
                        const details = document.getElementById('upload-details');
                        if (details) {
                            details.innerHTML = `
                                <div class="alert alert-danger mt-2">
                                    <strong>Error Details:</strong><br>
                                    ${result.error}<br>
                                    <small>Status: ${xhr.status} | Response: ${xhr.responseText.substring(0, 200)}...</small>
                                </div>
                            `;
                        }
                    }
                } catch (e) {
                    console.error('JSON parse error:', e);
                    updateUploadProgress(100, `❌ Invalid response: ${e.message}`, 'error');
                    
                    const details = document.getElementById('upload-details');
                    if (details) {
                        details.innerHTML = `
                            <div class="alert alert-danger mt-2">
                                <strong>Parse Error:</strong><br>
                                ${e.message}<br>
                                <small>Raw response: ${xhr.responseText.substring(0, 200)}...</small>
                            </div>
                        `;
                    }
                }
            } else {
                console.error('HTTP Error:', xhr.status, xhr.statusText);
                updateUploadProgress(100, `❌ HTTP ${xhr.status}: ${xhr.statusText}`, 'error');
                
                const details = document.getElementById('upload-details');
                if (details) {
                    details.innerHTML = `
                        <div class="alert alert-danger mt-2">
                            <strong>HTTP Error:</strong><br>
                            Status: ${xhr.status}<br>
                            Message: ${xhr.statusText}<br>
                            <small>Response: ${xhr.responseText.substring(0, 200)}...</small>
                        </div>
                    `;
                }
            }
        });
        
        // Handle errors
        xhr.addEventListener('error', () => {
            updateUploadProgress(100, '❌ Network error', 'error');
        });
        
        // Handle timeout
        xhr.addEventListener('timeout', () => {
            updateUploadProgress(100, '❌ Upload timeout (neem meer dan 15 minuten)', 'error');
        });
        
        // Send request with cache busting
        xhr.open('POST', `/api/koad/upload?t=${Date.now()}`);
        xhr.timeout = 900000; // 15 minutes timeout for large files
        xhr.send(formData);
        
        // Start polling for detailed progress from server logs
        startProgressPolling();
        
    } catch (error) {
        console.error('Error uploading CSV:', error);
        updateUploadProgress(100, `❌ Error: ${error.message}`, 'error');
    }
}

function updateUploadProgress(percent, message, type = 'info') {
    const progressBar = document.getElementById('upload-progress-bar');
    const progressText = document.getElementById('upload-progress-text');
    const statusMessage = document.getElementById('upload-message');
    
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.setAttribute('aria-valuenow', percent);
        
        if (type === 'success') {
            progressBar.classList.remove('progress-bar-animated', 'bg-danger');
            progressBar.classList.add('bg-success');
        } else if (type === 'error') {
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-danger');
        }
    }
    
    if (progressText) {
        progressText.textContent = Math.round(percent) + '%';
    }
    
    if (statusMessage) {
        statusMessage.innerHTML = message;
    }
}

let progressPollingInterval = null;
let uploadStartTime = null;
let totalRecords = 0;
let totalBatches = 0;

function startProgressPolling() {
    uploadStartTime = Date.now();
    
    // Poll dashboard logs for upload progress
    progressPollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/dashboard/logs?limit=20');
            const data = await response.json();
            
            if (data.success && data.logs.length > 0) {
                // Look for CSV upload related logs
                const csvLogs = data.logs.filter(log => 
                    log.message && (
                        log.message.includes('CSV') || 
                        log.message.includes('records') || 
                        log.message.includes('Progress:') ||
                        log.message.includes('batch') ||
                        log.message.includes('import')
                    )
                );
                
                if (csvLogs.length > 0) {
                    const latestLog = csvLogs[0];
                    const details = document.getElementById('upload-details');
                    
                    if (details && latestLog.message) {
                        let progressInfo = '';
                        let progressPercent = 0;
                        
                        // Check for specific actions
                        if (latestLog.action === 'file_read') {
                            const rows = latestLog.details?.rows || 0;
                            totalRecords = rows;
                            totalBatches = Math.ceil(rows / 1000);
                            progressInfo = `📊 ${rows.toLocaleString()} records gevonden in CSV`;
                            progressPercent = 20;
                            updateUploadProgress(progressPercent, 'CSV parsed, uploading naar database...');
                            updateUploadStats(rows, totalBatches);
                        } else if (latestLog.action === 'uploading_to_db') {
                            const count = latestLog.details?.record_count || 0;
                            const batches = latestLog.details?.estimated_batches || 0;
                            totalRecords = count;
                            totalBatches = batches;
                            progressInfo = `💾 ${count.toLocaleString()} records worden geïmporteerd...`;
                            progressPercent = 30;
                            updateUploadProgress(progressPercent, 'Database import bezig...');
                            updateUploadStats(count, batches);
                        } else if (latestLog.action === 'batch_progress') {
                            // Real-time batch progress
                            const imported = latestLog.details?.records_imported || 0;
                            const total = latestLog.details?.total_records || totalRecords;
                            const percent = latestLog.details?.progress_percent || 0;
                            
                            if (total > 0) {
                                totalRecords = total;
                                progressPercent = Math.max(30, Math.min(90, percent));
                                progressInfo = `🔄 ${imported.toLocaleString()}/${total.toLocaleString()} records (${percent}%)`;
                                updateUploadProgress(progressPercent, `Database import: ${percent}% voltooid`);
                                updateUploadStats(imported, totalBatches);
                            }
                        } else if (latestLog.action === 'upload_success') {
                            const imported = latestLog.details?.imported || 0;
                            progressInfo = `✅ ${imported.toLocaleString()} records succesvol geïmporteerd!`;
                            progressPercent = 100;
                            updateUploadProgress(progressPercent, 'Import voltooid!');
                            stopProgressPolling();
                        } else if (latestLog.level === 'error') {
                            progressInfo = `❌ ${latestLog.message}`;
                            progressPercent = 100;
                            updateUploadProgress(progressPercent, latestLog.message, 'error');
                            stopProgressPolling();
                        } else if (latestLog.message.includes('Progress:')) {
                            // Parse progress from log message
                            const progressMatch = latestLog.message.match(/(\d+)%\)/);
                            if (progressMatch) {
                                const percent = parseInt(progressMatch[1]);
                                progressPercent = Math.max(30, Math.min(90, percent));
                                progressInfo = `🔄 Database import: ${percent}%`;
                                updateUploadProgress(progressPercent, `Database import: ${percent}% voltooid`);
                            }
                        }
                    
                        // Update timing information
                        updateTimingInfo();
                        
                        if (progressInfo) {
                            const statsDiv = document.getElementById('upload-stats');
                            if (statsDiv) {
                                statsDiv.innerHTML = `
                                    <div class="col-6">
                                        <strong>Records:</strong> <span id="record-count">${totalRecords.toLocaleString()}</span>
                                    </div>
                                    <div class="col-6">
                                        <strong>Batches:</strong> <span id="batch-count">${totalBatches}</span>
                                    </div>
                                `;
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error polling progress:', error);
        }
    }, 1000); // Poll every second
}

function updateUploadStats(records, batches) {
    const recordCount = document.getElementById('record-count');
    const batchCount = document.getElementById('batch-count');
    
    if (recordCount) recordCount.textContent = records.toLocaleString();
    if (batchCount) batchCount.textContent = batches;
}

function updateTimingInfo() {
    if (!uploadStartTime) return;
    
    const elapsed = Date.now() - uploadStartTime;
    const elapsedSeconds = Math.floor(elapsed / 1000);
    const elapsedMinutes = Math.floor(elapsedSeconds / 60);
    const remainingSeconds = elapsedSeconds % 60;
    
    const elapsedTime = document.getElementById('elapsed-time');
    const estimatedTime = document.getElementById('estimated-time');
    
    if (elapsedTime) {
        elapsedTime.textContent = `${elapsedMinutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    if (estimatedTime && totalRecords > 0) {
        // Rough estimate: 1000 records per 10 seconds
        const estimatedSeconds = Math.ceil((totalRecords / 1000) * 10);
        const estimatedMinutes = Math.floor(estimatedSeconds / 60);
        const estimatedSecs = estimatedSeconds % 60;
        
        estimatedTime.textContent = `${estimatedMinutes}:${estimatedSecs.toString().padStart(2, '0')}`;
    }
}

function stopProgressPolling() {
    if (progressPollingInterval) {
        clearInterval(progressPollingInterval);
        progressPollingInterval = null;
    }
}

// Refresh data
function refreshData() {
    showSearchPrompt();
    loadStats();
}

// Show loading state
function showLoading() {
    const tbody = document.getElementById('koad-table-body');
    tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Laden...</td></tr>';
}

// Hide loading state
function hideLoading() {
    // Loading state is automatically hidden when data is displayed
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastHeader = toast.querySelector('.toast-header');
    
    toastMessage.textContent = message;
    
    // Update toast styling based on type
    toast.className = 'toast';
    if (type === 'success') {
        toastHeader.innerHTML = '<i class="fas fa-check-circle text-success me-2"></i><strong class="me-auto">Success</strong><button type="button" class="btn-close" data-bs-dismiss="toast"></button>';
    } else if (type === 'error') {
        toastHeader.innerHTML = '<i class="fas fa-exclamation-circle text-danger me-2"></i><strong class="me-auto">Error</strong><button type="button" class="btn-close" data-bs-dismiss="toast"></button>';
    } else {
        toastHeader.innerHTML = '<i class="fas fa-info-circle text-primary me-2"></i><strong class="me-auto">Info</strong><button type="button" class="btn-close" data-bs-dismiss="toast"></button>';
    }
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Chat History Functions
let currentChatData = [];

// Load chat statistics
async function loadChatStats() {
    try {
        const response = await fetch('/api/chat/stats');
        const result = await response.json();
        
        if (result.success) {
            const stats = result.data;
            document.getElementById('total-sessions').textContent = stats.total_sessions.toLocaleString();
            document.getElementById('total-messages').textContent = stats.total_messages.toLocaleString();
            document.getElementById('sessions-today').textContent = stats.sessions_today.toLocaleString();
            document.getElementById('sessions-week').textContent = stats.sessions_week.toLocaleString();
        }
    } catch (error) {
        console.error('Error loading chat stats:', error);
        showToast('Error loading chat statistics', 'error');
    }
}

// Load chat sessions
async function loadChatSessions() {
    try {
        showChatLoading();
        const response = await fetch('/api/chat/sessions');
        const result = await response.json();
        
        if (result.success) {
            currentChatData = result.data;
            displayChatSessions(currentChatData);
            updateChatTableInfo();
        } else {
            showToast('Error loading chat sessions: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error loading chat sessions:', error);
        showToast('Error loading chat sessions', 'error');
    } finally {
        hideChatLoading();
    }
}

// Display chat sessions in table
function displayChatSessions(sessions) {
    const tbody = document.getElementById('chat-sessions-table-body');
    tbody.innerHTML = '';
    
    if (sessions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Geen chat sessions gevonden</td></tr>';
        return;
    }
    
    sessions.forEach((session, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <code>${session.session_id.substring(0, 8)}...</code>
            </td>
            <td>${formatDateTime(session.created_at)}</td>
            <td>${formatDateTime(session.last_activity)}</td>
            <td>
                <span class="badge bg-primary">${session.message_count}</span>
            </td>
            <td>${session.last_message_time ? formatDateTime(session.last_message_time) : '-'}</td>
            <td>
                <button class="btn btn-sm btn-outline-info btn-action" onclick="viewChatSession('${session.session_id}')" title="Bekijk Chat">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update chat table info
function updateChatTableInfo(total = null) {
    const info = document.getElementById('chat-table-info');
    const count = total || currentChatData.length;
    info.textContent = `${count} chat sessions geladen`;
}

// View chat session details
async function viewChatSession(sessionId) {
    try {
        showChatLoading();
        const response = await fetch(`/api/chat/sessions/${sessionId}`);
        const result = await response.json();
        
        if (result.success) {
            showChatSessionModal(result.data);
        } else {
            showToast('Error loading chat session: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error loading chat session:', error);
        showToast('Error loading chat session', 'error');
    } finally {
        hideChatLoading();
    }
}

// Show chat session modal
function showChatSessionModal(data) {
    const session = data.session;
    const messages = data.messages;
    
    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="chatSessionModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-comments me-2"></i>
                            Chat Session: ${session.session_id.substring(0, 8)}...
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Gemaakt:</strong> ${formatDateTime(session.created_at)}
                            </div>
                            <div class="col-md-6">
                                <strong>Laatste Activiteit:</strong> ${formatDateTime(session.last_activity)}
                            </div>
                        </div>
                        <div class="chat-messages" style="max-height: 500px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 0.375rem; padding: 1rem;">
                            ${messages.map(msg => `
                                <div class="mb-3 ${msg.message_type === 'user' ? 'text-end' : 'text-start'}">
                                    <div class="d-inline-block p-2 rounded ${msg.message_type === 'user' ? 'bg-primary text-white' : 'bg-light'}">
                                        <strong>${msg.message_type === 'user' ? 'Gebruiker' : 'Bot'}:</strong><br>
                                        ${msg.content}
                                    </div>
                                    <div class="small text-muted mt-1">
                                        ${formatDateTime(msg.timestamp)}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Sluiten</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('chatSessionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('chatSessionModal'));
    modal.show();
}

// Search chat messages
async function searchChatMessages(query) {
    if (query === '') {
        loadChatSessions();
        return;
    }
    
    try {
        showChatLoading();
        const response = await fetch(`/api/chat/search?q=${encodeURIComponent(query)}`);
        const result = await response.json();
        
        if (result.success) {
            displayChatSearchResults(result.data);
            updateChatTableInfo(result.total, query);
        } else {
            showToast('Search error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search error', 'error');
    } finally {
        hideChatLoading();
    }
}

// Display chat search results
function displayChatSearchResults(messages) {
    const tbody = document.getElementById('chat-sessions-table-body');
    tbody.innerHTML = '';
    
    if (messages.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Geen resultaten gevonden</td></tr>';
        return;
    }
    
    messages.forEach((msg, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <code>${msg.session_id.substring(0, 8)}...</code>
            </td>
            <td>${formatDateTime(msg.session_created)}</td>
            <td>${formatDateTime(msg.timestamp)}</td>
            <td>
                <span class="badge ${msg.message_type === 'user' ? 'bg-primary' : 'bg-success'}">
                    ${msg.message_type === 'user' ? 'Gebruiker' : 'Bot'}
                </span>
            </td>
            <td>
                <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${msg.content}
                </div>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-info btn-action" onclick="viewChatSession('${msg.session_id}')" title="Bekijk Chat">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Show chat loading state
function showChatLoading() {
    const tbody = document.getElementById('chat-sessions-table-body');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Laden...</td></tr>';
}

// Hide chat loading state
function hideChatLoading() {
    // Loading state is automatically hidden when data is displayed
}

// Format datetime
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('nl-NL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================
// SYSTEM PROMPT MANAGEMENT FUNCTIONS
// ============================================

let currentPrompts = [];
let activePromptData = null;

// Load all system prompts
async function loadSystemPrompts() {
    try {
        const response = await fetch('/api/system-prompt');
        const result = await response.json();
        
        if (result.success) {
            currentPrompts = result.data;
            displaySystemPrompts(currentPrompts);
        } else {
            showToast('Error loading system prompts: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error loading system prompts:', error);
        showToast('Error loading system prompts', 'error');
    }
}

// Load active system prompt
async function loadActivePrompt() {
    try {
        const response = await fetch('/api/system-prompt/active');
        const result = await response.json();
        
        if (result.success) {
            activePromptData = result.data;
            displayActivePrompt(activePromptData);
        } else {
            document.getElementById('active-prompt-content').textContent = 'Geen actieve prompt gevonden';
            document.getElementById('active-prompt-version').textContent = '-';
            document.getElementById('active-prompt-updated').textContent = '-';
        }
    } catch (error) {
        console.error('Error loading active prompt:', error);
        showToast('Error loading active prompt', 'error');
    }
}

// Display active prompt
function displayActivePrompt(prompt) {
    // Use 'content' field from database (not 'prompt_content')
    document.getElementById('active-prompt-content').textContent = prompt.content || prompt.prompt_content || 'Geen content beschikbaar';
    document.getElementById('active-prompt-version').textContent = prompt.version;
    document.getElementById('active-prompt-updated').textContent = formatDateTime(prompt.updated_at);
}

// Display system prompts in table
function displaySystemPrompts(prompts) {
    const tbody = document.getElementById('prompts-table-body');
    tbody.innerHTML = '';
    
    if (prompts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Geen system prompts gevonden</td></tr>';
        return;
    }
    
    prompts.forEach((prompt, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${prompt.id}</td>
            <td>${prompt.version}</td>
            <td>${formatDateTime(prompt.created_at)}</td>
            <td>${formatDateTime(prompt.updated_at)}</td>
            <td>
                <span class="badge ${prompt.is_active ? 'bg-success' : 'bg-secondary'}">
                    ${prompt.is_active ? 'Actief' : 'Inactief'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-info btn-action" onclick="viewPrompt(${prompt.id})" title="Bekijken">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-primary btn-action" onclick="editPrompt(${prompt.id})" title="Bewerken">
                    <i class="fas fa-edit"></i>
                </button>
                ${!prompt.is_active ? `
                    <button class="btn btn-sm btn-outline-success btn-action" onclick="activatePrompt(${prompt.id})" title="Activeren">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger btn-action" onclick="deletePrompt(${prompt.id})" title="Verwijderen">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

// View prompt details
function viewPrompt(promptId) {
    const prompt = currentPrompts.find(p => p.id === promptId);
    if (!prompt) {
        showToast('Prompt niet gevonden', 'error');
        return;
    }
    
    document.getElementById('view-prompt-version').textContent = prompt.version;
    document.getElementById('view-prompt-created').textContent = formatDateTime(prompt.created_at);
    document.getElementById('view-prompt-updated').textContent = formatDateTime(prompt.updated_at);
    document.getElementById('view-prompt-status').innerHTML = `<span class="badge ${prompt.is_active ? 'bg-success' : 'bg-secondary'}">${prompt.is_active ? 'Actief' : 'Inactief'}</span>`;
    // Use 'content' field from database (not 'prompt_content')
    document.getElementById('view-prompt-content').textContent = prompt.content || prompt.prompt_content || 'Geen content beschikbaar';
    
    const modal = new bootstrap.Modal(document.getElementById('viewPromptModal'));
    modal.show();
}

// Edit prompt
function editPrompt(promptId) {
    const prompt = currentPrompts.find(p => p.id === promptId);
    if (!prompt) {
        showToast('Prompt niet gevonden', 'error');
        return;
    }
    
    document.getElementById('edit-prompt-id').value = prompt.id;
    document.getElementById('edit-prompt-version').value = prompt.version;
    // Use 'content' field from database (not 'prompt_content')
    document.getElementById('edit-prompt-content').value = prompt.content || prompt.prompt_content || '';
    
    const modal = new bootstrap.Modal(document.getElementById('editPromptModal'));
    modal.show();
}

// Edit active prompt (shortcut)
function editActivePrompt() {
    if (activePromptData) {
        editPrompt(activePromptData.id);
    } else {
        showToast('Geen actieve prompt om te bewerken', 'error');
    }
}

// Create new system prompt
async function createSystemPrompt() {
    const form = document.getElementById('create-prompt-form');
    const formData = new FormData(form);
    
    const data = {
        version: formData.get('version'),
        prompt_content: formData.get('prompt_content'),
        is_active: document.getElementById('create-prompt-active').checked
    };
    
    if (!data.version || !data.prompt_content) {
        showToast('Vul alle verplichte velden in', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/system-prompt/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('System prompt succesvol aangemaakt', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createPromptModal')).hide();
            form.reset();
            loadSystemPrompts();
            if (data.is_active) {
                loadActivePrompt();
            }
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error creating system prompt:', error);
        showToast('Error creating system prompt', 'error');
    }
}

// Update system prompt
async function updateSystemPrompt() {
    const promptId = document.getElementById('edit-prompt-id').value;
    const version = document.getElementById('edit-prompt-version').value;
    const promptContent = document.getElementById('edit-prompt-content').value;
    
    if (!version || !promptContent) {
        showToast('Vul alle verplichte velden in', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/system-prompt/update/${promptId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                version: version,
                prompt_content: promptContent
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('System prompt succesvol bijgewerkt', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editPromptModal')).hide();
            loadSystemPrompts();
            loadActivePrompt();
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error updating system prompt:', error);
        showToast('Error updating system prompt', 'error');
    }
}

// Activate system prompt
async function activatePrompt(promptId) {
    if (!confirm('Weet je zeker dat je deze prompt wilt activeren? De huidige actieve prompt wordt gedeactiveerd.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/system-prompt/activate/${promptId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('System prompt succesvol geactiveerd', 'success');
            loadSystemPrompts();
            loadActivePrompt();
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error activating system prompt:', error);
        showToast('Error activating system prompt', 'error');
    }
}

// Delete system prompt
async function deletePrompt(promptId) {
    if (!confirm('Weet je zeker dat je deze prompt wilt verwijderen? Deze actie kan niet ongedaan worden gemaakt.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/system-prompt/delete/${promptId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('System prompt succesvol verwijderd', 'success');
            loadSystemPrompts();
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting system prompt:', error);
        showToast('Error deleting system prompt', 'error');
    }
}

// ============================================
// LIVE LOGS FUNCTIONS
// ============================================

let logStreamActive = false;
let logEventSource = null;
let logLineCount = 0;
const CHATBOT_URL = 'https://irado-chatbot-app.azurewebsites.net';  // Production URL

function startLiveLogs() {
    if (logStreamActive) return;
    
    logStreamActive = true;
    document.getElementById('log-status').textContent = 'Loading...';
    document.getElementById('log-status').className = 'badge bg-warning ms-2';
    document.getElementById('start-logs-btn').disabled = true;
    document.getElementById('stop-logs-btn').disabled = false;
    
    // First, load recent logs
    loadRecentLogs();
    
    // Then start streaming
    startLogStream();
}

async function loadRecentLogs() {
    try {
        const response = await         fetch(`${CHATBOT_URL}/api/logs?lines=100&t=${Date.now()}`, {
            method: 'GET',
            headers: {
                'Authorization': 'Basic aXJhZG86MjBJcmFkbzI1IQ==',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'omit'
        });
        
        const result = await response.json();
        
        if (result.success) {
            const logContent = document.getElementById('log-content');
            logContent.innerHTML = '';
            
            result.logs.forEach(log => {
                appendLogLine(log);
            });
            
            document.getElementById('log-status').textContent = 'Live';
            document.getElementById('log-status').className = 'badge bg-success ms-2';
        }
    } catch (error) {
        console.error('Error loading recent logs:', error);
        showToast('Error loading logs: ' + error.message, 'error');
    }
}

function startLogStream() {
    // Use regular polling instead of SSE (better Azure compatibility)
    let lastLineCount = 0;
    
    function poll() {
        if (!logStreamActive) return;
        
        fetch(`${CHATBOT_URL}/api/logs?lines=200&t=${Date.now()}`, {
            method: 'GET',
            headers: {
                'Authorization': 'Basic aXJhZG86MjBJcmFkbzI1IQ==',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'omit'
        })
        .then(res => res.json())
        .then(result => {
            if (result.success && result.logs.length > 0) {
                // Only append new logs
                const logContent = document.getElementById('log-content');
                const currentLines = logContent.querySelectorAll('.log-line').length;
                
                if (result.logs.length > lastLineCount) {
                    // Clear and re-render all logs to ensure consistency
                    logContent.innerHTML = '';
                    result.logs.forEach(log => appendLogLine(log, false));
                    lastLineCount = result.logs.length;
                }
            }
            
            // Poll every 3 seconds
            if (logStreamActive) {
                setTimeout(poll, 3000);
            }
        })
        .catch(error => {
            console.error('Poll error:', error);
            if (logStreamActive) {
                setTimeout(poll, 5000);  // Retry after 5 sec on error
            }
        });
    }
    
    poll();
}

function stopLiveLogs() {
    logStreamActive = false;
    
    if (logEventSource) {
        logEventSource.close();
        logEventSource = null;
    }
    
    document.getElementById('log-status').textContent = 'Stopped';
    document.getElementById('log-status').className = 'badge bg-secondary ms-2';
    document.getElementById('start-logs-btn').disabled = false;
    document.getElementById('stop-logs-btn').disabled = true;
}

function appendLogLine(logText, shouldScroll = true) {
    const logContent = document.getElementById('log-content');
    const line = document.createElement('div');
    line.className = 'log-line';
    
    // Color coding based on log level
    let color = '#d4d4d4';  // default
    if (logText.includes('ERROR')) {
        color = '#f48771';
    } else if (logText.includes('WARNING')) {
        color = '#dcdcaa';
    } else if (logText.includes('INFO')) {
        color = '#4ec9b0';
    } else if (logText.includes('🔧') || logText.includes('Tool call')) {
        color = '#569cd6';
    } else if (logText.includes('✅')) {
        color = '#4ec9b0';
    } else if (logText.includes('❌')) {
        color = '#f48771';
    }
    
    line.style.color = color;
    line.textContent = logText;
    
    logContent.appendChild(line);
    
    // Update line count
    const currentLines = logContent.querySelectorAll('.log-line').length;
    document.getElementById('log-count').textContent = currentLines + ' lines';
    
    // Auto-scroll if enabled and requested
    if (shouldScroll && document.getElementById('auto-scroll').checked) {
        const container = document.getElementById('log-container');
        container.scrollTop = container.scrollHeight;
    }
    
    // Apply filters
    applyLogFilters();
}

function applyLogFilters() {
    const showError = document.getElementById('filter-error').checked;
    const showWarning = document.getElementById('filter-warning').checked;
    const showInfo = document.getElementById('filter-info').checked;
    const showTool = document.getElementById('filter-tool').checked;
    
    const lines = document.querySelectorAll('.log-line');
    
    lines.forEach(line => {
        const text = line.textContent;
        let show = false;
        
        if (showError && text.includes('ERROR')) show = true;
        if (showWarning && text.includes('WARNING')) show = true;
        if (showInfo && text.includes('INFO')) show = true;
        if (showTool && (text.includes('🔧') || text.includes('Tool call'))) show = true;
        
        // Show lines that don't match any filter if all filters are on
        if (showError && showWarning && showInfo && showTool) {
            show = true;
        }
        
        line.style.display = show ? 'block' : 'none';
    });
}

function clearLogs() {
    document.getElementById('log-content').innerHTML = '<span style="color: #888;">Logs cleared. Click "Start" to begin streaming.</span>';
    document.getElementById('log-count').textContent = '0 lines';
}

function downloadLogs() {
    const logContent = document.getElementById('log-content').innerText;
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chatbot-logs-${new Date().toISOString()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Setup filter checkboxes on page load
document.addEventListener('DOMContentLoaded', function() {
    // Setup filter checkboxes
    const filterIds = ['filter-error', 'filter-warning', 'filter-info', 'filter-tool'];
    filterIds.forEach(id => {
        const elem = document.getElementById(id);
        if (elem) {
            elem.addEventListener('change', applyLogFilters);
        }
    });
    
    // Initialize dashboard logs tab
    document.getElementById('logs-tab').addEventListener('click', function() {
        loadDashboardLogs();
    });
});

// Dashboard Activity Logs Functions
async function loadDashboardLogs() {
    try {
        const logType = document.getElementById('dashboard-log-type').value;
        const url = `/api/dashboard/logs?limit=200${logType ? '&type=' + logType : ''}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            displayDashboardLogs(data.logs);
        } else {
            showToast('Error loading dashboard logs: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading dashboard logs:', error);
        showToast('Error loading dashboard logs', 'error');
    }
}

function displayDashboardLogs(logs) {
    const tbody = document.getElementById('dashboard-logs-table');
    
    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No logs found</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => {
        const timestamp = new Date(log.timestamp).toLocaleString('nl-NL');
        const levelBadge = getLevelBadge(log.level);
        const typeBadge = getTypeBadge(log.log_type);
        
        // Format details if present
        let detailsHtml = '';
        if (log.details) {
            try {
                const details = typeof log.details === 'string' ? JSON.parse(log.details) : log.details;
                detailsHtml = `<br><small class="text-muted">${JSON.stringify(details)}</small>`;
            } catch (e) {
                // Ignore JSON parse errors
            }
        }
        
        return `
            <tr>
                <td><small>${timestamp}</small></td>
                <td>${typeBadge}</td>
                <td><small>${log.action}</small></td>
                <td>${log.message}${detailsHtml}</td>
                <td>${levelBadge}</td>
            </tr>
        `;
    }).join('');
}

function getLevelBadge(level) {
    const badges = {
        'info': '<span class="badge bg-info">ℹ️ Info</span>',
        'warning': '<span class="badge bg-warning">⚠️ Warning</span>',
        'error': '<span class="badge bg-danger">❌ Error</span>'
    };
    return badges[level] || `<span class="badge bg-secondary">${level}</span>`;
}

function getTypeBadge(type) {
    const badges = {
        'CSV_UPLOAD': '<span class="badge bg-primary">📤 CSV</span>',
        'API_CALL': '<span class="badge bg-success">🔌 API</span>',
        'ERROR': '<span class="badge bg-danger">❌ Error</span>',
        'DB_OPERATION': '<span class="badge bg-info">💾 DB</span>'
    };
    return badges[type] || `<span class="badge bg-secondary">${type}</span>`;
}
