<template>
  <Layout :nav-items="navItems">
    <div v-if="loading" class="loading">Loading…</div>
    <div v-else>
      <div class="page-header">
        <div>
          <h2>{{ data.welcome }}</h2>
          <p class="page-sub">Here's your schedule at a glance</p>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon blue">📅</div>
          <div><div class="stat-num">{{ data.todays_count }}</div><div class="stat-label">Today's Appointments</div></div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon teal">📆</div>
          <div><div class="stat-num">{{ data.week_count }}</div><div class="stat-label">This Week</div></div>
        </div>
      </div>

      <div class="card" style="margin-top: 24px;">
        <h3 style="margin-bottom: 16px;">Today's Schedule</h3>
        <div v-if="data.todays_appointments && data.todays_appointments.length === 0" class="empty-state">
          <div class="icon">☀️</div><p>No appointments scheduled for today</p>
        </div>
        <table v-else>
          <thead><tr><th>Time</th><th>Patient</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="a in data.todays_appointments" :key="a.id">
              <td><strong>{{ a.scheduled_time }}</strong></td>
              <td>{{ a.patient_name }}</td>
              <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
              <td><router-link to="/doctor/appointments" class="btn btn-outline btn-sm">Manage</router-link></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'DoctorDashboard',
  components: { Layout },
  data() {
    return {
      data: {}, loading: true,
      navItems: [
        { path: '/doctor/dashboard',    icon: 'fa-solid fa-gauge',         label: 'Dashboard' },
        { path: '/doctor/appointments', icon: 'fa-solid fa-calendar-check',label: 'Appointments' },
        { path: '/doctor/patients',     icon: 'fa-solid fa-users',         label: 'My Patients' },
        { path: '/doctor/schedule',     icon: 'fa-solid fa-clock',         label: 'Schedule' },
        { path: '/doctor/profile',      icon: 'fa-solid fa-circle-user',   label: 'Profile' },
      ]
    }
  },
  async created() {
    const { data } = await api.get('/doctor/dashboard')
    this.data = data; this.loading = false
  }
}
</script>
