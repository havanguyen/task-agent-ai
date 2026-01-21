<template>
  <div class="main-layout">
    <!-- Mobile Header -->
    <header class="mobile-header" v-if="isMobile">
      <el-button type="info" text @click="showMobileMenu = true">
        <el-icon size="24"><Menu /></el-icon>
      </el-button>
      <span class="mobile-logo">TaskFlow</span>
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="9">
        <el-button type="info" text @click="$router.push('/notifications')">
          <el-icon size="20"><Bell /></el-icon>
        </el-button>
      </el-badge>
    </header>

    <!-- Mobile Drawer Menu -->
    <el-drawer
      v-model="showMobileMenu"
      direction="ltr"
      size="280px"
      :show-close="false"
      class="mobile-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <div class="logo">
            <el-icon size="24"><Management /></el-icon>
            <span class="logo-text">TaskFlow</span>
          </div>
          <el-button type="info" text @click="showMobileMenu = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </template>
      
      <nav class="mobile-nav">
        <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }" @click="showMobileMenu = false">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/projects" class="nav-item" :class="{ active: $route.path.startsWith('/projects') }" @click="showMobileMenu = false">
          <el-icon><Folder /></el-icon>
          <span>Projects</span>
        </router-link>
        <router-link to="/tasks" class="nav-item" :class="{ active: $route.path.startsWith('/tasks') }" @click="showMobileMenu = false">
          <el-icon><Document /></el-icon>
          <span>Tasks</span>
        </router-link>
        <router-link to="/notifications" class="nav-item" :class="{ active: $route.path === '/notifications' }" @click="showMobileMenu = false">
          <el-icon><Bell /></el-icon>
          <span>Notifications</span>
          <el-badge v-if="unreadCount > 0" :value="unreadCount" :max="9" />
        </router-link>
        
        <div class="nav-divider"></div>
        
        <router-link to="/ai-chat" class="nav-item ai-item" :class="{ active: $route.path === '/ai-chat' }" @click="showMobileMenu = false">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI Assistant</span>
          <el-tag size="small" effect="dark" type="success">New</el-tag>
        </router-link>
      </nav>
      
      <div class="drawer-footer">
        <div class="user-info">
          <el-avatar :size="40" class="user-avatar">{{ userInitials }}</el-avatar>
          <div class="user-details">
            <span class="user-name">{{ authStore.user?.full_name || 'User' }}</span>
            <span class="user-role">{{ authStore.user?.role || 'Member' }}</span>
          </div>
        </div>
        <el-button type="danger" @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          Logout
        </el-button>
      </div>
    </el-drawer>

    <!-- Desktop Sidebar -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }" v-if="!isMobile">
      <div class="sidebar-header">
        <div class="logo" @click="$router.push('/dashboard')">
          <el-icon size="24"><Management /></el-icon>
          <span v-show="!isCollapsed" class="logo-text">TaskFlow</span>
        </div>
        <el-button type="info" text @click="isCollapsed = !isCollapsed" class="collapse-btn">
          <el-icon><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
        </el-button>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
          <el-icon><HomeFilled /></el-icon>
          <span v-show="!isCollapsed">Dashboard</span>
        </router-link>
        <router-link to="/projects" class="nav-item" :class="{ active: $route.path.startsWith('/projects') }">
          <el-icon><Folder /></el-icon>
          <span v-show="!isCollapsed">Projects</span>
        </router-link>
        <router-link to="/tasks" class="nav-item" :class="{ active: $route.path.startsWith('/tasks') }">
          <el-icon><Document /></el-icon>
          <span v-show="!isCollapsed">Tasks</span>
        </router-link>
        <router-link to="/notifications" class="nav-item" :class="{ active: $route.path === '/notifications' }">
          <el-icon><Bell /></el-icon>
          <span v-show="!isCollapsed">Notifications</span>
          <el-badge v-if="unreadCount > 0 && !isCollapsed" :value="unreadCount" :max="9" />
        </router-link>
        
        <div class="nav-divider"></div>
        
        <router-link to="/ai-chat" class="nav-item ai-item" :class="{ active: $route.path === '/ai-chat' }">
          <el-icon><ChatDotRound /></el-icon>
          <span v-show="!isCollapsed">AI Assistant</span>
          <el-tag v-if="!isCollapsed" size="small" effect="dark" type="success">New</el-tag>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info" v-show="!isCollapsed">
          <el-avatar :size="40" class="user-avatar">{{ userInitials }}</el-avatar>
          <div class="user-details">
            <span class="user-name">{{ authStore.user?.full_name || 'User' }}</span>
            <span class="user-role">{{ authStore.user?.role || 'Member' }}</span>
          </div>
        </div>
        <el-button type="danger" text @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          <span v-show="!isCollapsed">Logout</span>
        </el-button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content" :class="{ mobile: isMobile }">
      <header class="top-bar" v-if="!isMobile">
        <h2 class="page-title">{{ currentPageTitle }}</h2>
        <div class="top-actions">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="9">
            <el-button type="info" text circle @click="$router.push('/notifications')">
              <el-icon size="20"><Bell /></el-icon>
            </el-button>
          </el-badge>
        </div>
      </header>
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)
const unreadCount = ref(0)
const showMobileMenu = ref(false)
const isMobile = ref(window.innerWidth < 768)

