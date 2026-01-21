<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <el-icon size="48" color="#89b4fa"><OfficeBuilding /></el-icon>
        <h1>Register Organization</h1>
        <p>Create your organization account</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="Organization Name" prop="orgName">
          <el-input
            v-model="form.orgName"
            placeholder="Enter organization name"
            prefix-icon="OfficeBuilding"
            size="large"
          />
        </el-form-item>

        <el-form-item label="Full Name" prop="fullName">
          <el-input
            v-model="form.fullName"
            placeholder="Enter your full name"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input
            v-model="form.email"
            placeholder="Enter your email"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            native-type="submit"
            class="register-btn"
          >
            Create Organization
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>Already have an account?</span>
        <router-link to="/login">Sign In</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  orgName: '',
  fullName: '',
  email: '',
  password: ''
})

const rules = {
  orgName: [
    { required: true, message: 'Please enter organization name', trigger: 'blur' }
  ],
  fullName: [
    { required: true, message: 'Please enter your full name', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    { type: 'email', message: 'Invalid email format', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

async function handleRegister() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await authStore.register(form.orgName, form.email, form.password, form.fullName)
      ElMessage.success('Registration successful! Please login.')
      router.push('/login')
    } catch (error) {
      // Error already handled by http interceptor
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #11111b 0%, #1e1e2e 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: #1e1e2e;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid #313244;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  color: #cdd6f4;
  font-size: 24px;
  margin: 16px 0 8px;
}

.register-header p {
  color: #6c7086;
  font-size: 14px;
}

:deep(.el-form-item__label) {
  color: #a6adc8;
}

:deep(.el-input__wrapper) {
  background: #11111b;
  border: 1px solid #313244;
  box-shadow: none;
}

:deep(.el-input__wrapper:hover) {
  border-color: #89b4fa;
}

:deep(.el-input__inner) {
  color: #cdd6f4;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #89b4fa, #cba6f7);
  border: none;
}

.register-btn:hover {
  opacity: 0.9;
}

.register-footer {
  text-align: center;
  margin-top: 24px;
  color: #6c7086;
  font-size: 14px;
}

.register-footer a {
  color: #89b4fa;
  margin-left: 8px;
  text-decoration: none;
}

.register-footer a:hover {
  text-decoration: underline;
}
</style>
