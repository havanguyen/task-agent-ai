<template>
  <div class="ai-chat-view">
    <el-card class="chat-card">
      <!-- Chat Header -->
      <div class="chat-header">
        <div class="header-info">
          <div class="ai-icon">
            <el-icon size="28"><ChatDotRound /></el-icon>
          </div>
          <div class="header-text">
            <h3>AI Task Assistant</h3>
            <span class="status-badge">
              <span class="status-dot"></span> Online
            </span>
          </div>
        </div>
        <el-button type="info" size="small" @click="clearMessages" :icon="Delete" plain>
          Clear Chat
        </el-button>
      </div>

      <!-- Chat Messages -->
      <div class="chat-messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-icon">
            <el-icon size="64"><ChatDotRound /></el-icon>
          </div>
          <h2>Hello! I'm your AI Assistant</h2>
          <p class="subtitle">I can help you manage tasks efficiently</p>
          
          <div class="quick-actions">
            <div class="action-card" @click="sendQuickMessage('Create an task go to the gym, due tomorrow')">
              <el-icon size="24"><Plus /></el-icon>
              <span>Create Task</span>
            </div>
            <div class="action-card" @click="sendQuickMessage('Show me all my tasks')">
              <el-icon size="24"><List /></el-icon>
              <span>List Tasks</span>
            </div>
            <div class="action-card" @click="sendQuickMessage('Show project statistics')">
              <el-icon size="24"><DataAnalysis /></el-icon>
              <span>Project Stats</span>
            </div>
            <div class="action-card" @click="sendQuickMessage('What can you help me with?')">
              <el-icon size="24"><QuestionFilled /></el-icon>
              <span>Help</span>
            </div>
          </div>
        </div>

        <transition-group name="message" tag="div">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message"
            :class="msg.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="msg.role === 'user'" :size="36" class="user-avatar">
                {{ userInitials }}
              </el-avatar>
              <div v-else class="ai-avatar-wrapper">
                <el-icon size="20"><ChatDotRound /></el-icon>
              </div>
            </div>
            <div class="message-bubble">
              <div class="message-text">{{ msg.content }}</div>
              <div v-if="msg.actions?.length" class="message-actions">
                <el-tag
                  v-for="action in msg.actions"
                  :key="action.action"
                  :type="action.success ? 'success' : 'danger'"
                  size="small"
                  effect="dark"
                >
                  <el-icon><Check /></el-icon>
                  {{ action.details }}
                </el-tag>
              </div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>
        </transition-group>

        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <div class="ai-avatar-wrapper">
              <el-icon size="20"><ChatDotRound /></el-icon>
            </div>
          </div>
          <div class="message-bubble typing">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- Chat Input -->
      <div class="chat-input-wrapper">
        <el-input
          v-model="inputMessage"
          placeholder="Type your message here..."
          size="large"
          @keyup.enter="sendMessage"
          :disabled="loading"
        >
          <template #prefix>
            <el-icon><Edit /></el-icon>
          </template>
        </el-input>
        <el-button 
          type="primary" 
          size="large"
          @click="sendMessage" 
          :loading="loading"
          :disabled="!inputMessage.trim()"
          class="send-button"
        >
          <el-icon v-if="!loading"><Promotion /></el-icon>
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'

const authStore = useAuthStore()
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref()

