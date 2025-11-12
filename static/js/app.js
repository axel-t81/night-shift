/**
 * Night Shift App - Main Application Logic
 * 
 * This module handles:
 * - State management
 * - UI rendering
 * - Event handling
 * - Application lifecycle
 */

// =============================================================================
// Application State
// =============================================================================

const AppState = {
    nextBlock: null,           // The next block in queue (most important)
    activeBlocks: [],          // All active blocks (with incomplete tasks)
    selectedBlock: null,       // Currently selected block for viewing
    blockToComplete: null,     // Block pending completion confirmation
    tasks: [],                 // Tasks for the selected block
    categories: [],            // All categories
    blockProgress: null,       // Progress for selected block
    isLoading: false,          // Loading state
    modalMode: 'add',          // Modal mode: 'add' or 'edit'
    editingCategory: null,     // Category being edited (when in edit mode)
    blockModalMode: 'add',     // Block modal mode: 'add' or 'edit'
    editingBlock: null,        // Block being edited (when in edit mode)
    taskModalMode: 'add',      // Task modal mode: 'add' or 'edit'
    editingTask: null          // Task being edited (when in edit mode)
};

const FOCUS_MODAL_ID = 'focus-tracker-modal';
const FOCUS_MODAL_STYLE_ID = 'focus-tracker-modal-styles';
const FOCUS_MODAL_OPTIONS = [
    { id: 'focus-checkbox-1', label: 'Phone, Lights, Ambience' },
    { id: 'focus-checkbox-2', label: 'Track Date & Gap' },
    { id: 'focus-checkbox-3', label: '12-min Warm Up' },
    { id: 'focus-checkbox-4', label: 'Quick Amp Up' },
    { id: 'focus-checkbox-5', label: '12-min Cool Down' }
];
const FOCUS_MODAL_STORAGE_KEY = 'focusModalState';
const FOCUS_CONFETTI_CONTAINER_ID = 'focus-confetti-container';

// =============================================================================
// Initialization
// =============================================================================

/**
 * Initialize the application
 * Called when DOM is loaded
 */
async function init() {
    console.log('🚀 Initializing Night Shift App...');
    
    // Set up event listeners
    setupEventListeners();

    // Add focus modal styles & UI
    injectFocusModalStyles();
    renderFocusModal();
    
    // Start clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Load quote
    loadQuote();
    
    // Load initial data
    await loadAllData();
    
    console.log('✓ Application initialized');
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // Refresh button
    document.getElementById('btn-refresh').addEventListener('click', () => {
        loadAllData();
    });
    
    // Complete block button
    document.getElementById('btn-complete-block').addEventListener('click', () => {
        if (AppState.selectedBlock) {
            showCompleteBlockModal(AppState.selectedBlock.id, AppState.selectedBlock.title);
        }
    });
    
    // Reset tasks button
    document.getElementById('btn-reset-tasks').addEventListener('click', async () => {
        if (AppState.selectedBlock) {
            await handleResetTasks(AppState.selectedBlock.id);
        }
    });
    
    // Edit quote button
    document.getElementById('btn-edit-quote').addEventListener('click', () => {
        showEditQuoteModal();
    });
    
    // Quote modal close
    document.getElementById('quote-modal-close').addEventListener('click', () => {
        hideQuoteModal();
    });
    
    document.getElementById('btn-cancel-quote').addEventListener('click', () => {
        hideQuoteModal();
    });
    
    // Quote form submit
    document.getElementById('form-edit-quote').addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleSaveQuote();
    });
    
    // Click outside quote modal to close
    document.getElementById('quote-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'quote-modal-overlay') {
            hideQuoteModal();
        }
    });
    
    // Add category button
    document.getElementById('btn-add-category').addEventListener('click', () => {
        // Explicitly set to add mode before showing
        AppState.modalMode = 'add';
        showAddCategoryModal();
    });
    
    // Modal close
    document.getElementById('modal-close').addEventListener('click', () => {
        hideModal();
    });
    
    document.getElementById('btn-cancel-category').addEventListener('click', () => {
        hideModal();
    });
    
    // Category form submit
    document.getElementById('form-add-category').addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleAddCategory();
    });
    
    // Click outside modal to close
    document.getElementById('modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'modal-overlay') {
            hideModal();
        }
    });

    // Delete category modal
    document.getElementById('delete-modal-close').addEventListener('click', hideDeleteCategoryModal);
    document.getElementById('btn-cancel-delete').addEventListener('click', hideDeleteCategoryModal);
    document.getElementById('delete-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'delete-modal-overlay') {
            hideDeleteCategoryModal();
        }
    });
    
    // Delete block modal
    document.getElementById('delete-block-modal-close').addEventListener('click', hideDeleteBlockModal);
    document.getElementById('btn-cancel-delete-block').addEventListener('click', hideDeleteBlockModal);
    document.getElementById('delete-block-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'delete-block-modal-overlay') {
            hideDeleteBlockModal();
        }
    });
    
    // Complete block modal
    document.getElementById('complete-block-modal-close').addEventListener('click', hideCompleteBlockModal);
    document.getElementById('btn-cancel-complete-block').addEventListener('click', hideCompleteBlockModal);
    document.getElementById('complete-block-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'complete-block-modal-overlay') {
            hideCompleteBlockModal();
        }
    });
    document.getElementById('btn-confirm-complete-block').addEventListener('click', async () => {
        if (!AppState.blockToComplete) {
            return;
        }
        
        const blockId = AppState.blockToComplete;
        AppState.blockToComplete = null;
        hideCompleteBlockModal();
        await handleCompleteBlock(blockId);
    });
    
    // Delete task modal
    document.getElementById('delete-task-modal-close').addEventListener('click', hideDeleteTaskModal);
    document.getElementById('btn-cancel-delete-task').addEventListener('click', hideDeleteTaskModal);
    document.getElementById('delete-task-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'delete-task-modal-overlay') {
            hideDeleteTaskModal();
        }
    });
    
    // Add block button
    document.getElementById('btn-add-block').addEventListener('click', () => {
        showAddBlockModal();
    });
    
    // Block modal close
    document.getElementById('block-modal-close').addEventListener('click', () => {
        hideBlockModal();
    });
    
    document.getElementById('btn-cancel-block').addEventListener('click', () => {
        hideBlockModal();
    });
    
    // Block form submit
    document.getElementById('form-add-block').addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleAddBlock();
    });
    
    // Click outside block modal to close
    document.getElementById('block-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'block-modal-overlay') {
            hideBlockModal();
        }
    });
    
    // Add task button
    document.getElementById('btn-add-task').addEventListener('click', () => {
        showAddTaskModal();
    });
    
    // Task modal close
    document.getElementById('task-modal-close').addEventListener('click', () => {
        hideTaskModal();
    });
    
    document.getElementById('btn-cancel-task').addEventListener('click', () => {
        hideTaskModal();
    });
    
    // Task form submit
    document.getElementById('form-add-task').addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleAddTask();
    });
    
    // Click outside task modal to close
    document.getElementById('task-modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'task-modal-overlay') {
            hideTaskModal();
        }
    });
}

