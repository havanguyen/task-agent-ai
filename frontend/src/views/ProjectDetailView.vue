<template>
  <div class="project-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.push('/projects')">
          <el-icon><ArrowLeft /></el-icon>
          Back
        </el-button>
        <h2>{{ project.name || 'Loading...' }}</h2>
      </div>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :xs="24" :lg="16">
        <el-card class="detail-card">
          <template #header>
            <span>Project Details</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Name">{{ project.name }}</el-descriptions-item>
            <el-descriptions-item label="Description">{{ project.description || 'No description' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="detail-card mt-20">
          <template #header>
            <div class="card-header">
              <span>Task Statistics</span>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :span="8">
              <div class="mini-stat">
                <span class="mini-stat-value">{{ stats.todo }}</span>
                <span class="mini-stat-label">Todo</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="mini-stat in-progress">
                <span class="mini-stat-value">{{ stats.inProgress }}</span>
                <span class="mini-stat-label">In Progress</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="mini-stat done">
                <span class="mini-stat-value">{{ stats.done }}</span>
                <span class="mini-stat-label">Done</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- Project Tasks -->
        <el-card class="detail-card mt-20">
          <template #header>
            <div class="card-header">
              <span>Tasks ({{ projectTasks.length }})</span>
              <el-button type="primary" size="small" @click="router.push('/tasks')">
                <el-icon><Plus /></el-icon> Add Task
              </el-button>
            </div>
          </template>
          <div v-if="projectTasks.length === 0" class="no-data">No tasks in this project</div>
          <div v-else class="task-list">
            <div v-for="task in projectTasks" :key="task.id" class="task-item" @click="router.push(`/tasks/${task.id}`)">
              <div class="task-priority" :class="task.priority"></div>
              <div class="task-info">
                <span class="task-title">{{ task.title }}</span>
                <el-tag :type="getStatusType(task.status)" size="small" effect="dark">
                  {{ formatStatus(task.status) }}
                </el-tag>
              </div>
              <el-icon class="task-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="detail-card">
          <template #header>
            <span>Overdue Tasks</span>
          </template>
          <div v-if="overdueTasks.length === 0" class="no-data success">
            <el-icon><Check /></el-icon>
            <span>No overdue tasks!</span>
          </div>
          <div v-else class="overdue-list">
            <div v-for="task in overdueTasks" :key="task.id" class="overdue-item">
              <router-link :to="`/tasks/${task.id}`">{{ task.title }}</router-link>
              <span class="overdue-date">{{ formatDate(task.due_date) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/api/http'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const project = ref({})
const projectTasks = ref([])
const loading = ref(false)

const stats = reactive({
  todo: 0,
  inProgress: 0,
  done: 0
})

const overdueTasks = computed(() => {
  const now = new Date()
  return projectTasks.value.filter(t => 
    t.due_date && new Date(t.due_date) < now && t.status !== 'done'
  )
})

function getStatusType(status) {
  return { 'todo': 'info', 'in-progress': 'warning', 'done': 'success' }[status] || 'info'
}

function formatStatus(status) {
  return { 'todo': 'To Do', 'in-progress': 'In Progress', 'done': 'Done' }[status] || status
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

async function fetchData() {
  loading.value = true
  try {
    // Fetch all projects and find the one we need
    const projectsRes = await http.get('/projects')
    const projects = projectsRes.data || []
    const found = projects.find(p => p.id === parseInt(route.params.id))
    
    if (!found) {
      ElMessage.error('Project not found')
      router.push('/projects')
      return
    }
    
    project.value = found
    
    // Fetch all tasks and filter by project
    const tasksRes = await http.get('/tasks')
    const allTasks = tasksRes.data || []
    projectTasks.value = allTasks.filter(t => t.project_id === parseInt(route.params.id))
    
    // Calculate stats
    stats.todo = projectTasks.value.filter(t => t.status === 'todo').length
    stats.inProgress = projectTasks.value.filter(t => t.status === 'in-progress').length
    stats.done = projectTasks.value.filter(t => t.status === 'done').length
    
  } catch (error) {
    ElMessage.error('Failed to load project')
    router.push('/projects')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.project-detail {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  color: #cdd6f4;
  margin: 0;
  font-size: 24px;
}

.detail-card {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 16px;
}

:deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid #313244;
  padding: 16px 20px;
  color: #cdd6f4;
  font-weight: 600;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-descriptions__label) {
  background: #181825;
  color: #a6adc8;
}

:deep(.el-descriptions__content) {
  background: #11111b;
  color: #cdd6f4;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mini-stat {
  text-align: center;
  padding: 20px;
  background: rgba(137, 180, 250, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(137, 180, 250, 0.2);
}

.mini-stat.in-progress {
  background: rgba(249, 226, 175, 0.1);
  border-color: rgba(249, 226, 175, 0.2);
}

.mini-stat.done {
  background: rgba(166, 227, 161, 0.1);
  border-color: rgba(166, 227, 161, 0.2);
}

.mini-stat-value {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #cdd6f4;
}

.mini-stat-label {
  font-size: 13px;
  color: #6c7086;
  margin-top: 4px;
}

.no-data {
  text-align: center;
  color: #6c7086;
  padding: 32px;
}

.no-data.success {
  color: #a6e3a1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(49, 50, 68, 0.3);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.task-item:hover {
  background: rgba(137, 180, 250, 0.1);
}

.task-priority {
  width: 4px;
  height: 28px;
  border-radius: 2px;
}

.task-priority.high { background: #f38ba8; }
.task-priority.medium { background: #f9e2af; }
.task-priority.low { background: #89b4fa; }

.task-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-title {
  color: #cdd6f4;
  font-weight: 500;
}

.task-arrow {
  color: #6c7086;
}

/* Overdue */
.overdue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.overdue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(243, 139, 168, 0.1);
  border: 1px solid rgba(243, 139, 168, 0.2);
  border-radius: 8px;
}

.overdue-item a {
  color: #f38ba8;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.overdue-date {
  color: #6c7086;
  font-size: 12px;
}

@media (max-width: 992px) {
  .el-col {
    margin-bottom: 20px;
  }
}
</style>
