<template>
  <div class="tasks-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1><el-icon><Document /></el-icon> Tasks</h1>
        <p>Manage and track your tasks</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true" round>
        <el-icon><Plus /></el-icon>
        New Task
      </el-button>
    </div>

    <!-- Filters -->
    <el-card class="filters-card">
      <div class="filters-row">
        <el-input v-model="filters.search" placeholder="Search tasks..." clearable style="width: 240px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filters.status" placeholder="Status" clearable style="width: 140px">
          <el-option label="To Do" value="todo" />
          <el-option label="In Progress" value="in-progress" />
          <el-option label="Done" value="done" />
        </el-select>
        <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 140px">
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <el-select v-model="filters.project_id" placeholder="Project" clearable style="width: 180px">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
    </el-card>

    <!-- Tasks List -->
    <div v-loading="loading" class="tasks-list">
      <div v-if="filteredTasks.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <el-icon size="64"><Document /></el-icon>
        </div>
        <h3>No tasks found</h3>
        <p>Create a new task or adjust your filters</p>
      </div>

      <div v-for="task in filteredTasks" :key="task.id" class="task-card" @click="$router.push(`/tasks/${task.id}`)">
        <div class="task-priority-bar" :class="task.priority"></div>
        <div class="task-content">
          <div class="task-header">
            <h3>{{ task.title }}</h3>
            <el-tag :type="getStatusType(task.status)" size="small" effect="dark">
              {{ formatStatus(task.status) }}
            </el-tag>
          </div>
          
          <p v-if="task.description" class="task-description">{{ task.description }}</p>
          
          <div class="task-meta">
            <div class="meta-item" v-if="task.project">
              <el-icon><Folder /></el-icon>
              <span>{{ task.project.name || task.project }}</span>
            </div>
            <div class="meta-item" v-if="task.assignee">
              <el-icon><User /></el-icon>
              <span>{{ task.assignee.full_name || task.assignee }}</span>
            </div>
            <div class="meta-item" v-if="task.due_date" :class="{ overdue: isOverdue(task) }">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDate(task.due_date) }}</span>
            </div>
          </div>
          
          <div class="task-footer">
            <el-tag :type="getPriorityType(task.priority)" size="small">
              {{ task.priority }} priority
            </el-tag>
            <div class="task-actions" @click.stop>
              <el-button type="info" text size="small" @click="editTask(task)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" text size="small" @click="deleteTask(task)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showCreateDialog" :title="editingTask ? 'Edit Task' : 'Create New Task'" width="520px" class="modern-dialog">
      <el-form :model="form" label-position="top">
        <el-form-item label="Title" required>
          <el-input v-model="form.title" placeholder="Enter task title" size="large" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="Enter description" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Priority">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="High" value="high" />
                <el-option label="Medium" value="medium" />
                <el-option label="Low" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="To Do" value="todo" />
                <el-option label="In Progress" value="in-progress" />
                <el-option label="Done" value="done" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Project">
              <el-select v-model="form.project_id" style="width: 100%" placeholder="Select project">
                <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Due Date">
              <el-date-picker v-model="form.due_date" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false" size="large">Cancel</el-button>
        <el-button type="primary" @click="saveTask" :loading="saving" size="large">
          {{ editingTask ? 'Update' : 'Create' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import http from '@/api/http'
import { ElMessage, ElMessageBox } from 'element-plus'

const tasks = ref([])
const projects = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const editingTask = ref(null)

const filters = reactive({
  search: '',
  status: '',
  priority: '',
  project_id: ''
})

const form = reactive({
  title: '',
  description: '',
  priority: 'medium',
  status: 'todo',
  project_id: null,
  due_date: null
})

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    if (filters.search && !task.title.toLowerCase().includes(filters.search.toLowerCase())) return false
    if (filters.status && task.status !== filters.status) return false
    if (filters.priority && task.priority !== filters.priority) return false
    if (filters.project_id && task.project_id !== filters.project_id) return false
    return true
  })
})

function getStatusType(status) {
  return { 'todo': 'info', 'in-progress': 'warning', 'done': 'success' }[status] || 'info'
}

