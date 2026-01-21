<template>
  <div class="dashboard-view">
    <!-- Welcome Banner -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <h1>Welcome back, {{ authStore.user?.full_name || 'User' }}! 👋</h1>
        <p>Here's what's happening with your tasks today</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="$router.push('/ai-chat')" round>
          <el-icon><ChatDotRound /></el-icon>
          Ask AI Assistant
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card todo">
        <div class="stat-icon">
          <el-icon size="28"><List /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.todo }}</span>
          <span class="stat-label">To Do</span>
        </div>
      </div>
      
      <div class="stat-card in-progress">
        <div class="stat-icon">
          <el-icon size="28"><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.inProgress }}</span>
          <span class="stat-label">In Progress</span>
        </div>
      </div>
      
      <div class="stat-card done">
        <div class="stat-icon">
          <el-icon size="28"><Check /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.done }}</span>
          <span class="stat-label">Completed</span>
        </div>
      </div>
      
      <div class="stat-card overdue">
        <div class="stat-icon">
          <el-icon size="28"><WarningFilled /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.overdue }}</span>
          <span class="stat-label">Overdue</span>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Recent Tasks -->
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <h3><el-icon><Document /></el-icon> Recent Tasks</h3>
            <el-button type="primary" text @click="$router.push('/tasks')">
              View All <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        
        <div v-if="recentTasks.length === 0" class="empty-state">
          <el-icon size="48"><Document /></el-icon>
          <p>No tasks yet</p>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in recentTasks" :key="task.id" class="task-item" @click="$router.push(`/tasks/${task.id}`)">
            <div class="task-priority" :class="task.priority"></div>
            <div class="task-content">
              <span class="task-title">{{ task.title }}</span>
              <span class="task-meta">
                <el-tag :type="getStatusType(task.status)" size="small" effect="dark">
                  {{ task.status }}
                </el-tag>
              </span>
            </div>
            <el-icon class="task-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </el-card>

      <!-- Projects Overview -->
      <el-card class="projects-card">
        <template #header>
          <div class="card-header">
            <h3><el-icon><Folder /></el-icon> Projects</h3>
            <el-button type="primary" text @click="$router.push('/projects')">
              View All <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        
        <div v-if="projects.length === 0" class="empty-state">
          <el-icon size="48"><Folder /></el-icon>
          <p>No projects yet</p>
        </div>
        
        <div v-else class="project-list">
          <div v-for="project in projects.slice(0, 5)" :key="project.id" class="project-item" @click="$router.push(`/projects/${project.id}`)">
            <div class="project-icon">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="project-info">
              <span class="project-name">{{ project.name }}</span>
              <span class="project-desc">{{ project.description || 'No description' }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'

const authStore = useAuthStore()
const recentTasks = ref([])
const projects = ref([])
const stats = reactive({
  todo: 0,
  inProgress: 0,
  done: 0,
  overdue: 0
})

function getStatusType(status) {
  const types = {
    todo: 'info',
    'in-progress': 'warning',
    done: 'success'
  }
  return types[status] || 'info'
}

async function fetchData() {
  try {
    const [tasksRes, projectsRes] = await Promise.all([
      http.get('/tasks'),
      http.get('/projects')
    ])
    
    const tasks = tasksRes.data || []
    recentTasks.value = tasks.slice(0, 5)
    projects.value = projectsRes.data || []
    
    stats.todo = tasks.filter(t => t.status === 'todo').length
    stats.inProgress = tasks.filter(t => t.status === 'in-progress').length
    stats.done = tasks.filter(t => t.status === 'done').length
    stats.overdue = tasks.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== 'done').length
  } catch (e) {
    console.error('Failed to fetch dashboard data')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.dashboard-view {
  padding: 0;
}

/* Welcome Banner */
.welcome-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  background: linear-gradient(135deg, rgba(137, 180, 250, 0.15) 0%, rgba(203, 166, 247, 0.15) 100%);
  border: 1px solid #313244;
  border-radius: 20px;
  margin-bottom: 24px;
}

.welcome-content h1 {
  color: #cdd6f4;
  font-size: 28px;
  margin: 0 0 8px;
}

.welcome-content p {
  color: #6c7086;
  margin: 0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #313244;
  background: #1e1e2e;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
}

.stat-card.todo .stat-icon {
  background: rgba(137, 180, 250, 0.2);
  color: #89b4fa;
}

.stat-card.in-progress .stat-icon {
  background: rgba(249, 226, 175, 0.2);
  color: #f9e2af;
}

.stat-card.done .stat-icon {
  background: rgba(166, 227, 161, 0.2);
  color: #a6e3a1;
}

.stat-card.overdue .stat-icon {
  background: rgba(243, 139, 168, 0.2);
  color: #f38ba8;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #cdd6f4;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #6c7086;
  margin-top: 4px;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.tasks-card,
.projects-card {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 16px;
}

:deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #313244;
}

:deep(.el-card__body) {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  color: #cdd6f4;
  font-size: 16px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #6c7086;
}

.empty-state p {
  margin: 12px 0 0;
}

/* Task List */
.task-list {
  padding: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.task-item:hover {
  background: rgba(49, 50, 68, 0.5);
}

.task-priority {
  width: 4px;
  height: 32px;
  border-radius: 2px;
}

.task-priority.high { background: #f38ba8; }
.task-priority.medium { background: #f9e2af; }
.task-priority.low { background: #89b4fa; }

.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-title {
  color: #cdd6f4;
  font-weight: 500;
}

.task-arrow {
  color: #6c7086;
}

/* Project List */
.project-list {
  padding: 8px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.project-item:hover {
  background: rgba(49, 50, 68, 0.5);
}

.project-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border-radius: 10px;
  color: #1e1e2e;
}

.project-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.project-name {
  color: #cdd6f4;
  font-weight: 500;
}

.project-desc {
  color: #6c7086;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome-banner {
    flex-direction: column;
    text-align: center;
    gap: 16px;
    padding: 24px;
  }
  
  .welcome-content h1 {
    font-size: 22px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-card {
    padding: 16px;
    gap: 12px;
  }
  
  .stat-icon {
    width: 44px;
    height: 44px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .stat-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 14px;
  }
  
  .stat-icon {
    width: 36px;
    height: 36px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}
</style>
