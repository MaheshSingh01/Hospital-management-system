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
