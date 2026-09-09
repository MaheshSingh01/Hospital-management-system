<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>My Patients</h2>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">Loading patients…</div>
      <div v-else-if="patients.length === 0" class="empty-state">
        <div class="icon">🧑</div><p>No patients assigned yet</p>
      </div>
      <table v-else>
        <thead><tr><th>ID</th><th>Name</th><th>Contact</th><th>Address</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="p in patients" :key="p.id">
            <td><code>{{ p.display_id }}</code></td>
            <td><strong>{{ p.full_name }}</strong></td>
            <td>{{ p.contact_num || '—' }}</td>
            <td>{{ p.home_address || '—' }}</td>
            <td><button class="btn btn-outline btn-sm" @click="viewHistory(p)">📋 Full History</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Patient History Modal -->
    <div v-if="showHistory" class="modal-overlay" @click.self="showHistory = false">
      <div class="modal-box large">
        <div class="history-header">
          <div>
            <h3>{{ selectedPatient?.full_name }}</h3>
            <p class="modal-sub">{{ selectedPatient?.display_id }} · {{ selectedPatient?.contact_num }}</p>
          </div>
          <button class="close-btn" @click="showHistory = false">✕</button>
        </div>

        <div v-if="historyLoading" class="loading">Loading history…</div>
        <div v-else-if="history.length === 0" class="empty-state">
          <div class="icon">📋</div><p>No appointment history yet</p>
        </div>
        <div v-else class="history-list">
          <div v-for="a in history" :key="a.id" class="history-item" :class="`status-${a.booking_status.toLowerCase()}`">
            <div class="history-top">
              <div class="history-date">
                <strong>{{ a.scheduled_date }}</strong> at {{ a.scheduled_time }}
              </div>
              <span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span>
            </div>
            <div v-if="a.treatment" class="treatment-box">
              <div class="treat-row"><span class="treat-label">Diagnosis:</span> {{ a.treatment.diagnosis_text }}</div>
              <div class="treat-row"><span class="treat-label">Prescription:</span> {{ a.treatment.prescription_text }}</div>
              <div v-if="a.treatment.follow_up_notes" class="treat-row">
                <span class="treat-label">Notes:</span> {{ a.treatment.follow_up_notes }}
              </div>
              <div v-if="a.treatment.next_visit_date" class="treat-row">
                <span class="treat-label">Next Visit:</span> {{ a.treatment.next_visit_date }}
              </div>
            </div>
            <div v-else-if="a.booking_status === 'Booked'" class="no-treatment">
              <em>Treatment not yet recorded</em>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'DoctorPatients',
  components: { Layout },
  data() {
    return {
      patients: [], loading: true,
      showHistory: false, historyLoading: false,
      selectedPatient: null, history: [],
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
    const { data } = await api.get('/doctor/patients')
    this.patients = data; this.loading = false
  },
  methods: {
    async viewHistory(patient) {
      this.selectedPatient = patient
      this.history = []; this.historyLoading = true; this.showHistory = true
      const { data } = await api.get(`/doctor/patients/${patient.id}/history`)
      this.history = data.history; this.historyLoading = false
    }
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 20px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(13,27,42,.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-box { background: #fff; border-radius: 12px; padding: 28px; width: 620px; max-width: 95vw; max-height: 88vh; overflow-y: auto; }
.modal-box.large { width: 680px; }
.history-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.modal-sub { color: var(--muted); font-size: 13px; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--muted); padding: 4px 8px; }
.history-list { display: flex; flex-direction: column; gap: 12px; }
.history-item { border: 1.5px solid #e2eaf3; border-radius: 8px; padding: 14px; }
.history-item.status-completed { border-color: #a7f3d0; }
.history-item.status-cancelled { border-color: #fecaca; }
.history-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.history-date { font-size: 14px; }
.treatment-box { background: #f8fbff; border-radius: 6px; padding: 12px; }
.treat-row { font-size: 13px; margin-bottom: 6px; }
.treat-label { font-weight: 600; color: var(--teal); margin-right: 6px; }
.no-treatment { font-size: 13px; color: var(--muted); font-style: italic; }
</style>
