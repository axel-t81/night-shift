/**
 * API Client for Night Shift App
 * 
 * This module provides a centralized interface for all API communication.
 * It handles requests to the FastAPI backend and provides error handling.
 * 
 * Base URL: http://localhost:8000/api
 */

// =============================================================================
// Configuration
// =============================================================================

const API_CONFIG = {
    baseURL: '/api',  // Relative URL since frontend is served by same server
    timeout: 10000,   // 10 second timeout
    headers: {
        'Content-Type': 'application/json',
    }
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Make an HTTP request to the API
 * @param {string} endpoint - API endpoint (e.g., '/blocks')
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {object|null} data - Request body data
 * @returns {Promise<object>} Response data
 */
async function request(endpoint, method = 'GET', data = null) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    
    const options = {
        method,
        headers: API_CONFIG.headers,
    };
    
    // Add body for POST/PUT/PATCH requests
    if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        // Handle different status codes
        if (response.status === 204) {
            // No content - successful deletion
            return { success: true };
        }
        
        // Check content type before parsing
        const contentType = response.headers.get('content-type');
        
        // If not JSON, try to get text for better error message
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error(`Non-JSON response from ${endpoint}:`, text.substring(0, 200));
            throw new Error(`Server returned non-JSON response: ${text.substring(0, 100)}`);
        }
        
        // Parse JSON response
        const responseData = await response.json();
        
        // Check if response is OK
        if (!response.ok) {
            throw new Error(responseData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return responseData;
    } catch (error) {
        console.error(`API Error [${method} ${endpoint}]:`, error);
        throw error;
    }
}

// =============================================================================
// Category API Functions
// =============================================================================

const CategoryAPI = {
    /**
     * Get all categories
     * @param {number} skip - Number of records to skip
     * @param {number} limit - Maximum number of records to return
     * @returns {Promise<Array>} List of categories
     */
    async getAll(skip = 0, limit = 100) {
        return request(`/categories?skip=${skip}&limit=${limit}`);
    },
    
    /**
     * Get categories with task counts
     * @returns {Promise<Array>} List of categories with task counts
     */
    async getWithTasks() {
        return request('/categories/with-tasks');
    },
    
    /**
     * Get a single category by ID
     * @param {string} categoryId - Category UUID
     * @returns {Promise<object>} Category object
     */
    async getById(categoryId) {
        return request(`/categories/${categoryId}`);
    },
    
    /**
     * Create a new category
     * @param {object} categoryData - Category data {name, color}
     * @returns {Promise<object>} Created category
     */
    async create(categoryData) {
        return request('/categories', 'POST', categoryData);
    },
    
    /**
     * Update a category
     * @param {string} categoryId - Category UUID
     * @param {object} categoryData - Updated category data
     * @returns {Promise<object>} Updated category
     */
    async update(categoryId, categoryData) {
        return request(`/categories/${categoryId}`, 'PUT', categoryData);
    },
    
    /**
     * Delete a category
     * @param {string} categoryId - Category UUID
     * @returns {Promise<object>} Success response
     */
    async delete(categoryId) {
        return request(`/categories/${categoryId}`, 'DELETE');
    },
    
    /**
     * Get category statistics
     * @param {string} categoryId - Category UUID
     * @returns {Promise<object>} Category statistics
     */
    async getStats(categoryId) {
        return request(`/categories/${categoryId}/stats`);
    }
};

// =============================================================================
// Block API Functions
// =============================================================================

