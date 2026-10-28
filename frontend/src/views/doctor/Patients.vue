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
.search-row { display: flex; gap: 12px; }
.doctors-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.doctor-card { display: flex; flex-direction: column; gap: 14px; }
.doc-top { display: flex; align-items: center; gap: 14px; }
.doc-avatar {
  width: 54px; height: 54px; border-radius: 50%; background: var(--teal);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 18px; flex-shrink: 0;
}
.doc-name { font-size: 16px; margin-bottom: 4px; }
.dept-badge {
  background: var(--light); color: var(--teal); padding: 3px 10px;
  border-radius: 12px; font-size: 12px; font-weight: 600;
}
.slots-title {
  font-size: 12px; font-weight: 700; color: var(--muted);
  text-transform: uppercase; letter-spacing: .4px; margin-bottom: 8px;
}
.slots-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.slot-btn {
  background: var(--light); border: 1.5px solid #d4e0ec; border-radius: 8px;
  padding: 8px 12px; cursor: pointer; font-size: 12px; text-align: center;
  font-family: 'Outfit', sans-serif; transition: all .18s; line-height: 1.4;
  color: var(--text); position: relative;
}
.slot-btn:hover { border-color: var(--teal); background: var(--teal); color: #fff; }
.slot-btn.selected { border-color: var(--teal); background: var(--teal); color: #fff; }
.slot-btn.booked {
  background: #f0f0f0; border-color: #ccc; color: #aaa;
  cursor: not-allowed; opacity: 0.7;
}
.booked-label {
  display: block; font-size: 10px; font-weight: 700;
  color: #e74c3c; margin-top: 2px; text-transform: uppercase;
}
.no-slots { font-size: 13px; color: var(--muted); font-style: italic; }

.btn-profile {
  margin-left: auto; background: var(--light); border: 1.5px solid #c7dff0;
  color: var(--teal); font-size: 16px; cursor: pointer;
  padding: 6px 10px; flex-shrink: 0; border-radius: 8px;
  display: flex; align-items: center; gap: 6px;
}
.btn-profile::after { content: 'Profile'; font-size: 12px; font-weight: 600; }
.btn-profile:hover { background: var(--teal); color: #fff; border-color: var(--teal); }
.btn-profile:hover { color: var(--navy); }
.modal-overlay { position: fixed; inset: 0; background: rgba(13,27,42,.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-box { background: #fff; border-radius: 12px; padding: 28px; width: 440px; max-width: 95vw; }
.profile-modal-top { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.doc-avatar.large { width: 70px; height: 70px; font-size: 24px; }
.profile-modal-body { display: flex; flex-direction: column; gap: 12px; }
.bio-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--teal); margin-bottom: 4px; }
.bio-text { font-size: 14px; line-height: 1.6; color: var(--text); }
.bio-text.muted { color: var(--muted); font-style: italic; }
.profile-detail { display: flex; align-items: center; gap: 8px; font-size: 14px; color: var(--muted); }
</style>
