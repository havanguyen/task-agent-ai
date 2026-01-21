import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LoginView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/RegisterView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        component: () => import('@/layouts/MainLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                redirect: '/dashboard'
            },
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/DashboardView.vue')
            },
            {
                path: 'projects',
                name: 'Projects',
                component: () => import('@/views/ProjectsView.vue')
            },
            {
                path: 'projects/:id',
                name: 'ProjectDetail',
                component: () => import('@/views/ProjectDetailView.vue')
            },
            {
                path: 'tasks',
                name: 'Tasks',
                component: () => import('@/views/TasksView.vue')
            },
            {
                path: 'tasks/:id',
                name: 'TaskDetail',
                component: () => import('@/views/TaskDetailView.vue')
            },
            {
                path: 'notifications',
                name: 'Notifications',
                component: () => import('@/views/NotificationsView.vue')
            },
            {
                path: 'ai-chat',
                name: 'AIChat',
                component: () => import('@/views/AIChatView.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login')
    } else if (!to.meta.requiresAuth && authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
        next('/')
    } else {
        next()
    }
})

export default router