const BlockAPI = {
    /**
     * Get all blocks with optional filters
     * @param {object} filters - Filter options {skip, limit, day_number, order_by}
     * @returns {Promise<Array>} List of blocks
     */
    async getAll(filters = {}) {
        const params = new URLSearchParams();
        if (filters.skip !== undefined) params.append('skip', filters.skip);
        if (filters.limit !== undefined) params.append('limit', filters.limit);
        if (filters.day_number) params.append('day_number', filters.day_number);
        if (filters.order_by) params.append('order_by', filters.order_by);
        
        const queryString = params.toString();
        return request(`/blocks${queryString ? '?' + queryString : ''}`);
    },
    
    /**
     * Get a single block by ID
     * @param {string} blockId - Block UUID
     * @returns {Promise<object>} Block object
     */
    async getById(blockId) {
        return request(`/blocks/${blockId}`);
    },
    
    /**
     * Get a block with all its tasks
     * @param {string} blockId - Block UUID
     * @returns {Promise<object>} Block with tasks
     */
    async getWithTasks(blockId) {
        return request(`/blocks/${blockId}/with-tasks`);
    },
    
    /**
     * Create a new block
     * @param {object} blockData - Block data {start_time, end_time, title, block_number, day_number}
     * @returns {Promise<object>} Created block
     */
    async create(blockData) {
        return request('/blocks', 'POST', blockData);
    },
    
    /**
     * Update a block
     * @param {string} blockId - Block UUID
     * @param {object} blockData - Updated block data
     * @returns {Promise<object>} Updated block
     */
    async update(blockId, blockData) {
        return request(`/blocks/${blockId}`, 'PUT', blockData);
    },
    
    /**
     * Delete a block (and its tasks)
     * @param {string} blockId - Block UUID
     * @returns {Promise<object>} Success response
     */
    async delete(blockId) {
        return request(`/blocks/${blockId}`, 'DELETE');
    },
    
    /**
     * Complete and reset a block for recurrence
     * This is the KEY function for recurring blocks!
     * @param {string} blockId - Block UUID
     * @param {boolean} moveToEnd - Whether to move block to end of queue
     * @returns {Promise<object>} Operation result
     */
    async completeAndReset(blockId, moveToEnd = true) {
        return request(`/blocks/${blockId}/complete-and-reset?move_to_end=${moveToEnd}`, 'POST');
    },
    
    /**
     * Reset all tasks in a block to incomplete
     * @param {string} blockId - Block UUID
     * @returns {Promise<object>} Reset result
     */
    async resetTasks(blockId) {
        return request(`/blocks/${blockId}/reset-tasks`, 'POST');
    },
    
    /**
     * Move a block to the end of the queue
     * @param {string} blockId - Block UUID
     * @returns {Promise<object>} Updated block
     */
    async moveToEnd(blockId) {
        return request(`/blocks/${blockId}/move-to-end`, 'POST');
    },
    
    /**
     * Clone a block
     * @param {string} blockId - Block UUID to clone
     * @param {object} options - Clone options {new_start_time, new_end_time, copy_tasks}
     * @returns {Promise<object>} Cloned block
     */
    async clone(blockId, options = {}) {
        return request(`/blocks/${blockId}/clone`, 'POST', options);
    },
    
    /**
     * Get the next block in the queue
     * @returns {Promise<object>} Next block with progress info
     */
    async getNext() {
        return request('/blocks/next');
    },
    
    /**
     * Get active blocks (with incomplete tasks)
     * @param {number|null} dayNumber - Optional filter by day number
     * @returns {Promise<Array>} List of active blocks
     */
    async getActive(dayNumber = null) {
        const queryString = dayNumber ? `?day_number=${dayNumber}` : '';
        return request(`/blocks/active${queryString}`);
    },
    
    /**
     * Reorder multiple blocks
     * @param {Array} blockOrders - Array of {block_id, block_number} objects
     * @returns {Promise<object>} Success response
     */
    async reorder(blockOrders) {
        return request('/blocks/reorder', 'POST', blockOrders);
    },
    
    /**
     * Get overall block statistics
     * @returns {Promise<object>} Block statistics
     */
    async getStatistics() {
        return request('/blocks/statistics');
    }
};

// =============================================================================
// Task API Functions
// =============================================================================