const userInitials = computed(() => {
  const name = authStore.user?.full_name || 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const currentPageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/projects': 'Projects',
    '/tasks': 'Tasks',
    '/notifications': 'Notifications',
    '/ai-chat': 'AI Assistant'
  }
  return titles[route.path] || 'Dashboard'
})

function handleResize() {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) showMobileMenu.value = false
}

async function fetchNotifications() {
  try {
    const res = await http.get('/notifications')
    unreadCount.value = (res.data || []).filter(n => !n.is_read).length
  } catch (e) {}
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchNotifications()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  background: #11111b;
}

/* Mobile Header */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #1e1e2e;
  border-bottom: 1px solid #313244;
  z-index: 100;
}

.mobile-logo {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Mobile Drawer */
:deep(.mobile-drawer .el-drawer) {
  background: #1e1e2e !important;
}

:deep(.mobile-drawer .el-drawer__header) {
  padding: 16px;
  margin-bottom: 0;
  border-bottom: 1px solid #313244;
}

:deep(.mobile-drawer .el-drawer__body) {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.mobile-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-footer {
  padding: 16px;
  border-top: 1px solid #313244;
}

.drawer-footer .user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(49, 50, 68, 0.5);
  border-radius: 12px;
}

.drawer-footer .logout-btn {
  width: 100%;
}

/* Desktop Sidebar */
.sidebar {
  width: 260px;
  background: #1e1e2e;
  border-right: 1px solid #313244;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #313244;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  color: #cdd6f4;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.collapse-btn {
  color: #6c7086;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  color: #a6adc8;
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(137, 180, 250, 0.1);
  color: #89b4fa;
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(137, 180, 250, 0.2) 0%, rgba(203, 166, 247, 0.1) 100%);
  color: #89b4fa;
}

.nav-item.ai-item {
  background: rgba(166, 227, 161, 0.05);
  border: 1px dashed rgba(166, 227, 161, 0.2);
}

.nav-item.ai-item:hover,
.nav-item.ai-item.active {
  background: rgba(166, 227, 161, 0.15);
  border-color: #a6e3a1;
  color: #a6e3a1;
}

.nav-divider {
  height: 1px;
  background: #313244;
  margin: 12px 0;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #313244;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(49, 50, 68, 0.5);
  border-radius: 12px;
}

.user-avatar {
  background: linear-gradient(135deg, #f38ba8 0%, #fab387 100%);
  color: #1e1e2e;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  color: #cdd6f4;
  font-weight: 600;
  font-size: 14px;
}

.user-role {
  color: #6c7086;
  font-size: 12px;
  text-transform: capitalize;
}

.logout-btn {
  width: 100%;
  justify-content: center;
  color: #f38ba8;
}

.logout-btn:hover {
  background: rgba(243, 139, 168, 0.1);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-content.mobile {
  padding-top: 56px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: #1e1e2e;
  border-bottom: 1px solid #313244;
}

.page-title {
  color: #cdd6f4;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.content-wrapper {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 16px;
  }
}
</style>
