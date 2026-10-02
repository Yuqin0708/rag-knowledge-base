<template>
  <v-container class="kb-page" max-width="1100">
    <!-- 頁首 -->
    <div class="page-head d-flex align-center flex-wrap ga-4 mb-6">
      <div class="head-icon d-flex align-center justify-center">
        <v-icon color="white" size="26">mdi-database-outline</v-icon>
      </div>
      <div class="flex-grow-1">
        <h1 class="page-title">知識庫管理</h1>
        <div class="page-sub">AI 只會根據這裡的內容回答問題</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ knowledgeList.length }}</div>
        <div class="stat-label">筆知識</div>
      </div>
    </div>

    <div class="kb-grid">
      <!-- 新增 -->
      <section class="panel add-panel">
        <div class="panel-title">
          <span class="dot add" />新增知識
        </div>
        <v-textarea
          v-model="content"
          auto-grow
          class="field"
          :disabled="loading"
          hide-details
          max-rows="10"
          placeholder="輸入任何想讓 AI 助手學習的資訊..."
          rows="5"
          variant="outlined"
        />
        <div class="d-flex align-center justify-space-between mt-2 mb-3">
          <span class="char-count">{{ content.length }} 字</span>
          <button
            v-if="content"
            class="link-btn"
            type="button"
            @click="content = ''"
          >
            清除
          </button>
        </div>
        <v-btn
          block
          class="primary-btn"
          :disabled="!content.trim() || loading"
          elevation="0"
          height="46"
          :loading="loading"
          @click="addKnowledge"
        >
          <v-icon start>mdi-plus-circle-outline</v-icon>
          新增至知識庫
        </v-btn>
      </section>

      <!-- 列表 -->
      <section class="panel list-panel">
        <div class="panel-title">
          <span class="dot list" />知識庫內容
        </div>

        <v-text-field
          v-model="search"
          class="field mb-3"
          clearable
          density="comfortable"
          hide-details
          placeholder="搜尋知識內容..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
        />

        <div class="list-meta mb-3">
          <template v-if="search">
            找到 <b>{{ filteredList.length }}</b> / {{ knowledgeList.length }} 筆
          </template>
          <template v-else>
            共 <b>{{ knowledgeList.length }}</b> 筆
          </template>
        </div>

        <div v-if="filteredList.length" class="knowledge-list">
          <transition-group name="list">
            <article
              v-for="item in filteredList"
              :key="item.id"
              class="k-item"
            >
              <div v-if="editId !== item.id" class="d-flex align-start ga-3">
                <div class="k-bullet d-flex align-center justify-center">
                  <v-icon color="white" size="16">mdi-lightbulb-on-outline</v-icon>
                </div>
                <div class="k-text flex-grow-1">{{ item.content }}</div>
                <div class="k-actions d-flex">
                  <v-btn
                    density="comfortable"
                    icon
                    size="small"
                    variant="text"
                    @click="startEdit(item)"
                  >
                    <v-icon color="primary" size="20">mdi-pencil-outline</v-icon>
                    <v-tooltip activator="parent" location="top">編輯</v-tooltip>
                  </v-btn>
                  <v-btn
                    density="comfortable"
                    icon
                    size="small"
                    variant="text"
                    @click="deleteKnowledge(item.id)"
                  >
                    <v-icon color="#ef5b5b" size="20">mdi-trash-can-outline</v-icon>
                    <v-tooltip activator="parent" location="top">刪除</v-tooltip>
                  </v-btn>
                </div>
              </div>

              <div v-else>
                <v-textarea
                  v-model="editContent"
                  auto-grow
                  class="field"
                  hide-details
                  rows="3"
                  variant="outlined"
                />
                <div class="d-flex justify-end ga-2 mt-3">
                  <v-btn class="ghost-btn" elevation="0" variant="outlined" @click="cancelEdit">
                    取消
                  </v-btn>
                  <v-btn
                    class="primary-btn"
                    :disabled="!editContent.trim() || loading"
                    elevation="0"
                    @click="confirmEdit(item.id)"
                  >
                    <v-icon start>mdi-content-save-outline</v-icon>
                    儲存
                  </v-btn>
                </div>
              </div>
            </article>
          </transition-group>
        </div>

        <div v-else class="empty">
          <v-icon color="#c9c4fb" size="56">mdi-text-box-search-outline</v-icon>
          <div class="empty-text">
            {{ search ? '查無符合的知識資料' : '知識庫中尚無資料' }}
          </div>
          <v-btn
            v-if="search"
            class="mt-2"
            color="primary"
            variant="text"
            @click="search = ''"
          >
            清除搜尋條件
          </v-btn>
        </div>
      </section>
    </div>

    <!-- 提示訊息 -->
    <v-snackbar
      v-model="showSuccess"
      color="#1fb978"
      location="top"
      rounded="pill"
      :timeout="3000"
    >
      <div class="d-flex align-center">
        <v-icon color="white" start>mdi-check-circle-outline</v-icon>
        <span class="font-weight-medium">{{ successMsg }}</span>
      </div>
    </v-snackbar>

    <v-snackbar
      v-model="showError"
      color="#ef5b5b"
      location="top"
      rounded="pill"
      :timeout="3000"
    >
      <div class="d-flex align-center">
        <v-icon color="white" start>mdi-alert-circle-outline</v-icon>
        <span class="font-weight-medium">{{ errorMsg }}</span>
      </div>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref, watch } from 'vue'
  import axios from 'axios'

  interface KnowledgeItem {
    id: string
    content: string
  }

  const content = ref('')
  const loading = ref(false)
  const knowledgeList = ref<KnowledgeItem[]>([])
  const search = ref('')
  const successMsg = ref('')
  const errorMsg = ref('')
  const editId = ref('')
  const editContent = ref('')
  const showSuccess = ref(false)
  const showError = ref(false)

  watch(successMsg, newVal => {
    if (newVal) {
      showSuccess.value = true
      setTimeout(() => {
        showSuccess.value = false
        successMsg.value = ''
      }, 3000)
    }
  })

  watch(errorMsg, newVal => {
    if (newVal) {
      showError.value = true
      setTimeout(() => {
        showError.value = false
        errorMsg.value = ''
      }, 3000)
    }
  })

  // 搜尋功能
  const filteredList = computed(() =>
    knowledgeList.value.filter(item =>
      item.content.toLowerCase().includes((search.value ?? '').trim().toLowerCase())
    )
  )

  const fetchKnowledge = async () => {
    try {
      loading.value = true
      const res = await axios.get('/knowledge')
      knowledgeList.value = res.data.items || []
    } catch {
      errorMsg.value = '無法載入知識庫，請重試'
      knowledgeList.value = []
    } finally {
      loading.value = false
    }
  }

  const addKnowledge = async () => {
    if (!content.value.trim()) return
    loading.value = true
    try {
      await axios.post('/knowledge', { msg: content.value })
      successMsg.value = '知識已成功新增！'
      content.value = ''
      await fetchKnowledge()
    } catch {
      errorMsg.value = '新增失敗，請稍後再試'
    } finally {
      loading.value = false
    }
  }

  const deleteKnowledge = async (id: string) => {
    if (!confirm('確定要刪除這筆知識嗎？')) return
    loading.value = true
    try {
      await axios.delete(`/knowledge/${id}`)
      successMsg.value = '知識已成功刪除'
      await fetchKnowledge()
    } catch {
      errorMsg.value = '刪除失敗，請重試'
    } finally {
      loading.value = false
    }
  }

  const startEdit = (item: KnowledgeItem) => {
    editId.value = item.id
    editContent.value = item.content
  }

  const cancelEdit = () => {
    editId.value = ''
    editContent.value = ''
  }

  const confirmEdit = async (id: string) => {
    loading.value = true
    try {
      await axios.put(`/knowledge/${id}`, { content: editContent.value })
      successMsg.value = '知識已成功更新'
      cancelEdit()
      await fetchKnowledge()
    } catch {
      errorMsg.value = '更新失敗，請重試'
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    fetchKnowledge()
  })
