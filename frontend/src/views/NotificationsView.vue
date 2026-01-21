<template>
  <div class="notifications-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1><el-icon><Bell /></el-icon> Notifications</h1>
        <p>Stay updated with your tasks and projects</p>
      </div>
      <el-button v-if="unreadCount > 0" type="primary" @click="markAllRead" round>
        <el-icon><Select /></el-icon>
        Mark All Read
      </el-button>
    </div>

    <!-- Notifications List -->
    <div v-loading="loading" class="notifications-list">
      <div v-if="notifications.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <el-icon size="64"><Bell /></el-icon>
        </div>
        <h3>No notifications</h3>
        <p>You're all caught up!</p>
      </div>

      <transition-group name="notification" tag="div">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-card"
          :class="{ unread: !notification.is_read }"
          @click="markAsRead(notification)"
        >
          <div class="notification-indicator" v-if="!notification.is_read"></div>
          <div class="notification-icon">
            <el-icon size="24"><Bell /></el-icon>
          </div>
          <div class="notification-content">
            <h4>{{ notification.title }}</h4>
            <p>{{ notification.message }}</p>
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          </div>
          <el-button v-if="!notification.is_read" type="primary" text size="small" @click.stop="markAsRead(notification)">
            Mark Read
          </el-button>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'
import { ElMessage } from 'element-plus'

const notifications = ref([])
const loading = ref(false)

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

function formatTime(date) {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`
  return d.toLocaleDateString()
}

async function fetchNotifications() {
  loading.value = true
  try {
    const res = await http.get('/notifications')
    notifications.value = res.data || []
  } catch (e) {
    console.error('Failed to load notifications')
  } finally {
    loading.value = false
  }
}

async function markAsRead(notification) {
  if (notification.is_read) return
  try {
    await http.put(`/notifications/${notification.id}/read`)
    notification.is_read = true
  } catch (e) {
    console.error('Failed to mark as read')
  }
}

async function markAllRead() {
  try {
    await Promise.all(
      notifications.value.filter(n => !n.is_read).map(n => http.put(`/notifications/${n.id}/read`))
    )
    notifications.value.forEach(n => n.is_read = true)
    ElMessage.success('All notifications marked as read')
  } catch (e) {
    ElMessage.error('Failed to mark all as read')
  }
}

onMounted(fetchNotifications)
</script>

<style scoped>
.notifications-view {
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

/* Notifications List */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
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
  background: rgba(166, 227, 161, 0.1);
  border-radius: 50%;
  margin-bottom: 20px;
  color: #a6e3a1;
}

.empty-state h3 { color: #cdd6f4; margin: 0 0 8px; }
.empty-state p { margin: 0; }

/* Notification Card */
.notification-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.notification-card:hover {
  border-color: #89b4fa;
  background: rgba(49, 50, 68, 0.5);
}

.notification-card.unread {
  background: rgba(137, 180, 250, 0.05);
  border-color: rgba(137, 180, 250, 0.3);
}

.notification-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #89b4fa;
  border-radius: 16px 0 0 16px;
}

.notification-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(137, 180, 250, 0.15);
  border-radius: 12px;
  color: #89b4fa;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-content h4 {
  color: #cdd6f4;
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 6px;
}

.notification-content p {
  color: #a6adc8;
  font-size: 14px;
  margin: 0 0 8px;
  line-height: 1.5;
}

.notification-time {
  font-size: 12px;
  color: #6c7086;
}

/* Animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
