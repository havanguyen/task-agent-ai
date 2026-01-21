import axios from 'axios'
import { ElMessage } from 'element-plus'

// Use environment variable for API URL
// In development (localhost): VITE_API_URL=http://localhost:8000/api/v1
// In production (Vercel): VITE_API_URL=https://task-agent-ai.onrender.com/api/v1
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://task-agent-ai.onrender.com/api/v1'

const http = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request interceptor - add auth token
http.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor - handle errors
http.interceptors.response.use(
    (response) => response,
    (error) => {
        const message = error.response?.data?.detail || error.message || 'An error occurred'

        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.href = '/login'
        } else {
            ElMessage.error(message)
        }

        return Promise.reject(error)
    }
)

export default http
