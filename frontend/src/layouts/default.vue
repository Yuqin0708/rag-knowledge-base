<template>
  <v-app class="app-shell">
    <v-app-bar class="app-bar" flat height="64">
      <div class="brand d-flex align-center ms-4">
        <div class="brand-logo d-flex align-center justify-center me-3">
          <v-icon color="white" size="20">mdi-book-search-outline</v-icon>
        </div>
        <span class="brand-name">RAG</span>
        <span class="brand-sub d-none d-sm-inline ms-2">知識庫問答</span>
      </div>
      <v-spacer />
      <nav class="nav-pills me-4">
        <router-link class="nav-pill" :class="{ active: isActive('/chat') }" to="/chat">
          <v-icon size="18" start>mdi-chat-processing-outline</v-icon>對話
        </router-link>
        <router-link class="nav-pill" :class="{ active: isActive('/knowledge') }" to="/knowledge">
          <v-icon size="18" start>mdi-database-outline</v-icon>知識庫
        </router-link>
      </nav>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
  import { useRoute } from 'vue-router'

  const route = useRoute()
  const isActive = (path: string) => route.path.startsWith(path)
</script>

<style>
:root {
  --c-primary: #6d5ef5;
  --c-primary-dark: #5445d8;
  --c-primary-soft: #efedff;
  --c-accent: #22c1c3;
  --c-ink: #1f2340;
  --c-muted: #7b809a;
  --c-line: #e6e8f2;
  --c-danger: #ef5b5b;
  --shadow-card: 0 10px 40px rgba(60, 50, 140, 0.10);
}

.app-shell {
  background:
    radial-gradient(900px 500px at 8% -10%, #e4e0ff 0%, transparent 60%),
    radial-gradient(800px 500px at 100% 0%, #d6f6f6 0%, transparent 55%),
    #f7f8fd !important;
  color: var(--c-ink);
}
</style>

<style scoped>
.app-bar {
  background: rgba(255, 255, 255, 0.75) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--c-line);
}

.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  background: linear-gradient(135deg, var(--c-primary), var(--c-accent));
  box-shadow: 0 6px 14px rgba(109, 94, 245, 0.35);
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--c-ink);
}

.brand-sub {
  color: var(--c-muted);
  font-size: 0.9rem;
}

.nav-pills {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--c-primary-soft);
  border-radius: 999px;
}

.nav-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 999px;
  color: var(--c-muted);
  font-weight: 600;
  font-size: 0.92rem;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-pill:hover {
  color: var(--c-primary);
}

.nav-pill.active {
  background: #fff;
  color: var(--c-primary);
  box-shadow: 0 2px 8px rgba(109, 94, 245, 0.18);
}
</style>
