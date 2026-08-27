<template>
  <div class="layout">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <i class="fa-solid fa-heart-pulse logo-icon"></i>
        <span v-if="!sidebarCollapsed" class="logo-text">Nivea Health Care</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <i :class="item.icon" class="nav-icon"></i>
          <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="nav-item logout-btn" @click="handleLogout">
          <i class="fa-solid fa-right-from-bracket nav-icon"></i>
          <span v-if="!sidebarCollapsed" class="nav-label">Logout</span>
        </button>
      </div>
    </aside>

    <div class="main-wrapper">
      <header class="top-bar">
        <button class="toggle-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <i class="fa-solid fa-bars"></i>
        </button>
        <div class="top-bar-info">
          <span class="role-badge">{{ roleLabel }}</span>
          <span class="user-name">{{ userName }}</span>
        </div>
      </header>
      <main class="page-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppLayout',
  props: {
    navItems: { type: Array, required: true }
  },
  data() {
    return { sidebarCollapsed: false }
  },
  computed: {
    userName() { return localStorage.getItem('hms_name') || 'User' },
    roleLabel() {
      const map = { admin: 'Admin', doctor: 'Doctor', patient: 'Patient' }
      return map[localStorage.getItem('hms_role')] || 'User'
    }
  },
  methods: {
    handleLogout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }

.sidebar {
  width: 240px; background: var(--navy); display: flex; flex-direction: column;
  transition: width .25s ease; flex-shrink: 0; position: sticky; top: 0; height: 100vh;
}
.sidebar.collapsed { width: 64px; }

.sidebar-header {
  display: flex; align-items: center; gap: 12px;
  padding: 24px 20px 20px; border-bottom: 1px solid rgba(255,255,255,.08);
}
.logo-icon { font-size: 22px; color: #fff; flex-shrink: 0; }
.logo-text { font-family: 'Times New Roman', Times, serif; color: #fff; font-size: 17px; white-space: nowrap; font-weight: 600; }

.sidebar-nav { flex: 1; padding: 16px 10px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; }

.nav-item {
  display: flex; align-items: center; gap: 14px; padding: 11px 12px;
  border-radius: 8px; color: rgba(255,255,255,.65); cursor: pointer;
  text-decoration: none; transition: all .18s; border: none; background: none;
  font-family: 'Times New Roman', Times, serif; font-size: 14px; width: 100%;
}
.nav-item:hover { background: rgba(255,255,255,.08); color: #fff; }
.nav-item.active { background: var(--teal); color: #fff; }
.nav-icon { font-size: 16px; flex-shrink: 0; width: 20px; text-align: center; }
.nav-label { white-space: nowrap; }

.sidebar-footer { padding: 12px 10px; border-top: 1px solid rgba(255,255,255,.08); }
.logout-btn { color: rgba(255,255,255,.5); }
.logout-btn:hover { color: var(--danger) !important; background: rgba(224,92,92,.12) !important; }

.main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.top-bar {
  background: var(--white); padding: 14px 28px; display: flex;
  align-items: center; justify-content: space-between;
  border-bottom: 1px solid #e2eaf3; box-shadow: 0 1px 6px rgba(13,27,42,.06);
}
.toggle-btn {
  background: none; border: none; font-size: 18px; cursor: pointer;
  color: var(--muted); padding: 6px 10px; border-radius: 6px;
}
.toggle-btn:hover { background: var(--light); color: var(--navy); }
.top-bar-info { display: flex; align-items: center; gap: 12px; }
.role-badge {
  background: var(--light); color: var(--teal); padding: 4px 12px;
  border-radius: 20px; font-size: 13px; font-weight: 600; border: 1px solid #c7dff0;
}
.user-name { font-weight: 600; color: var(--navy); }

.page-content { flex: 1; padding: 28px; overflow-y: auto; }
</style>
