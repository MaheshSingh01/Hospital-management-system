<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Patient Dashboard</h2>
      <p class="page-sub">Your health at a glance</p>
    </div>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else>
      <!-- Departments -->
      <div class="card" style="margin-bottom: 20px;">
        <h3 style="margin-bottom: 14px;">Available Departments</h3>
        <div class="dept-scroll">
          <div v-for="d in data.departments" :key="d.id" class="dept-chip">
            <span class="dept-name"> {{ d.name }}</span>
            <span v-if="d.description" class="dept-desc">{{ d.description }}</span>
          </div>
        </div>
      </div>

      <!-- Upcoming Appointments -->
      <div class="card" style="margin-bottom: 20px;">
        <div class="section-head">
          <h3>Upcoming Appointments</h3>
          <router-link to="/patient/doctors" class="btn btn-primary btn-sm">+ Book New</router-link>
        </div>
        <div v-if="data.upcoming_appointments?.length === 0" class="empty-state">
          <div class="icon">📅</div><p>No upcoming appointments</p>
        </div>
        <table v-else>
          <thead><tr><th>Doctor</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="a in data.upcoming_appointments" :key="a.id">
              <td>Dr. {{ a.doctor_name }}</td>
              <td>{{ a.scheduled_date }}</td>
              <td>{{ a.scheduled_time }}</td>
              <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
              <td>
                <div class="action-btns" v-if="a.booking_status === 'Booked'">
                  <router-link to="/patient/appointments" class="btn btn-outline btn-sm">Manage</router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Recent Past Appointments -->
      <div class="card">
        <div class="section-head">
          <h3>Recent History</h3>
          <router-link to="/patient/history" class="btn btn-outline btn-sm">View All</router-link>
        </div>
        <div v-if="data.past_appointments?.length === 0" class="empty-state">
          <div class="icon">📋</div><p>No past appointments yet</p>
        </div>
        <table v-else>
          <thead><tr><th>Doctor</th><th>Date</th><th>Status</th><th>Diagnosis</th></tr></thead>
          <tbody>
            <tr v-for="a in data.past_appointments" :key="a.id">
              <td>Dr. {{ a.doctor_name }}</td>
              <td>{{ a.scheduled_date }}</td>
              <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
              <td>{{ a.treatment?.diagnosis_text || '—' }}</td>
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
  name: 'PatientDashboard',
  components: { Layout },
  data() {
    return {
      data: {}, loading: true,
      navItems: [
        { path: '/patient/dashboard',    icon: 'fa-solid fa-gauge',         label: 'Dashboard' },
        { path: '/patient/doctors',      icon: 'fa-solid fa-stethoscope',   label: 'Find Doctors' },
        { path: '/patient/appointments', icon: 'fa-solid fa-calendar-check',label: 'Appointments' },
        { path: '/patient/history',      icon: 'fa-solid fa-clock-rotate-left', label: 'History' },
        { path: '/patient/profile',      icon: 'fa-solid fa-circle-user',   label: 'Profile' },
      ]
    }
  },
  async created() {
    const { data } = await api.get('/patient/dashboard')
    this.data = data; this.loading = false
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-sub { color: var(--muted); margin-top: 4px; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.dept-scroll { display: flex; flex-wrap: wrap; gap: 10px; }
.dept-chip {
  background: var(--light); color: var(--teal); padding: 10px 16px;
  border-radius: 12px; font-size: 13px; font-weight: 500;
  border: 1.5px solid #c7dff0;
  display: flex; flex-direction: column; align-items: flex-start;
  min-width: 140px;
}
.dept-name { font-weight: 600; font-size: 13px; }
.dept-desc { font-size: 11px; color: var(--muted); margin-top: 3px; }
.action-btns { display: flex; gap: 6px; }
</style>