function getPriorityType(priority) {
  return { 'high': 'danger', 'medium': 'warning', 'low': 'info' }[priority] || 'info'
}

function formatStatus(status) {
  return { 'todo': 'To Do', 'in-progress': 'In Progress', 'done': 'Done' }[status] || status
}

function formatDate(date) {
  return date ? new Date(date).toLocaleDateString() : ''
}

function isOverdue(task) {
  return task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done'
}

function resetForm() {
  Object.assign(form, { title: '', description: '', priority: 'medium', status: 'todo', project_id: null, due_date: null })
  editingTask.value = null
}

function editTask(task) {
  editingTask.value = task
  Object.assign(form, { ...task, project_id: task.project_id, due_date: task.due_date ? new Date(task.due_date) : null })
  showCreateDialog.value = true
}

async function fetchData() {
  loading.value = true
  try {
    const [tasksRes, projectsRes] = await Promise.all([http.get('/tasks'), http.get('/projects')])
    tasks.value = tasksRes.data || []
    projects.value = projectsRes.data || []
  } catch (e) {
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

async function saveTask() {
  if (!form.title.trim()) {
    ElMessage.warning('Please enter a task title')
    return
  }
  
  saving.value = true
  try {
    const data = { ...form, due_date: form.due_date ? new Date(form.due_date).toISOString().split('T')[0] : null }
    if (editingTask.value) {
      await http.put(`/tasks/${editingTask.value.id}`, data)
      ElMessage.success('Task updated')
    } else {
      await http.post('/tasks', data)
      ElMessage.success('Task created')
    }
    showCreateDialog.value = false
    resetForm()
    fetchData()
  } catch (e) {
    ElMessage.error('Failed to save task')
  } finally {
    saving.value = false
  }
}

async function deleteTask(task) {
  try {
    await ElMessageBox.confirm(`Delete "${task.title}"?`, 'Delete Task', { type: 'warning' })
    await http.delete(`/tasks/${task.id}`)
    ElMessage.success('Task deleted')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('Failed to delete')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.tasks-view {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #cdd6f4;
  font-size: 28px;
  margin: 0 0 4px;
}

.header-content p {
  color: #6c7086;
  margin: 0;
}

/* Filters */
.filters-card {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 16px;
  margin-bottom: 24px;
}

:deep(.filters-card .el-card__body) {
  padding: 16px 20px;
}

.filters-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Tasks List */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 200px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  background: #1e1e2e;
  border: 2px dashed #313244;
  border-radius: 20px;
  color: #6c7086;
}

.empty-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(49, 50, 68, 0.5);
  border-radius: 24px;
  margin-bottom: 20px;
}

.empty-state h3 { color: #cdd6f4; margin: 0 0 8px; }
.empty-state p { margin: 0; }

/* Task Card */
.task-card {
  display: flex;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-card:hover {
  border-color: #89b4fa;
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.task-priority-bar {
  width: 5px;
  flex-shrink: 0;
}

.task-priority-bar.high { background: #f38ba8; }
.task-priority-bar.medium { background: #f9e2af; }
.task-priority-bar.low { background: #89b4fa; }

.task-content {
  flex: 1;
  padding: 20px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.task-header h3 {
  color: #cdd6f4;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.task-description {
  color: #6c7086;
  font-size: 14px;
  margin: 0 0 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6c7086;
}

.meta-item.overdue {
  color: #f38ba8;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-actions {
  display: flex;
  gap: 4px;
}

/* Dialog */
:deep(.modern-dialog .el-dialog) {
  background: #1e1e2e;
  border-radius: 16px;
}

:deep(.modern-dialog .el-dialog__header) {
  border-bottom: 1px solid #313244;
  padding: 20px 24px;
}

:deep(.modern-dialog .el-dialog__title) { color: #cdd6f4; }
:deep(.modern-dialog .el-dialog__body) { padding: 24px; }
:deep(.modern-dialog .el-dialog__footer) { border-top: 1px solid #313244; padding: 16px 24px; }
</style>