const userInitials = computed(() => {
  const name = authStore.user?.full_name || 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

function formatTime(timestamp) {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function clearMessages() {
  messages.value = []
}

async function sendQuickMessage(text) {
  inputMessage.value = text
  await sendMessage()
}

async function sendMessage() {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  messages.value.push({ role: 'user', content: message, timestamp: new Date() })
  inputMessage.value = ''
  loading.value = true

  await nextTick()
  scrollToBottom()

  try {
    const response = await http.post('/agent/chat', { message })
    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      actions: response.data.actions,
      timestamp: new Date()
    })
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, an error occurred. Please try again.',
      timestamp: new Date()
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-chat-view {
  height: calc(100vh - 140px);
  padding: 0;
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, #1e1e2e 0%, #181825 100%);
  border: 1px solid #313244;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

:deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

/* Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: rgba(49, 50, 68, 0.5);
  border-bottom: 1px solid #313244;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border-radius: 14px;
  color: #1e1e2e;
}

.header-text h3 {
  margin: 0 0 4px;
  color: #cdd6f4;
  font-size: 16px;
  font-weight: 600;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #a6e3a1;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #a6e3a1;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Messages Area */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scrollbar-width: thin;
  scrollbar-color: #313244 transparent;
}

/* Welcome Section */
.welcome-section {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border-radius: 28px;
  color: #1e1e2e;
}

.welcome-section h2 {
  color: #cdd6f4;
  font-size: 24px;
  margin: 0 0 8px;
}

.welcome-section .subtitle {
  color: #6c7086;
  margin: 0 0 32px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 400px;
  margin: 0 auto;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 16px;
  background: rgba(49, 50, 68, 0.5);
  border: 1px solid #313244;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #a6adc8;
}

.action-card:hover {
  background: rgba(137, 180, 250, 0.1);
  border-color: #89b4fa;
  color: #89b4fa;
  transform: translateY(-2px);
}

/* Message Styles */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.user-avatar {
  background: linear-gradient(135deg, #f38ba8 0%, #fab387 100%);
  color: #1e1e2e;
  font-weight: 600;
  font-size: 14px;
}

.ai-avatar-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border-radius: 12px;
  color: #1e1e2e;
}

.message-bubble {
  max-width: 70%;
  padding: 14px 18px;
  border-radius: 18px;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #89b4fa 0%, #74c7ec 100%);
  color: #1e1e2e;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: rgba(49, 50, 68, 0.8);
  color: #cdd6f4;
  border-bottom-left-radius: 4px;
}

.message-text {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 14px;
}

.message-time {
  font-size: 11px;
  color: inherit;
  opacity: 0.6;
  margin-top: 6px;
  text-align: right;
}

.message-actions {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* Typing Indicator */
.message-bubble.typing {
  display: flex;
  gap: 6px;
  padding: 16px 20px;
}

.message-bubble.typing .dot {
  width: 10px;
  height: 10px;
  background: #6c7086;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

/* Input Area */
.chat-input-wrapper {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  background: rgba(24, 24, 37, 0.9);
  border-top: 1px solid #313244;
}

:deep(.el-input__wrapper) {
  background: #11111b;
  border: 1px solid #313244;
  border-radius: 12px;
  box-shadow: none !important;
  padding: 0 16px;
}

:deep(.el-input__wrapper:focus-within) {
  border-color: #89b4fa;
}

:deep(.el-input__inner) {
  color: #cdd6f4;
  font-size: 14px;
}

:deep(.el-input__prefix) {
  color: #6c7086;
}

.send-button {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #89b4fa 0%, #cba6f7 100%);
  border: none;
}

.send-button:hover {
  background: linear-gradient(135deg, #74c7ec 0%, #89b4fa 100%);
}

.send-button:disabled {
  background: #313244;
  opacity: 0.5;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .ai-chat-view {
    height: calc(100vh - 100px);
  }
  
  .chat-card {
    border-radius: 12px;
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .ai-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
  }
  
  .header-text h3 {
    font-size: 14px;
  }
  
  .chat-messages {
    padding: 16px;
  }
  
  .welcome-section {
    padding: 24px 16px;
  }
  
  .welcome-icon {
    width: 72px;
    height: 72px;
    border-radius: 20px;
  }
  
  .welcome-section h2 {
    font-size: 20px;
  }
  
  .quick-actions {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  
  .action-card {
    padding: 14px 12px;
  }
  
  .message-bubble {
    max-width: 85%;
    padding: 12px 14px;
  }
  
  .chat-input-wrapper {
    padding: 12px 16px;
    gap: 10px;
  }
  
  .send-button {
    width: 44px;
    height: 44px;
  }
}
</style>
