<template>
  <div class="projects-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1><el-icon><Folder /></el-icon> Projects</h1>
        <p>Manage your team's projects</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true" round>
        <el-icon><Plus /></el-icon>
        New Project
      </el-button>
    </div>

    <!-- Projects Grid -->
    <div v-loading="loading" class="projects-grid">
      <div v-if="projects.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <el-icon size="64"><Folder /></el-icon>
        </div>
        <h3>No projects yet</h3>
        <p>Create your first project to get started</p>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          Create Project
        </el-button>
      </div>

      <div v-for="project in projects" :key="project.id" class="project-card" @click="$router.push(`/projects/${project.id}`)">
        <div class="project-header">
          <div class="project-icon">
            <el-icon size="24"><Folder /></el-icon>
          </div>
          <el-dropdown @click.stop>
            <el-button type="info" text circle size="small">
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="editProject(project)">
                  <el-icon><Edit /></el-icon> Edit
                </el-dropdown-item>
                <el-dropdown-item @click="deleteProject(project)" divided>
                  <el-icon><Delete /></el-icon> Delete
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <h3 class="project-name">{{ project.name }}</h3>
        <p class="project-desc">{{ project.description || 'No description' }}</p>
        
        <div class="project-stats">
          <div class="stat">
            <span class="value">{{ project.task_count || 0 }}</span>
            <span class="label">Tasks</span>
          </div>
          <div class="stat">
            <span class="value">{{ project.member_count || 0 }}</span>
            <span class="label">Members</span>
          </div>
        </div>
        
        <div class="project-footer">
          <el-tag size="small" effect="dark" type="success">Active</el-tag>
          <span class="date">{{ formatDate(project.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? 'Edit Project' : 'Create New Project'"
      width="480px"
      class="modern-dialog"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="Project Name" required>
          <el-input v-model="form.name" placeholder="Enter project name" size="large" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="Enter project description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false" size="large">Cancel</el-button>
        <el-button type="primary" @click="saveProject" :loading="saving" size="large">
          {{ editingProject ? 'Update' : 'Create' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const projects = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const editingProject = ref(null)

const form = reactive({
  name: '',
  description: ''
})

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

function resetForm() {
  form.name = ''
  form.description = ''
  editingProject.value = null
}

function editProject(project) {
  editingProject.value = project
  form.name = project.name
  form.description = project.description || ''
  showCreateDialog.value = true
}

async function fetchProjects() {
  loading.value = true
  try {
    const res = await http.get('/projects')
    projects.value = res.data || []
  } catch (e) {
    ElMessage.error('Failed to load projects')
  } finally {
    loading.value = false
  }
}

async function saveProject() {
  if (!form.name.trim()) {
    ElMessage.warning('Please enter a project name')
    return
  }
  
  saving.value = true
  try {
    if (editingProject.value) {
      await http.put(`/projects/${editingProject.value.id}`, form)
      ElMessage.success('Project updated successfully')
    } else {
      await http.post('/projects', { 
        ...form, 
        organization_id: authStore.user?.organization_id 
      })
      ElMessage.success('Project created successfully')
    }
    showCreateDialog.value = false
    resetForm()
    fetchProjects()
  } catch (e) {
    ElMessage.error('Failed to save project')
  } finally {
    saving.value = false
  }
}

async function deleteProject(project) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${project.name}"?`,
      'Delete Project',
      { type: 'warning' }
    )
    await http.delete(`/projects/${project.id}`)
    ElMessage.success('Project deleted successfully')
    fetchProjects()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('Failed to delete project')
  }
}

onMounted(fetchProjects)
</script>

<style scoped>
.projects-view {
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

/* Projects Grid */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.empty-state {
  grid-column: 1 / -1;
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

.empty-state h3 {
  color: #cdd6f4;
  margin: 0 0 8px;
}

.empty-state p {
  margin: 0 0 20px;
}

/* Project Card */
.project-card {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.project-card:hover {
  border-color: #89b4fa;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.project-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border-radius: 12px;
  color: #1e1e2e;
}

.project-name {
  color: #cdd6f4;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
}

.project-desc {
  color: #6c7086;
  font-size: 14px;
  margin: 0 0 20px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(49, 50, 68, 0.5);
  border-radius: 12px;
}

.project-stats .stat {
  display: flex;
  flex-direction: column;
}

.project-stats .value {
  font-size: 24px;
  font-weight: 700;
  color: #cdd6f4;
}

.project-stats .label {
  font-size: 12px;
  color: #6c7086;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-footer .date {
  font-size: 12px;
  color: #6c7086;
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

:deep(.modern-dialog .el-dialog__title) {
  color: #cdd6f4;
}

:deep(.modern-dialog .el-dialog__body) {
  padding: 24px;
}

:deep(.modern-dialog .el-dialog__footer) {
  border-top: 1px solid #313244;
  padding: 16px 24px;
}
</style>