// =============================================================================
// Data Loading Functions
// =============================================================================

/**
 * Load all initial data
 */
async function loadAllData() {
    setLoadingState(true);
    updateStatus('Loading data...');
    
    try {
        // Load data in parallel for speed
        await Promise.all([
            loadNextBlock(),
            loadActiveBlocks(),
            loadCategories()
        ]);
        
        updateStatus('Ready');
        showNotification('Data loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading data:', error);
        updateStatus('Error');
        showNotification('Failed to load data: ' + error.message, 'error');
    } finally {
        setLoadingState(false);
    }
}

/**
 * Load the next block in queue (highest priority)
 */
async function loadNextBlock() {
    try {
        const response = await API.Block.getNext();
        
        if (response.message) {
            // No blocks available
            AppState.nextBlock = null;
        } else {
            AppState.nextBlock = response;
            // Auto-select the next block
            await selectBlock(response.block.id);
        }
        
        renderNextBlock();
    } catch (error) {
        console.error('Error loading next block:', error);
        throw error;
    }
}

/**
 * Refresh just the next block's progress data (without selecting it)
 * Used when tasks are toggled to update the priority block display
 */
async function refreshNextBlockProgress() {
    try {
        const response = await API.Block.getNext();
        
        if (response.message) {
            // No blocks available
            AppState.nextBlock = null;
        } else {
            AppState.nextBlock = response;
        }
        
        renderNextBlock();
    } catch (error) {
        console.error('Error refreshing next block progress:', error);
        // Don't throw - this is a non-critical UI update
    }
}

/**
 * Load all active blocks (blocks with incomplete tasks)
 */
async function loadActiveBlocks() {
    try {
        AppState.activeBlocks = await API.Block.getActive();
        renderBlockQueue();
    } catch (error) {
        console.error('Error loading active blocks:', error);
        throw error;
    }
}

/**
 * Load all categories
 */
