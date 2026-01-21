import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/api/http'

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('token') || null)
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

    const isAuthenticated = computed(() => !!token.value)
    const userRole = computed(() => user.value?.role || 'member')
    const isAdmin = computed(() => userRole.value === 'admin')
    const isManager = computed(() => userRole.value === 'manager' || isAdmin.value)

    async function login(email, password) {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)

        const response = await http.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })

        token.value = response.data.access_token
        localStorage.setItem('token', token.value)

        // Fetch user info
        await fetchUser()

        return response.data
    }

    async function register(orgName, email, password, fullName) {
        const response = await http.post('/organizations/register', {
            organization_name: orgName,
            email,
            password,
            full_name: fullName
        })
        return response.data
    }

    async function fetchUser() {
        if (!token.value) return

        const response = await http.get('/users/me')
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(user.value))
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
    }

    return {
        token,
        user,
        isAuthenticated,
        userRole,
        isAdmin,
        isManager,
        login,
        register,
        fetchUser,
        logout
    }
})