const TaskAPI = {
    /**
     * Get all tasks with optional filters
     * @param {object} filters - Filter options {skip, limit, completed, block_id, category_id}
     * @returns {Promise<Array>} List of tasks
     */
    async getAll(filters = {}) {
        const params = new URLSearchParams();
        if (filters.skip !== undefined) params.append('skip', filters.skip);
        if (filters.limit !== undefined) params.append('limit', filters.limit);
        if (filters.completed !== undefined) params.append('completed', filters.completed);
        if (filters.block_id) params.append('block_id', filters.block_id);
        if (filters.category_id) params.append('category_id', filters.category_id);
        
        const queryString = params.toString();
        return request(`/tasks${queryString ? '?' + queryString : ''}`);
    },
    
    /**
     * Get a single task by ID
     * @param {string} taskId - Task UUID
     * @returns {Promise<object>} Task object
     */
    async getById(taskId) {
        return request(`/tasks/${taskId}`);
    },
    
    /**
     * Create a new task
     * @param {object} taskData - Task data {block_id, category_id, title, description, estimated_minutes, position}
     * @returns {Promise<object>} Created task
     */
    async create(taskData) {
        return request('/tasks', 'POST', taskData);
    },
    
    /**
     * Update a task
     * @param {string} taskId - Task UUID
     * @param {object} taskData - Updated task data
     * @returns {Promise<object>} Updated task
     */
    async update(taskId, taskData) {
        return request(`/tasks/${taskId}`, 'PUT', taskData);
    },
    
    /**
     * Delete a task
     * @param {string} taskId - Task UUID
     * @returns {Promise<object>} Success response
     */
    async delete(taskId) {
        return request(`/tasks/${taskId}`, 'DELETE');
    },
    
    /**
     * Mark a task as complete
     * @param {string} taskId - Task UUID
     * @param {number|null} actualMinutes - Actual time spent (optional)
     * @returns {Promise<object>} Updated task
     */
    async complete(taskId, actualMinutes = null) {
        const data = actualMinutes !== null ? { actual_minutes: actualMinutes } : {};
        return request(`/tasks/${taskId}/complete`, 'POST', data);
    },
    
    /**
     * Mark a task as incomplete
     * @param {string} taskId - Task UUID
     * @returns {Promise<object>} Updated task
     */
    async uncomplete(taskId) {
        return request(`/tasks/${taskId}/uncomplete`, 'POST');
    },
    
    /**
     * Reorder tasks within a block
     * @param {Array} taskPositions - Array of {task_id, position} objects
     * @returns {Promise<object>} Success response
     */
    async reorder(taskPositions) {
        return request('/tasks/reorder', 'POST', taskPositions);
    },
    
    /**
     * Get all tasks in a block
     * @param {string} blockId - Block UUID
     * @param {boolean} orderByPosition - Whether to order by position
     * @returns {Promise<Array>} List of tasks
     */
    async getByBlock(blockId, orderByPosition = true) {
        return request(`/tasks/block/${blockId}?order_by_position=${orderByPosition}`);
    },
    
    /**
     * Get all tasks in a category
     * @param {string} categoryId - Category UUID
     * @returns {Promise<Array>} List of tasks
     */
    async getByCategory(categoryId) {
        return request(`/tasks/category/${categoryId}`);
    },
    
    /**
     * Get progress for a block
     * @param {string} blockId - Block UUID
     * @returns {Promise<object>} Block progress information
     */
    async getBlockProgress(blockId) {
        return request(`/tasks/block/${blockId}/progress`);
    },
    
    /**
     * Complete multiple tasks at once
     * @param {Array<string>} taskIds - Array of task UUIDs
     * @returns {Promise<object>} Bulk complete result
     */
    async bulkComplete(taskIds) {
        return request('/tasks/bulk-complete', 'POST', { task_ids: taskIds });
    },
    
    /**
     * Uncomplete multiple tasks at once
     * @param {Array<string>} taskIds - Array of task UUIDs
     * @returns {Promise<object>} Bulk uncomplete result
     */
    async bulkUncomplete(taskIds) {
        return request('/tasks/bulk-uncomplete', 'POST', { task_ids: taskIds });
    }
};

// =============================================================================
// Export API modules
// =============================================================================

// Make API modules globally available
window.API = {
    Category: CategoryAPI,
    Block: BlockAPI,
    Task: TaskAPI,
    Quote: {
        async getLatest() {
            return request('/quotes/latest');
        },
        async create(text) {
            return request('/quotes', 'POST', { text });
        }
    }
};

console.log('✓ API Client loaded');

