<template>
  <v-container class="chat-page d-flex justify-center">
    <section class="chat-card">
      <!-- 標題列 -->
      <header class="chat-header d-flex align-center px-5 py-4">
        <div class="header-icon d-flex align-center justify-center me-3">
          <v-icon color="white" size="22">mdi-robot-happy-outline</v-icon>
        </div>
        <div>
          <div class="header-title">AI 對話助手</div>
          <div class="header-sub">
            <span class="status-dot" />只依據知識庫內容回答
          </div>
        </div>
      </header>

      <!-- 訊息區 -->
      <div ref="chatWindow" class="chat-content px-5 py-4">
        <div v-if="messages.length <= 1" class="empty-state">
          <div class="empty-icon d-flex align-center justify-center">
            <v-icon color="white" size="36">mdi-message-text-outline</v-icon>
          </div>
          <div class="empty-title">開始與 AI 助手對話吧</div>
          <div class="empty-sub">試試下面的問題，或直接輸入你想問的內容</div>
          <div class="d-flex flex-wrap justify-center ga-2 mt-4">
            <button
              v-for="s in suggestions"
              :key="s"
              class="suggest-chip"
              type="button"
              @click="useSuggestion(s)"
            >
              {{ s }}
            </button>
          </div>
        </div>

        <template v-for="(item, i) in messages" :key="i">
          <!-- 使用者 -->
          <div v-if="item.role === 'user'" class="msg-row user">
            <div class="bubble user-bubble">{{ item.content }}</div>
            <div class="msg-time">{{ item.time }}</div>
          </div>

          <!-- 助手 -->
          <div v-else class="msg-row assistant">
            <div class="avatar d-flex align-center justify-center">
              <v-icon color="white" size="18">mdi-robot-outline</v-icon>
            </div>
            <div class="assistant-col">
              <div class="bubble assistant-bubble">{{ item.content }}</div>
              <div class="msg-time">{{ item.time }}</div>
            </div>
          </div>
        </template>

        <!-- 載入中 -->
        <div v-if="loading" class="msg-row assistant">
          <div class="avatar d-flex align-center justify-center">
            <v-icon color="white" size="18">mdi-robot-outline</v-icon>
          </div>
          <div class="bubble assistant-bubble typing">
            <span /><span /><span />
          </div>
        </div>
      </div>

      <!-- 輸入區 -->
      <footer class="chat-input-area px-4 py-3">
        <div class="input-wrap d-flex align-center">
          <v-text-field
            v-model="input"
            autocomplete="off"
            class="flex-grow-1"
            density="comfortable"
            :disabled="loading"
            hide-details
            placeholder="請輸入訊息，按 Enter 送出"
            variant="plain"
            @keydown.enter="onEnter"
          />
          <v-btn
            class="send-btn"
            color="primary"
            :disabled="!input.trim() || loading"
            elevation="0"
            icon
            size="40"
            @click="send"
          >
            <v-icon size="20">mdi-send</v-icon>
          </v-btn>
        </div>
      </footer>
    </section>
  </v-container>
</template>

<script setup lang="ts">
  import { nextTick, ref, watch } from 'vue'
  import axios from 'axios'

  const input = ref('')
  const loading = ref(false)
  const chatWindow = ref(null)

  const suggestions = ['這個系統可以做什麼？', '知識庫怎麼管理？', '如何新增知識？']

  const getCurrentTime = () => {
    const now = new Date()
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  }

  const messages = ref([
    { role: 'assistant', content: '你好，我是 AI 助手，請問有什麼可以協助你？', time: getCurrentTime() },
  ])

  const scrollToBottom = async () => {
    await nextTick()
    if (chatWindow.value) {
      const element = chatWindow.value as HTMLElement
      element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' })
    }
  }

  watch(messages, () => {
    scrollToBottom()
  }, { deep: true })

  const send = async () => {
    const text = input.value.trim()
    if (!text || loading.value) return
    messages.value.push({ role: 'user', content: text, time: getCurrentTime() })
    input.value = ''
    loading.value = true

    try {
      await scrollToBottom()
      const res = await axios.post('/chat', { msg: text })
      messages.value.push({ role: 'assistant', content: res.data.message, time: getCurrentTime() })
    } catch (e) {
      console.error(e)
      messages.value.push({ role: 'assistant', content: '伺服器錯誤，請稍後再試。', time: getCurrentTime() })
    } finally {
      loading.value = false
      scrollToBottom()
    }
  }

  // 注音／拼音選字時按 Enter 不應送出
  const onEnter = (e: KeyboardEvent) => {
    if (e.isComposing) return
    send()
  }

  const useSuggestion = (text: string) => {
    input.value = text
    send()
  }
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 64px);
  padding-top: 24px;
  padding-bottom: 24px;
}

