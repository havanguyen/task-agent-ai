<template>
  <div class="login-container">
    <div class="login-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>
    
    <el-card class="login-card">
      <div class="login-header">
        <div class="logo">
          <el-icon size="40"><Management /></el-icon>
        </div>
        <h1>Welcome Back</h1>
        <p>Sign in to continue to Task Manager</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="Sign In" name="login">
          <el-form :model="loginForm" @submit.prevent="handleLogin" label-position="top">
            <el-form-item label="Email">
              <el-input
                v-model="loginForm.email"
                type="email"
                placeholder="Enter your email"
                size="large"
                prefix-icon="Message"
              />
            </el-form-item>
            <el-form-item label="Password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="Enter your password"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-button type="primary" native-type="submit" :loading="loading" size="large" class="submit-btn">
              Sign In
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Sign Up" name="register">
          <el-form :model="registerForm" @submit.prevent="handleRegister" label-position="top">
            <el-form-item label="Organization Name">
              <el-input v-model="registerForm.organization_name" placeholder="Your company name" size="large" prefix-icon="OfficeBuilding" />
            </el-form-item>
            <el-form-item label="Full Name">
              <el-input v-model="registerForm.full_name" placeholder="Your full name" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item label="Email">
              <el-input v-model="registerForm.email" type="email" placeholder="Your email" size="large" prefix-icon="Message" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="registerForm.password" type="password" placeholder="Create password" size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-button type="primary" native-type="submit" :loading="loading" size="large" class="submit-btn">
              Create Account
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const activeTab = ref('login')

const loginForm = reactive({ email: '', password: '' })
const registerForm = reactive({ organization_name: '', full_name: '', email: '', password: '' })

async function handleLogin() {
  if (!loginForm.email || !loginForm.password) {
    ElMessage.warning('Please fill in all fields')
    return
  }
  loading.value = true
  try {
    await authStore.login(loginForm.email, loginForm.password)
    ElMessage.success('Welcome back!')
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Login failed')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.organization_name || !registerForm.full_name || !registerForm.email || !registerForm.password) {
    ElMessage.warning('Please fill in all fields')
    return
  }
  loading.value = true
  try {
    await authStore.register(registerForm)
    ElMessage.success('Account created! Please sign in.')
    activeTab.value = 'login'
    loginForm.email = registerForm.email
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background: #11111b;
}

.login-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #89b4fa;
  top: -100px;
  left: -100px;
  animation: float 8s ease-in-out infinite;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #cba6f7;
  bottom: -50px;
  right: -50px;
  animation: float 10s ease-in-out infinite reverse;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: #f38ba8;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(10deg); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.5; }
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(30, 30, 46, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid #313244;
  border-radius: 24px;
  position: relative;
  z-index: 1;
}

:deep(.el-card__body) {
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border-radius: 20px;
  color: #1e1e2e;
}

.login-header h1 {
  color: #cdd6f4;
  font-size: 28px;
  margin: 0 0 8px;
}

.login-header p {
  color: #6c7086;
  margin: 0;
}

/* Tabs */
:deep(.login-tabs .el-tabs__header) {
  margin-bottom: 24px;
}

:deep(.login-tabs .el-tabs__nav-wrap::after) {
  background: #313244;
}

:deep(.login-tabs .el-tabs__item) {
  color: #6c7086;
  font-weight: 500;
}

:deep(.login-tabs .el-tabs__item.is-active) {
  color: #89b4fa;
}

:deep(.login-tabs .el-tabs__active-bar) {
  background: linear-gradient(90deg, #89b4fa, #cba6f7);
}

/* Form */
:deep(.el-form-item__label) {
  color: #a6adc8;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  background: #11111b;
  border: 1px solid #313244;
  border-radius: 12px;
  box-shadow: none !important;
}

:deep(.el-input__wrapper:focus-within) {
  border-color: #89b4fa;
}

:deep(.el-input__inner) {
  color: #cdd6f4;
}

:deep(.el-input__prefix) {
  color: #6c7086;
}

.submit-btn {
  width: 100%;
  height: 48px;
  margin-top: 8px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border: none;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #74c7ec 0%, #89b4fa 100%);
}
</style>