async function loadCategories() {
    try {
        AppState.categories = await API.Category.getWithTasks();
        renderCategories();
        // Re-render areas that depend on category names/colors
        renderBlockQueue();
        renderNextBlock();
        if (AppState.selectedBlock) {
            renderBlockInfo();
            renderTasks();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        throw error;
    }
}

/**
 * Load and display the saved quote
 */
async function loadQuote() {
    const defaultQuote = 'Enter your message or quote of inspiration here.';
    try {
        const latest = await API.Quote.getLatest();
        const quoteElement = document.getElementById('quote-text');
        if (quoteElement) {
            quoteElement.textContent = latest.text || defaultQuote;
        }
    } catch (e) {
        // If no quote or API fails, fall back to default
        const quoteElement = document.getElementById('quote-text');
        if (quoteElement) {
            quoteElement.textContent = defaultQuote;
        }
    }
}

/**
 * Save a new quote
 */
function saveQuote(newQuote) {
    if (newQuote && newQuote.trim()) {
        localStorage.setItem('inspirationalQuote', newQuote.trim());
        loadQuote();
        showNotification('Quote updated successfully', 'success');
    }
}

/**
 * Show the edit quote modal
 */
function showEditQuoteModal() {
    const currentQuote = localStorage.getItem('inspirationalQuote') || 'Enter your message or quote of inspiration here.';
    
    // Pre-fill the textarea with current quote
    document.getElementById('input-quote-text').value = currentQuote;
    
    // Show modal
    document.getElementById('quote-modal-overlay').classList.remove('hidden');
}

/**
 * Hide the edit quote modal
 */
function hideQuoteModal() {
    document.getElementById('quote-modal-overlay').classList.add('hidden');
    
    // Reset form
    document.getElementById('form-edit-quote').reset();
}

/**
 * Handle save quote from modal
 */
async function handleSaveQuote() {
    const quoteInput = document.getElementById('input-quote-text');
    const newQuote = quoteInput.value.trim();
    
    if (!newQuote) {
        showNotification('Quote cannot be empty', 'error');
        return;
    }
    
    try {
        await API.Quote.create(newQuote);
        await loadQuote();
        hideQuoteModal();
    } catch (error) {
        console.error('Error saving quote:', error);
        showNotification('Failed to save quote', 'error');
    }
}

/**
 * Select a block and load its tasks
 * @param {string} blockId - Block UUID
 */
async function selectBlock(blockId) {
    try {
        // Load block details with tasks
        const blockData = await API.Block.getWithTasks(blockId);
        
        AppState.selectedBlock = blockData.block;
        AppState.tasks = blockData.tasks || [];
        
        // Load progress
        AppState.blockProgress = await API.Task.getBlockProgress(blockId);
        
        // Update UI
        renderBlockInfo();
        renderTasks();
        renderProgress();
        
        // Enable/disable action buttons based on block state
        updateActionButtons();
        
    } catch (error) {
        console.error('Error selecting block:', error);
        showNotification('Failed to load block details', 'error');
    }
}

// =============================================================================
// UI Rendering Functions
// =============================================================================

/**
 * Inject styles specific to the focus modal panel
 */
function injectFocusModalStyles() {
    if (document.getElementById(FOCUS_MODAL_STYLE_ID)) {
        return;
    }

    const style = document.createElement('style');
    style.id = FOCUS_MODAL_STYLE_ID;
    style.textContent = `
        #${FOCUS_MODAL_ID} {
            width: 100%;
            margin: 0 0 16px;
            border: 1px solid var(--color-border-accent);
            box-shadow: 0 0 12px rgba(51, 255, 51, 0.18);
            background: linear-gradient(135deg, rgba(10, 10, 10, 0.95), rgba(20, 20, 20, 0.85));
        }

        #${FOCUS_MODAL_ID} .panel-title {
            text-align: center;
            margin-bottom: 0;
        }

        #${FOCUS_MODAL_ID} .panel-content {
            padding: 14px 24px;
        }
        
        .focus-confetti-container {
            position: relative;
            width: 100%;
            height: 0;
            pointer-events: none;
        }
        
        .focus-confetti-container.active {
            height: 120px;
        }
        
        .confetti-particle {
            position: absolute;
            top: 0;
            left: var(--confetti-left, 50%);
            width: 6px;
            height: 12px;
            background: hsl(var(--confetti-hue, 140), 70%, 55%);
            border-radius: 1px;
            opacity: 0;
            transform: rotate(var(--confetti-rotation, 0deg));
            animation: focus-confetti-fall var(--confetti-duration, 1.6s) ease-out var(--confetti-delay, 0s) forwards;
        }
        
        @keyframes focus-confetti-fall {
            0% {
                transform: translate3d(-50%, -20px, 0) rotate(var(--confetti-rotation, 0deg));
                opacity: 1;
            }
            25% {
                opacity: 1;
            }
            100% {
                transform: translate3d(-50%, 100px, 0) rotate(calc(var(--confetti-rotation, 0deg) + 200deg));
                opacity: 0;
            }
        }

        .focus-modal-content {
            display: flex;
            justify-content: space-evenly;
            align-items: flex-start;
            gap: 8px;
        }

        .focus-modal-option {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            text-align: center;
            flex: 1;
        }

        .focus-modal-option.with-divider {
            border-left: 1px solid var(--color-border-accent);
            padding-left: 8px;
            margin-left: 8px;
        }

        .focus-modal-checkbox {
            width: 22px;
            height: 22px;
            border: 2px solid var(--color-border-accent);
            border-radius: 4px;
            background: var(--color-bg-card);
            cursor: pointer;
            accent-color: var(--color-text-primary);
        }

        .focus-modal-label {
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--color-text-secondary);
        }

        @media (max-width: 768px) {
            .focus-modal-content {
                flex-wrap: wrap;
                justify-content: center;
                gap: 12px 24px;
            }
            
            .focus-modal-option.with-divider {
                border-left: none;
                padding-left: 0;
                margin-left: 0;
            }
        }
    `;

    document.head.appendChild(style);
}

/**
 * Render the focus modal above the next block panel
 */
function renderFocusModal() {
    const mainContent = document.querySelector('.main-content');
    const nextBlockPanel = document.querySelector('.next-block-panel');

    if (!mainContent || !nextBlockPanel || document.getElementById(FOCUS_MODAL_ID)) {
        return;
    }

    const modalSection = document.createElement('section');
    modalSection.className = 'panel focus-modal-panel';
    modalSection.id = FOCUS_MODAL_ID;

    const optionsHtml = FOCUS_MODAL_OPTIONS.map((option, index) => `
        <div class="focus-modal-option${index === 4 ? ' with-divider' : ''}">
            <input type="checkbox" id="${option.id}" class="focus-modal-checkbox">
            <label for="${option.id}" class="focus-modal-label">${option.label}</label>
        </div>
    `).join('');

    modalSection.innerHTML = `
        <h2 class="panel-title">&gt; EUDAIMONIA MACHINE</h2>
        <div class="panel-content">
            <div class="focus-modal-content" role="group" aria-label="Focus tracker checkboxes">
                ${optionsHtml}
            </div>
            <div id="${FOCUS_CONFETTI_CONTAINER_ID}" class="focus-confetti-container" aria-hidden="true"></div>
        </div>
    `;

    // Restore saved checkbox states
    const savedFocusState = loadFocusModalState();
    FOCUS_MODAL_OPTIONS.forEach((option) => {
        const checkbox = modalSection.querySelector(`#${option.id}`);
        if (checkbox) {
            checkbox.checked = Boolean(savedFocusState[option.id]);
        }
    });

    // Persist changes on toggle
    modalSection.addEventListener('change', (event) => {
        if (!event.target.classList.contains('focus-modal-checkbox')) {
            return;
        }
        const state = loadFocusModalState();
        state[event.target.id] = event.target.checked;
        saveFocusModalState(state);
        handleFocusCelebration(modalSection);
    });

    // Initial celebration check
    handleFocusCelebration(modalSection, { skipCooldown: true });

    mainContent.insertBefore(modalSection, nextBlockPanel);
}

/**
 * Render the next block (priority block)
 */
function renderNextBlock() {
    const container = document.getElementById('next-block-content');
    
    if (!AppState.nextBlock) {
        container.innerHTML = '<div class="info-text">🎉 No blocks in queue! All caught up.</div>';
        return;
    }
    
    const { block } = AppState.nextBlock;
    
    // Find category for this block
    const category = AppState.categories.find(c => c.id === block.category_id);
    const categoryName = category ? category.name : null;
    const categoryColor = category ? category.color : '#808080';
    
    const html = `
        <div class="next-block-card" data-block-id="${block.id}">
            <div class="block-header">
                <div>
                    <div class="block-title-text">${escapeHtml(block.title)}</div>
                    ${block.description ? `<div class="block-description">${escapeHtml(block.description)}</div>` : ''}
                </div>
                <div class="block-badges">
                    ${categoryName ? `<div class="block-category-badge">${escapeHtml(categoryName)}</div>` : ''}
                    ${block.day_number ? `<div class="block-day-badge">Day ${block.day_number}</div>` : ''}
                    <div class="block-number-badge">#${block.block_number || '?'}</div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

/**
 * Render the blocks queue
 */
function renderBlockQueue() {
    const container = document.getElementById('blocks-queue');
    
    if (AppState.activeBlocks.length === 0) {
        container.innerHTML = '<div class="info-text">No active blocks</div>';
        return;
    }
    
    const html = AppState.activeBlocks.map(block => {
        const isSelected = AppState.selectedBlock && AppState.selectedBlock.id === block.id;
        
        // Find category for this block
        const category = AppState.categories.find(c => c.id === block.category_id);
        const categoryName = category ? category.name : null;
        const categoryColor = category ? category.color : '#808080';
        
        return `
            <div class="block-queue-item ${isSelected ? 'selected' : ''}" 
                 data-block-id="${block.id}"
                 onclick="handleBlockClick('${block.id}')">
                <div class="block-queue-header">
                    <div class="block-queue-title">${escapeHtml(block.title)}</div>
                    <div class="block-queue-right">
                        <div class="block-actions">
                            <button class="btn-icon-sm" onclick="event.stopPropagation(); handleEditBlock('${block.id}')" title="Edit block">✎</button>
                            <button class="btn-icon-sm btn-danger" onclick="event.stopPropagation(); handleDeleteBlock('${block.id}', '${escapeHtml(block.title)}')" title="Delete block">×</button>
                        </div>
                        ${categoryName ? `<div class="block-queue-category" style="background-color: ${categoryColor};">${escapeHtml(categoryName)}</div>` : ''}
                        ${block.day_number ? `<div class="block-queue-day">Day ${block.day_number}</div>` : ''}
                        <div class="block-queue-number">#${block.block_number || '?'}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

/**
 * Render block info panel
 */
function renderBlockInfo() {
    const container = document.getElementById('block-info');
    
    if (!AppState.selectedBlock) {
        container.innerHTML = '<div class="info-text">Select a block to view details</div>';
        return;
    }
    
    const block = AppState.selectedBlock;
    
    const html = `
        <div class="stat-row">
            <span class="stat-name">Title:</span>
            <span class="stat-data">${escapeHtml(block.title)}</span>
        </div>
        ${block.description ? `
        <div class="stat-row">
            <span class="stat-name">Description:</span>
            <span class="stat-data">${escapeHtml(block.description)}</span>
        </div>
        ` : ''}
        <div class="stat-row">
            <span class="stat-name">Day:</span>
            <span class="stat-data">${block.day_number || 'N/A'}</span>
        </div>
        <div class="stat-row">
            <span class="stat-name">Block #:</span>
            <span class="stat-data">${block.block_number || 'N/A'}</span>
        </div>
        <div class="stat-row">
            <span class="stat-name">Created:</span>
            <span class="stat-data">${formatDateTime(block.created_at)}</span>
        </div>
        <div class="stat-row">
            <span class="stat-name">Last Completed:</span>
            <span class="stat-data">${block.last_completed_at ? formatDateTime(block.last_completed_at) : 'Never'}</span>
        </div>
    `;
    
    container.innerHTML = html;
}

/**
 * Render tasks list
 */
function renderTasks() {
    const container = document.getElementById('tasks-list');
    
    if (AppState.tasks.length === 0) {
        container.innerHTML = '<div class="info-text">No tasks in this block</div>';
        return;
    }
    
    const html = AppState.tasks.map(task => {
        // Find category for this task
        const category = AppState.categories.find(c => c.id === task.category_id);
        const categoryName = category ? category.name : 'Unknown';
        const categoryColor = category ? category.color : '#808080';
        
        return `
            <div class="task-item ${task.completed ? 'completed' : ''}" data-task-id="${task.id}">
                <input type="checkbox" 
                       class="task-checkbox" 
                       ${task.completed ? 'checked' : ''}
                       onchange="handleTaskToggle('${task.id}', this.checked)">
                <div class="task-content">
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                    <div class="task-meta">
                        <span class="task-category" style="background-color: ${categoryColor}20; color: ${categoryColor};">
                            ${escapeHtml(categoryName)}
                        </span>
                        <span>⏱ ${task.estimated_minutes} min</span>
                        ${task.completed && task.actual_minutes ? `<span>✓ ${task.actual_minutes} min</span>` : ''}
                        ${task.completed_at ? `<span>📅 ${formatDateTime(task.completed_at)}</span>` : ''}
                    </div>
                </div>
                <div class="task-actions">
                    <button class="btn-icon-sm" onclick="handleEditTask('${task.id}')" title="Edit task">✎</button>
                    <button class="btn-icon-sm btn-danger" onclick="handleDeleteTask('${task.id}', '${escapeHtml(task.title)}')" title="Delete task">×</button>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

/**
 * Render progress panel
 */
function renderProgress() {
    if (!AppState.blockProgress) {
        return;
    }
    
    const progress = AppState.blockProgress;
    
    // Update progress bar
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${progress.completion_percentage}%`;
    
    // Update progress text
    document.getElementById('progress-percentage').textContent = 
        `${progress.completion_percentage.toFixed(0)}%`;
    
    // Update progress stats
    document.getElementById('progress-completed').textContent = progress.completed_tasks;
    document.getElementById('progress-remaining').textContent = 
        progress.total_tasks - progress.completed_tasks;
    document.getElementById('progress-time').textContent = 
        `${progress.remaining_estimated_minutes} min`;
}

/**
 * Render categories list
 */
function renderCategories() {
    const container = document.getElementById('categories-list');
    
    if (AppState.categories.length === 0) {
        container.innerHTML = '<div class="info-text">No categories</div>';
        return;
    }
    
    const html = AppState.categories.map(category => {
        const color = category.color || '#808080';
        return `
            <div class="category-item">
                <div class="category-color" style="background-color: ${color};"></div>
                <div class="category-name">${escapeHtml(category.name)}</div>
                <div class="category-actions">
                    <button class="btn-icon-sm" onclick="handleEditCategory('${category.id}')" title="Edit category">✎</button>
                    <button class="btn-icon-sm btn-danger" onclick="handleDeleteCategory('${category.id}', '${escapeHtml(category.name)}')" title="Delete category">×</button>
                </div>
                <div class="category-count">${category.total_tasks || 0}</div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// Statistics rendering removed - replaced with Quote of the Moment panel

// =============================================================================
// Event Handlers
// =============================================================================

/**
 * Handle block click in queue
 * @param {string} blockId - Block UUID
 */
async function handleBlockClick(blockId) {
    await selectBlock(blockId);
}

/**
 * Handle task checkbox toggle
 * @param {string} taskId - Task UUID
 * @param {boolean} checked - New checked state
 */
async function handleTaskToggle(taskId, checked) {
    try {
        if (checked) {
            // Complete the task
            await API.Task.complete(taskId);
            showNotification('Task completed! ✓', 'success');
        } else {
            // Uncomplete the task
            await API.Task.uncomplete(taskId);
            showNotification('Task marked incomplete', 'info');
        }
        
        // Reload selected block to update UI and refresh next block progress in parallel
        await Promise.all([
            AppState.selectedBlock ? selectBlock(AppState.selectedBlock.id) : Promise.resolve(),
            refreshNextBlockProgress()
        ]);
        
    } catch (error) {
        console.error('Error toggling task:', error);
        showNotification('Failed to update task', 'error');
        // Revert checkbox state on error
        const checkbox = document.querySelector(`[data-task-id="${taskId}"] .task-checkbox`);
        if (checkbox) {
            checkbox.checked = !checked;
        }
    }
}

/**
 * Handle complete block button
 * This triggers the complete-and-reset flow for recurring blocks
 * @param {string} blockId - Block UUID
 */
async function handleCompleteBlock(blockId) {
    try {
        updateStatus('Completing block...');
        
        // Call the complete-and-reset endpoint
        const result = await API.Block.completeAndReset(blockId, true);
        
        showNotification(
            `Block completed! ${result.tasks_completed} tasks done. Block moved to position #${result.new_block_number}`, 
            'success'
        );
        
        // Reload all data to reflect changes
        await loadAllData();
        
    } catch (error) {
        console.error('Error completing block:', error);
        showNotification('Failed to complete block: ' + error.message, 'error');
        updateStatus('Error');
    }
}

/**
 * Handle reset tasks button
 * @param {string} blockId - Block UUID
 */
async function handleResetTasks(blockId) {
    if (!confirm('Reset all tasks in this block to incomplete?')) {
        return;
    }
    
    try {
        updateStatus('Resetting tasks...');
        
        const result = await API.Block.resetTasks(blockId);
        
        showNotification(`${result.tasks_reset} tasks reset to incomplete`, 'info');
        
        // Reload selected block
        await selectBlock(blockId);
        
        updateStatus('Ready');
    } catch (error) {
        console.error('Error resetting tasks:', error);
        showNotification('Failed to reset tasks', 'error');
        updateStatus('Error');
    }
}

/**
 * Handle add/edit category form submission
 */
async function handleAddCategory() {
    const nameInput = document.getElementById('input-category-name');
    const colorInput = document.getElementById('input-category-color');
    
    const name = nameInput.value.trim();
    const color = colorInput.value.trim() || null;
    
    if (!name) {
        showNotification('Category name is required', 'error');
        return;
    }
    
    try {
        if (AppState.modalMode === 'edit' && AppState.editingCategory) {
            // Update existing category
            await API.Category.update(AppState.editingCategory.id, { name, color });
            showNotification('Category updated successfully', 'success');
        } else {
            // Create new category
            await API.Category.create({ name, color });
            showNotification('Category created successfully', 'success');
        }
        
        // Reset form and close modal
        nameInput.value = '';
        colorInput.value = '';
        hideModal();
        
        // Reload categories
        await loadCategories();
        
    } catch (error) {
        console.error('Error saving category:', error);
        showNotification('Failed to save category: ' + error.message, 'error');
    }
}

/**
 * Handle edit category button click
 * @param {string} categoryId - Category UUID
 */
async function handleEditCategory(categoryId) {
    try {
        // Find the category in our current list
        const category = AppState.categories.find(c => c.id === categoryId);
        
        if (!category) {
            showNotification('Category not found', 'error');
            return;
        }
        
        // Set modal to edit mode
        AppState.modalMode = 'edit';
        AppState.editingCategory = category;
        
        // Pre-fill the form
        document.getElementById('input-category-name').value = category.name;
        document.getElementById('input-category-color').value = category.color || '';
        
        // Update modal title and button
        document.querySelector('.modal-title').textContent = 'Edit Category';
        document.querySelector('#form-add-category button[type="submit"]').textContent = 'Update';
        
        // Show modal
        showAddCategoryModal();
        
    } catch (error) {
        console.error('Error loading category for edit:', error);
        showNotification('Failed to load category', 'error');
    }
}

/**
 * Handle delete category button click
 * @param {string} categoryId - Category UUID
 * @param {string} categoryName - Category name for confirmation
 */
async function handleDeleteCategory(categoryId, categoryName) {
    showDeleteCategoryModal(categoryId, categoryName);
}

// =============================================================================
// UI Helper Functions
// =============================================================================

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    const container = document.getElementById('notifications');
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Update status in header and footer
 * @param {string} status - Status message
 */
function updateStatus(status) {
    document.getElementById('stat-status').textContent = status;
    document.getElementById('footer-status').textContent = status;
}

/**
 * Set loading state
 * @param {boolean} isLoading - Loading state
 */
function setLoadingState(isLoading) {
    AppState.isLoading = isLoading;
    // Could add loading spinner here
}

/**
 * Update action buttons based on current state
 */
function updateActionButtons() {
    const completeBtn = document.getElementById('btn-complete-block');
    const resetBtn = document.getElementById('btn-reset-tasks');
    
    const hasSelectedBlock = AppState.selectedBlock !== null;
    const hasTasks = AppState.tasks.length > 0;
    
    completeBtn.disabled = !hasSelectedBlock || !hasTasks;
    resetBtn.disabled = !hasSelectedBlock || !hasTasks;
}

/**
 * Show the delete category confirmation modal
 * @param {string} categoryId - The ID of the category to delete
 * @param {string} categoryName - The name of the category for the confirmation message
 */
function showDeleteCategoryModal(categoryId, categoryName) {
    const deleteModalOverlay = document.getElementById('delete-modal-overlay');
    const deleteCategoryName = document.getElementById('delete-category-name');
    const btnConfirmDelete = document.getElementById('btn-confirm-delete');

    deleteCategoryName.textContent = categoryName;

    // This ensures we don't stack event listeners
    const newBtn = btnConfirmDelete.cloneNode(true);
    btnConfirmDelete.parentNode.replaceChild(newBtn, btnConfirmDelete);

    newBtn.addEventListener('click', async () => {
        hideDeleteCategoryModal();
        try {
            updateStatus('Deleting category...');
            await API.Category.delete(categoryId);
            showNotification('Category deleted successfully', 'success');
            
            // Reload data
            await loadCategories();
            await loadActiveBlocks();
            
        } catch (error) {
            console.error('Error deleting category:', error);
            if (error.message.includes('tasks still reference it') || error.message.includes('Cannot delete')) {
                showNotification('Cannot delete category: It still has tasks assigned to it. Please delete or reassign them first.', 'error');
            } else {
                showNotification('Failed to delete category: ' + error.message, 'error');
            }
        } finally {
            updateStatus('Ready');
        }
    });

    deleteModalOverlay.classList.remove('hidden');
}

/**
 * Hide the delete category confirmation modal
 */
function hideDeleteCategoryModal() {
    const deleteModalOverlay = document.getElementById('delete-modal-overlay');
    deleteModalOverlay.classList.add('hidden');
}

/**
 * Show add block modal
 */
function showAddBlockModal() {
    // Only reset if not in edit mode
    if (AppState.blockModalMode !== 'edit') {
        AppState.blockModalMode = 'add';
        AppState.editingBlock = null;
        
        document.getElementById('form-add-block').reset();
        
        // Update modal title and button
        document.querySelector('#block-modal-overlay .modal-title').textContent = 'Add Block';
        document.querySelector('#form-add-block button[type="submit"]').textContent = 'Create Block';
    }
    
    // Populate category dropdown
    populateBlockCategoryDropdown();
    
    // Show modal
    document.getElementById('block-modal-overlay').classList.remove('hidden');
}

/**
 * Populate the category dropdown in the block modal
 */
function populateBlockCategoryDropdown() {
    const select = document.getElementById('input-block-category');
    
    // Clear existing options except the first one (placeholder)
    select.innerHTML = '<option value="">-- Select Category (Optional) --</option>';
    
    // Add categories
    AppState.categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

/**
 * Hide block modal
 */
function hideBlockModal() {
    document.getElementById('block-modal-overlay').classList.add('hidden');
    
    // Reset form and state
    document.getElementById('form-add-block').reset();
    AppState.blockModalMode = 'add';
    AppState.editingBlock = null;
}

/**
 * Handle add/edit block form submission
 */
async function handleAddBlock() {
    const titleInput = document.getElementById('input-block-title');
    const descriptionInput = document.getElementById('input-block-description');
    const dayNumberInput = document.getElementById('input-block-day-number');
    const blockNumberInput = document.getElementById('input-block-number');
    const categorySelect = document.getElementById('input-block-category');
    
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim() || null;
    const dayNumber = dayNumberInput.value ? parseInt(dayNumberInput.value) : null;
    const blockNumber = blockNumberInput.value ? parseInt(blockNumberInput.value) : null;
    const categoryId = categorySelect.value || null;
    
    // Validate required fields
    if (!title) {
        showNotification('Block title is required', 'error');
        return;
    }

    if (!blockNumber) {
        showNotification('Block number is required', 'error');
        return;
    }

    if (!dayNumber) {
        showNotification('Day number is required', 'error');
        return;
    }
    
    try {
        // Prepare block data
        const blockData = {};
        
        // Add fields to update (only changed fields for edit)
        if (title) blockData.title = title;
        if (description !== null) blockData.description = description;
        if (dayNumber !== null) blockData.day_number = dayNumber;
        if (blockNumber !== null) blockData.block_number = blockNumber;
        if (categoryId !== null) blockData.category_id = categoryId;
        
        if (AppState.blockModalMode === 'edit' && AppState.editingBlock) {
            // Update existing block
            updateStatus('Updating block...');
            await API.Block.update(AppState.editingBlock.id, blockData);
            showNotification('Block updated successfully!', 'success');
        } else {
            // Create new block
            updateStatus('Creating block...');
            await API.Block.create(blockData);
            showNotification('Block created successfully!', 'success');
        }
        
        // Close modal and reset form
        hideBlockModal();
        
        // Reload data to show changes
        await Promise.all([
            loadActiveBlocks(),
            loadNextBlock()
        ]);
        
        updateStatus('Ready');
        
    } catch (error) {
        console.error('Error saving block:', error);
        showNotification('Failed to save block: ' + error.message, 'error');
        updateStatus('Error');
    }
}

/**
 * Handle edit block button click
 * @param {string} blockId - Block UUID
 */
async function handleEditBlock(blockId) {
    try {
        // Load the full block data
        const block = await API.Block.getById(blockId);
        
        if (!block) {
            showNotification('Block not found', 'error');
            return;
        }
        
        // Set modal to edit mode
        AppState.blockModalMode = 'edit';
        AppState.editingBlock = block;
        
        // Pre-fill the form
        document.getElementById('input-block-title').value = block.title || '';
        document.getElementById('input-block-description').value = block.description || '';
        document.getElementById('input-block-day-number').value = block.day_number || '';
        document.getElementById('input-block-number').value = block.block_number || '';
        
        // Populate category dropdown first
        populateBlockCategoryDropdown();
        
        // Set selected category
        document.getElementById('input-block-category').value = block.category_id || '';
        
        // Update modal title and button
        document.querySelector('#block-modal-overlay .modal-title').textContent = 'Edit Block';
        document.querySelector('#form-add-block button[type="submit"]').textContent = 'Update Block';
        
        // Show modal
        showAddBlockModal();
        
    } catch (error) {
        console.error('Error loading block for edit:', error);
        showNotification('Failed to load block', 'error');
    }
}

/**
 * Handle delete block button click
 * @param {string} blockId - Block UUID
 * @param {string} blockTitle - Block title for confirmation
 */
async function handleDeleteBlock(blockId, blockTitle) {
    showDeleteBlockModal(blockId, blockTitle);
}

/**
 * Show the delete block confirmation modal
 * @param {string} blockId - The ID of the block to delete
 * @param {string} blockTitle - The title of the block for the confirmation message
 */
function showDeleteBlockModal(blockId, blockTitle) {
    const deleteModalOverlay = document.getElementById('delete-block-modal-overlay');
    const deleteBlockName = document.getElementById('delete-block-name');
    const btnConfirmDelete = document.getElementById('btn-confirm-delete-block');

    deleteBlockName.textContent = blockTitle;

    // Replace button to avoid stacking event listeners
    const newBtn = btnConfirmDelete.cloneNode(true);
    btnConfirmDelete.parentNode.replaceChild(newBtn, btnConfirmDelete);

    newBtn.addEventListener('click', async () => {
        hideDeleteBlockModal();
        try {
            updateStatus('Deleting block...');
            await API.Block.delete(blockId);
            showNotification('Block deleted successfully', 'success');
            
            // Reload data
            await Promise.all([
                loadActiveBlocks(),
                loadStatistics(),
                loadNextBlock()
            ]);
            
        } catch (error) {
            console.error('Error deleting block:', error);
            showNotification('Failed to delete block: ' + error.message, 'error');
        } finally {
            updateStatus('Ready');
        }
    });

    deleteModalOverlay.classList.remove('hidden');
}

/**
 * Hide the delete block confirmation modal
 */
function hideDeleteBlockModal() {
    const deleteModalOverlay = document.getElementById('delete-block-modal-overlay');
    deleteModalOverlay.classList.add('hidden');
}

/**
 * Show the complete block confirmation modal
 * @param {string} blockId - The ID of the block to complete
 * @param {string} blockTitle - The title of the block for the confirmation message
 */
function showCompleteBlockModal(blockId, blockTitle) {
    AppState.blockToComplete = blockId;
    
    const completeModalOverlay = document.getElementById('complete-block-modal-overlay');
    const completeBlockName = document.getElementById('complete-block-name');
    
    completeBlockName.textContent = blockTitle || 'this block';
    completeModalOverlay.classList.remove('hidden');
}

/**
 * Hide the complete block confirmation modal
 */
function hideCompleteBlockModal() {
    const completeModalOverlay = document.getElementById('complete-block-modal-overlay');
    completeModalOverlay.classList.add('hidden');
    AppState.blockToComplete = null;
}

/**
 * Trigger a celebratory animation when all focus checkboxes are checked
 * @param {HTMLElement} modalSection - The focus modal section element
 * @param {Object} options - Additional options
 * @param {boolean} options.skipCooldown - If true, bypass the cooldown check
 */
function handleFocusCelebration(modalSection, { skipCooldown = false } = {}) {
    const checkboxes = [...modalSection.querySelectorAll('.focus-modal-checkbox')];
    const totalChecked = checkboxes.filter((checkbox) => checkbox.checked).length;
    const confettiContainer = modalSection.querySelector(`#${FOCUS_CONFETTI_CONTAINER_ID}`);
    
    if (totalChecked !== FOCUS_MODAL_OPTIONS.length || !confettiContainer) {
        return;
    }
    
    const now = Date.now();
    const lastCelebrated = Number(localStorage.getItem('focusModalCelebratedAt') || 0);
    const oneMinute = 60 * 1000;
    if (!skipCooldown && now - lastCelebrated < oneMinute) {
        return;
    }
    
    localStorage.setItem('focusModalCelebratedAt', String(now));
    
    spawnConfetti(confettiContainer, {
        particleCount: 24,
        duration: 1200
    });
}

/**
 * Spawn confetti particles inside a container
 * @param {HTMLElement} container - Container element to host confetti
 * @param {Object} options - Confetti options
 * @param {number} options.particleCount - Number of particles to create
 * @param {number} options.duration - Duration of the animation in ms
 */
function spawnConfetti(container, { particleCount = 20, duration = 1500 } = {}) {
    container.classList.add('active');
    const particles = [];
    
    for (let i = 0; i < particleCount; i += 1) {
        const particle = document.createElement('span');
        particle.className = 'confetti-particle';
        
        // Randomize initial position and properties
        particle.style.setProperty('--confetti-left', `${Math.random() * 100}%`);
        particle.style.setProperty('--confetti-rotation', `${Math.random() * 360}deg`);
        particle.style.setProperty('--confetti-delay', `${Math.random() * 0.3}s`);
        particle.style.setProperty('--confetti-duration', `${duration / 1000 + Math.random() * 0.5}s`);
        particle.style.setProperty('--confetti-hue', `${Math.floor(Math.random() * 360)}`);
        
        particles.push(particle);
        container.appendChild(particle);
    }
    
    setTimeout(() => {
        particles.forEach((particle) => particle.remove());
        container.classList.remove('active');
    }, duration + 500);
}


/**
 * Show add category modal
 */
function showAddCategoryModal() {
    // Only reset if not in edit mode
    if (AppState.modalMode !== 'edit') {
        AppState.modalMode = 'add';
        AppState.editingCategory = null;
        
        document.getElementById('input-category-name').value = '';
        document.getElementById('input-category-color').value = '';
        
        document.querySelector('.modal-title').textContent = 'Add Category';
        document.querySelector('#form-add-category button[type="submit"]').textContent = 'Create';
    }
    
    // Show modal
    document.getElementById('modal-overlay').classList.remove('hidden');
}

/**
 * Hide modal
 */
function hideModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
    
    // Reset state
    AppState.modalMode = 'add';
    AppState.editingCategory = null;
}

/**
 * Show add task modal
 */
async function showAddTaskModal() {
    // Only reset if not in edit mode
    if (AppState.taskModalMode !== 'edit') {
        AppState.taskModalMode = 'add';
        AppState.editingTask = null;
        
        document.getElementById('form-add-task').reset();
        
        // Update modal title and button
        document.querySelector('#task-modal-overlay .modal-title').textContent = 'Add Task';
        document.querySelector('#form-add-task button[type="submit"]').textContent = 'Create Task';
    }
    
    // Populate block dropdown with all blocks
    await populateTaskBlockDropdown();
    
    // Show modal
    document.getElementById('task-modal-overlay').classList.remove('hidden');
}

/**
 * Hide task modal
 */
function hideTaskModal() {
    document.getElementById('task-modal-overlay').classList.add('hidden');
    
    // Reset form and state
    document.getElementById('form-add-task').reset();
    AppState.taskModalMode = 'add';
    AppState.editingTask = null;
}

/**
 * Populate the block dropdown in the task modal with ALL blocks
 */
async function populateTaskBlockDropdown() {
    const select = document.getElementById('input-task-block');
    
    // Clear existing options except the first one (placeholder)
    select.innerHTML = '<option value="">-- Select Block --</option>';
    
    try {
        // Fetch all blocks
        const blocks = await API.Block.getAll();
        
        // Sort by day_number, then block_number
        blocks.sort((a, b) => (a.day_number || 0) - (b.day_number || 0) || (a.block_number || 0) - (b.block_number || 0));
        
        // Add blocks to dropdown
        blocks.forEach(block => {
            const option = document.createElement('option');
            option.value = block.id;
            option.textContent = `Day ${block.day_number || '?'} | #${block.block_number || '?'} - ${block.title}`;
            select.appendChild(option);
        });
        
        if (blocks.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = '(No blocks available - create a block first)';
            option.disabled = true;
            select.appendChild(option);
        }
        
    } catch (error) {
        console.error('Error loading blocks for dropdown:', error);
        showNotification('Failed to load blocks', 'error');
    }
}

/**
 * Handle add/edit task form submission
 */
async function handleAddTask() {
    const blockSelect = document.getElementById('input-task-block');
    const titleInput = document.getElementById('input-task-title');
    const descriptionInput = document.getElementById('input-task-description');
    const estimatedMinutesInput = document.getElementById('input-task-estimated-minutes');
    const positionInput = document.getElementById('input-task-position');
    
    const blockId = blockSelect.value;
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim() || null;
    const estimatedMinutes = parseInt(estimatedMinutesInput.value);
    const position = parseInt(positionInput.value) || 0;
    
    // Validate required fields
    if (!blockId) {
        showNotification('Please select a block', 'error');
        return;
    }
    
    if (!title) {
        showNotification('Task title is required', 'error');
        return;
    }
    
    if (!estimatedMinutes || estimatedMinutes <= 0) {
        showNotification('Estimated minutes must be a positive number', 'error');
        return;
    }
    
    try {
        // Prepare task data
        const taskData = {};
        
         if (blockId) taskData.block_id = blockId;
        if (title) taskData.title = title;
        if (description !== null) taskData.description = description;
        if (estimatedMinutes) taskData.estimated_minutes = estimatedMinutes;
        if (position !== null) taskData.position = position;
        
        if (AppState.taskModalMode === 'edit' && AppState.editingTask) {
            // Update existing task
            updateStatus('Updating task...');
            await API.Task.update(AppState.editingTask.id, taskData);
            showNotification('Task updated successfully!', 'success');
        } else {
            // Create new task
            updateStatus('Creating task...');
            await API.Task.create(taskData);
            showNotification('Task created successfully!', 'success');
        }
        
        // Close modal and reset form
        hideTaskModal();
        
        // Reload data to show changes
        await Promise.all([
            loadActiveBlocks(),
            loadNextBlock()
        ]);
        
        // If the block we're working with is currently selected, reload its tasks
        if (AppState.selectedBlock && AppState.selectedBlock.id === blockId) {
            await selectBlock(blockId);
        }
        
        updateStatus('Ready');
        
    } catch (error) {
        console.error('Error saving task:', error);
        showNotification('Failed to save task: ' + error.message, 'error');
        updateStatus('Error');
    }
}

/**
 * Handle edit task button click
 * @param {string} taskId - Task UUID
 */
async function handleEditTask(taskId) {
    try {
        // Find the task in our current list first
        let task = AppState.tasks.find(t => t.id === taskId);
        
        // If not found in current block, fetch it
        if (!task) {
            task = await API.Task.getById(taskId);
        }
        
        if (!task) {
            showNotification('Task not found', 'error');
            return;
        }
        
        // Set modal to edit mode
        AppState.taskModalMode = 'edit';
        AppState.editingTask = task;
        
        // Populate block dropdown first
        await populateTaskBlockDropdown();
        
        // Pre-fill the form
        document.getElementById('input-task-block').value = task.block_id || '';
        document.getElementById('input-task-title').value = task.title || '';
        document.getElementById('input-task-description').value = task.description || '';
        document.getElementById('input-task-estimated-minutes').value = task.estimated_minutes || '';
        document.getElementById('input-task-position').value = task.position || 0;
        
        // Update modal title and button
        document.querySelector('#task-modal-overlay .modal-title').textContent = 'Edit Task';
        document.querySelector('#form-add-task button[type="submit"]').textContent = 'Update Task';
        
        // Show modal
        await showAddTaskModal();
        
    } catch (error) {
        console.error('Error loading task for edit:', error);
        showNotification('Failed to load task', 'error');
    }
}

/**
 * Handle delete task button click
 * @param {string} taskId - Task UUID
 * @param {string} taskTitle - Task title for confirmation
 */
async function handleDeleteTask(taskId, taskTitle) {
    showDeleteTaskModal(taskId, taskTitle);
}

/**
 * Show the delete task confirmation modal
 * @param {string} taskId - The ID of the task to delete
 * @param {string} taskTitle - The title of the task for the confirmation message
 */
function showDeleteTaskModal(taskId, taskTitle) {
    const deleteModalOverlay = document.getElementById('delete-task-modal-overlay');
    const deleteTaskName = document.getElementById('delete-task-name');
    const btnConfirmDelete = document.getElementById('btn-confirm-delete-task');

    deleteTaskName.textContent = taskTitle;

    // Replace button to avoid stacking event listeners
    const newBtn = btnConfirmDelete.cloneNode(true);
    btnConfirmDelete.parentNode.replaceChild(newBtn, btnConfirmDelete);

    newBtn.addEventListener('click', async () => {
        hideDeleteTaskModal();
        try {
            updateStatus('Deleting task...');
            await API.Task.delete(taskId);
            showNotification('Task deleted successfully', 'success');
            
            // Reload data
            await Promise.all([
                loadActiveBlocks(),
                loadStatistics(),
                loadNextBlock()
            ]);
            
            // If we have a selected block, reload its tasks
            if (AppState.selectedBlock) {
                await selectBlock(AppState.selectedBlock.id);
            }
            
        } catch (error) {
            console.error('Error deleting task:', error);
            showNotification('Failed to delete task: ' + error.message, 'error');
        } finally {
            updateStatus('Ready');
        }
    });

    deleteModalOverlay.classList.remove('hidden');
}

/**
 * Hide the delete task confirmation modal
 */
function hideDeleteTaskModal() {
    const deleteModalOverlay = document.getElementById('delete-task-modal-overlay');
    deleteModalOverlay.classList.add('hidden');
}

/**
 * Update clock in footer
 */
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('footer-time').textContent = timeString;
}

/**
 * Load the persisted focus modal checkbox state
 * @returns {Object<string, boolean>} Focus checkbox state map
 */
function loadFocusModalState() {
    try {
        const raw = localStorage.getItem(FOCUS_MODAL_STORAGE_KEY);
        if (!raw) {
            return {};
        }
        const parsed = JSON.parse(raw);
        return typeof parsed === 'object' && parsed !== null ? parsed : {};
    } catch (error) {
        console.warn('Unable to read focus modal state from storage:', error);
        return {};
    }
}

/**
 * Persist the focus modal checkbox state
 * @param {Object<string, boolean>} state - Focus checkbox state map
 */
function saveFocusModalState(state) {
    try {
        localStorage.setItem(FOCUS_MODAL_STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
        console.warn('Unable to save focus modal state to storage:', error);
    }
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format datetime string
 * @param {string} datetime - ISO datetime string
 * @returns {string} Formatted datetime
 */
function formatDateTime(datetime) {
    if (!datetime) return 'N/A';
    const date = new Date(datetime);
    return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/**
 * Format time only
 * @param {string} datetime - ISO datetime string
 * @returns {string} Formatted time
 */
function formatTime(datetime) {
    if (!datetime) return 'N/A';
    const date = new Date(datetime);
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
    });
}

// =============================================================================
// Application Startup
// =============================================================================

// Initialize app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

console.log('✓ App.js loaded');

