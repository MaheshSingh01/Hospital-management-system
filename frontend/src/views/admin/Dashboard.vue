<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Admin Dashboard</h2>
      <p class="page-sub">Overview of hospital activity</p>
    </div>

    <div v-if="loading" class="loading">Loading dashboard…</div>

    <div v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">👨‍⚕️</div>
          <div class="stat-info">
            <div class="stat-num">{{ stats.total_doctors }}</div>
            <div class="stat-label">Total Doctors</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">🧑</div>
          <div class="stat-info">
            <div class="stat-num">{{ stats.total_patients }}</div>
            <div class="stat-label">Total Patients</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon teal">📅</div>
          <div class="stat-info">
            <div class="stat-num">{{ stats.total_appointments }}</div>
            <div class="stat-label">Total Appointments</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">⏳</div>
          <div class="stat-info">
            <div class="stat-num">{{ stats.pending_verification }}</div>
            <div class="stat-label">Pending Verification</div>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="card" style="margin-top: 28px;">
        <h3 style="margin-bottom: 16px;">Quick Actions</h3>
        <div class="action-grid">
          <router-link to="/admin/doctors" class="action-item">
            <span>👨‍⚕️</span> Manage Doctors
          </router-link>
          <router-link to="/admin/patients" class="action-item">
            <span>🧑</span> Manage Patients
          </router-link>
          <router-link to="/admin/appointments" class="action-item">
            <span>📅</span> View Appointments
          </router-link>
          <router-link to="/admin/departments" class="action-item">
            <span>🏥</span> Departments
          </router-link>
        </div>
      </div>
    </div>
  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'

export default {
  name: 'AdminDashboard',
  components: { Layout },
  data() {
    return {
      stats: {},
      loading: true,
      navItems: [
        { path: '/admin/dashboard',    icon: 'fa-solid fa-gauge',          label: 'Dashboard' },
        { path: '/admin/doctors',      icon: 'fa-solid fa-user-doctor',    label: 'Doctors' },
        { path: '/admin/patients',     icon: 'fa-solid fa-users',          label: 'Patients' },
        { path: '/admin/appointments', icon: 'fa-solid fa-calendar-check', label: 'Appointments' },
        { path: '/admin/departments',  icon: 'fa-solid fa-building-columns',label: 'Departments' },
      ]
    }
  },
  async created() {
    try {
      const { data } = await api.get('/admin/dashboard')
      this.stats = data
    } finally {
      this.loading = false
    }
  }
}
</script>
<style scoped>
.page-header { margin-bottom: 28px; }
.page-sub { color: var(--muted); margin-top: 4px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.stat-card { background: var(--white); border-radius: var(--radius); box-shadow: var(--shadow);
  padding: 22px; display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 52px; height: 52px; border-radius: 12px; display: flex;
  align-items: center; justify-content: center; font-size: 24px; }
.stat-icon.blue   { background: #dbeafe; }
.stat-icon.green  { background: #d1fae5; }
.stat-icon.teal   { background: #ccfbf1; }
.stat-icon.orange { background: #fef3c7; }
.stat-num { font-size: 28px; font-weight: 700; color: var(--navy); }
.stat-label { color: var(--muted); font-size: 13px; margin-top: 2px; }

.action-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.action-item {
  background: var(--light); border-radius: var(--radius); padding: 18px;
  text-align: center; color: var(--teal); font-weight: 600; font-size: 14px;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  transition: all .2s; border: 1.5px solid transparent;
}
.action-item:hover { border-color: var(--teal); background: #fff; box-shadow: var(--shadow); }
.action-item span { font-size: 28px; }

@media (max-width: 1000px) { .stats-grid, .action-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