.chat-card {
  width: 100%;
  max-width: 820px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--c-line);
  border-radius: 24px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

/* header */
.chat-header {
  background: linear-gradient(120deg, var(--c-primary), #8a6cf7 60%, var(--c-accent));
  color: #fff;
}

.header-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
}

.header-title {
  font-size: 1.1rem;
  font-weight: 700;
}

.header-sub {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  opacity: 0.9;
}

.status-dot {
  width: 8px;
  height: 8px;
  margin-right: 6px;
  border-radius: 50%;
  background: #5cf2a6;
  box-shadow: 0 0 0 3px rgba(92, 242, 166, 0.3);
}

/* content */
.chat-content {
  flex: 1;
  overflow-y: auto;
  background: #fafbff;
  scrollbar-width: thin;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0 8px;
  text-align: center;
}

.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-accent));
  box-shadow: 0 10px 24px rgba(109, 94, 245, 0.3);
}

.empty-title {
  margin-top: 16px;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--c-ink);
}

.empty-sub {
  margin-top: 4px;
  font-size: 0.9rem;
  color: var(--c-muted);
}

.suggest-chip {
  padding: 8px 16px;
  border: 1px solid var(--c-line);
  border-radius: 999px;
  background: #fff;
  color: var(--c-primary);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
}

.suggest-chip:hover {
  background: var(--c-primary-soft);
  border-color: var(--c-primary);
  transform: translateY(-1px);
}

/* messages */
.msg-row {
  display: flex;
  margin: 14px 0;
}

.msg-row.user {
  flex-direction: column;
  align-items: flex-end;
}

.msg-row.assistant {
  align-items: flex-start;
  gap: 10px;
}

.assistant-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 78%;
}

.avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-accent));
}

.bubble {
  padding: 10px 16px;
  line-height: 1.65;
  font-size: 0.95rem;
  white-space: pre-wrap;
  word-break: break-word;
}

.user-bubble {
  max-width: 78%;
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  color: #fff;
  border-radius: 18px 18px 4px 18px;
  box-shadow: 0 6px 16px rgba(109, 94, 245, 0.28);
}

.assistant-bubble {
  background: #fff;
  color: var(--c-ink);
  border: 1px solid var(--c-line);
  border-radius: 18px 18px 18px 4px;
  box-shadow: 0 2px 8px rgba(40, 40, 100, 0.05);
}

.msg-time {
  margin-top: 4px;
  font-size: 0.72rem;
  color: var(--c-muted);
}

/* typing dots */
.typing {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 18px;
}

.typing span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--c-primary);
  animation: bounce 1.3s infinite ease-in-out both;
}

.typing span:nth-child(1) { animation-delay: -0.3s; }
.typing span:nth-child(2) { animation-delay: -0.15s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* input */
.chat-input-area {
  background: #fff;
  border-top: 1px solid var(--c-line);
}

.input-wrap {
  padding: 4px 8px 4px 16px;
  background: #f4f5fc;
  border: 1.5px solid transparent;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.input-wrap:focus-within {
  background: #fff;
  border-color: var(--c-primary);
  box-shadow: 0 0 0 4px rgba(109, 94, 245, 0.12);
}

.send-btn {
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark)) !important;
  color: #fff !important;
}

.send-btn:disabled {
  opacity: 0.45;
}

@media (max-width: 600px) {
  .chat-page {
    padding: 8px;
  }

  .chat-card {
    border-radius: 16px;
  }

  .assistant-col,
  .user-bubble {
    max-width: 88%;
  }
}
</style>
