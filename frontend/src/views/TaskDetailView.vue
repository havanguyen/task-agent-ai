<template>
  <div class="task-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.push('/tasks')">
          <el-icon><ArrowLeft /></el-icon>
          Back
        </el-button>
        <h2>{{ task.title }}</h2>
        <el-tag :type="statusTagType(task.status)" size="small">{{ formatStatus(task.status) }}</el-tag>
      </div>
      <div class="header-right" v-if="task.status !== 'done'">
        <el-button v-if="task.status === 'todo'" type="warning" @click="updateStatus('in-progress')">
          <el-icon><VideoPlay /></el-icon>
          Start Progress
        </el-button>
        <el-button v-if="task.status === 'in-progress'" type="success" @click="updateStatus('done')">
          <el-icon><Check /></el-icon>
          Mark Done
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="detail-card">
          <template #header>Task Details</template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Title" :span="2">{{ task.title }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ task.description || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="statusTagType(task.status)" size="small">{{ formatStatus(task.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Priority">
              <el-tag :type="priorityTagType(task.priority)" size="small" effect="plain">{{ task.priority }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Due Date">
              <span :class="{ 'overdue': isOverdue(task) }">{{ formatDate(task.due_date) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="Assignee">{{ task.assignee?.full_name || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="detail-card mt-20">
          <template #header>
            <div class="card-header">
              <span>Comments</span>
            </div>
          </template>
          <div v-if="comments.length === 0" class="no-data">No comments yet</div>
          <div v-else class="comments-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <el-avatar :size="32">{{ getInitials(comment.user?.full_name) }}</el-avatar>
              <div class="comment-content">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.user?.full_name }}</span>
                  <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="comment-text">{{ comment.content }}</p>
              </div>
            </div>
          </div>
          <el-divider />
          <el-form @submit.prevent="submitComment">
            <el-input v-model="newComment" type="textarea" :rows="2" placeholder="Add a comment..." />
            <el-button type="primary" size="small" style="margin-top: 12px;" @click="submitComment" :loading="submittingComment">
              Add Comment
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>Attachments</span>
            </div>
          </template>
          <div v-if="attachments.length === 0" class="no-data">No attachments</div>
          <div v-else class="attachments-list">
            <div v-for="attachment in attachments" :key="attachment.id" class="attachment-item">
              <el-icon><Document /></el-icon>
              <span class="attachment-name">{{ attachment.filename }}</span>
            </div>
          </div>
          <el-divider v-if="attachments.length < 3" />
          <el-upload
            v-if="attachments.length < 3"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept="*"
          >
            <el-button size="small">
              <el-icon><Upload /></el-icon>
              Upload File
            </el-button>
          </el-upload>
          <p v-if="attachments.length >= 3" class="limit-text">Max 3 attachments reached</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '@/api/http'

const route = useRoute()
const router = useRouter()

const task = ref({})
const comments = ref([])
const attachments = ref([])
const newComment = ref('')
const submittingComment = ref(false)

function statusTagType(status) {
  return { todo: 'info', 'in-progress': 'warning', done: 'success' }[status] || 'info'
}

function priorityTagType(priority) {
  return { low: 'info', medium: 'warning', high: 'danger' }[priority] || 'info'
}

function formatStatus(status) {
  if (!status) return ''
  return status.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

function isOverdue(task) {
  if (!task.due_date || task.status === 'done') return false
  return new Date(task.due_date) < new Date()
}

function getInitials(name) {
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

async function fetchTask() {
  try {
    const response = await http.get(`/tasks/${route.params.id}`)
    task.value = response.data
  } catch (error) {
    router.push('/tasks')
  }
}

async function fetchComments() {
  try {
    const response = await http.get(`/tasks/${route.params.id}/comments`)
    comments.value = response.data
  } catch (error) {}
}

async function fetchAttachments() {
  try {
    const response = await http.get(`/tasks/${route.params.id}/attachments`)
    attachments.value = response.data
  } catch (error) {}
}

async function updateStatus(newStatus) {
  try {
    await http.patch(`/tasks/${route.params.id}`, { status: newStatus })
    ElMessage.success('Status updated')
    fetchTask()
  } catch (error) {}
}

async function submitComment() {
  if (!newComment.value.trim()) return
  
  submittingComment.value = true
  try {
    await http.post(`/tasks/${route.params.id}/comments`, { content: newComment.value })
    ElMessage.success('Comment added')
    newComment.value = ''
    fetchComments()
  } catch (error) {
  } finally {
    submittingComment.value = false
  }
}

async function handleFileChange(file) {
  const formData = new FormData()
  formData.append('file', file.raw)
  
  try {
    await http.post(`/tasks/${route.params.id}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('File uploaded')
    fetchAttachments()
  } catch (error) {}
}

onMounted(() => {
  fetchTask()
  fetchComments()
  fetchAttachments()
})
</script>

<style scoped>
.task-detail {
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
  border-radius: 12px;
}

:deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid #313244;
  padding: 16px 20px;
  color: #cdd6f4;
  font-weight: 600;
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

.overdue {
  color: #f38ba8;
}

.no-data {
  text-align: center;
  color: #6c7086;
  padding: 24px 0;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.comment-author {
  color: #cdd6f4;
  font-weight: 500;
  font-size: 14px;
}

.comment-time {
  color: #6c7086;
  font-size: 12px;
}

.comment-text {
  color: #a6adc8;
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
}

:deep(.el-divider) {
  border-color: #313244;
}

:deep(.el-textarea__inner) {
  background: #11111b;
  border: 1px solid #313244;
  color: #cdd6f4;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #11111b;
  border-radius: 6px;
  color: #cdd6f4;
  font-size: 14px;
}

.limit-text {
  color: #6c7086;
  font-size: 12px;
  text-align: center;
  margin: 8px 0 0;
}
</style>