</script>

<style scoped>
.kb-page {
  padding-top: 28px;
  padding-bottom: 40px;
}

/* head */
.head-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-accent));
  box-shadow: 0 8px 20px rgba(109, 94, 245, 0.32);
}

.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  line-height: 1.2;
  color: var(--c-ink);
}

.page-sub {
  margin-top: 2px;
  color: var(--c-muted);
  font-size: 0.92rem;
}

.stat-card {
  padding: 8px 22px;
  text-align: center;
  background: #fff;
  border: 1px solid var(--c-line);
  border-radius: 16px;
  box-shadow: var(--shadow-card);
}

.stat-num {
  font-size: 1.6rem;
  font-weight: 800;
  line-height: 1.1;
  color: var(--c-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--c-muted);
}

/* layout */
.kb-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
  align-items: start;
}

.panel {
  padding: 22px;
  background: #fff;
  border: 1px solid var(--c-line);
  border-radius: 22px;
  box-shadow: var(--shadow-card);
}

.add-panel {
  position: sticky;
  top: 84px;
}

.panel-title {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--c-ink);
}

.dot {
  width: 10px;
  height: 10px;
  margin-right: 10px;
  border-radius: 50%;
}

.dot.add { background: var(--c-primary); }
.dot.list { background: var(--c-accent); }

.field :deep(.v-field) {
  border-radius: 14px;
  background: #fafbff;
}

.char-count {
  font-size: 0.78rem;
  color: var(--c-muted);
}

.link-btn {
  border: 0;
  background: none;
  color: var(--c-primary);
  font-size: 0.82rem;
  cursor: pointer;
}

.primary-btn {
  border-radius: 14px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-primary-dark)) !important;
  color: #fff !important;
  font-weight: 600;
  letter-spacing: 0.02em;
  box-shadow: 0 8px 18px rgba(109, 94, 245, 0.3);
}

.primary-btn:disabled {
  opacity: 0.45;
  box-shadow: none;
}

.ghost-btn {
  border-radius: 14px;
  border-color: var(--c-line);
  color: var(--c-muted);
}

/* list */
.list-meta {
  font-size: 0.85rem;
  color: var(--c-muted);
}

.list-meta b {
  color: var(--c-primary);
}

.knowledge-list {
  max-height: calc(100vh - 340px);
  min-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-width: thin;
}

.k-item {
  margin-bottom: 12px;
  padding: 14px 14px 14px 16px;
  background: #fff;
  border: 1px solid var(--c-line);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.k-item:hover {
  border-color: #cfc9fb;
  box-shadow: 0 8px 22px rgba(109, 94, 245, 0.12);
  transform: translateY(-1px);
}

.k-bullet {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-accent));
}

.k-text {
  padding-top: 3px;
  line-height: 1.65;
  font-size: 0.95rem;
  white-space: pre-wrap;
  word-break: break-word;
}

.k-actions {
  opacity: 0.35;
  transition: opacity 0.2s ease;
}

.k-item:hover .k-actions {
  opacity: 1;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0;
}

.empty-text {
  margin-top: 8px;
  color: var(--c-muted);
}

/* transition */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(16px);
}

@media (max-width: 860px) {
  .kb-grid {
    grid-template-columns: 1fr;
  }

  .add-panel {
    position: static;
  }

  .knowledge-list {
    max-height: none;
  }

  .k-actions {
    opacity: 1;
  }
}
</style>
