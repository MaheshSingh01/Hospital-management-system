<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Treatment History</h2>
      <div style="display:flex; gap:10px;">
        <button class="btn btn-outline" @click="triggerExport" :disabled="exporting">
          {{ exporting ? 'Queuing…' : '⬇ Export as CSV' }}
        </button>
        <button v-if="exportDone" class="btn btn-success" @click="downloadCsv">
          ⬇ Download CSV
        </button>
      </div>
    </div>

    <div v-if="exportMsg" class="alert alert-info">{{ exportMsg }}</div>
    <div v-if="loading" class="loading">Loading history…</div>
    <div v-else-if="history.length === 0" class="empty-state card">
      <div class="icon">📋</div><p>No appointment history found</p>
    </div>
    <div v-else class="history-list">
      <div v-for="a in history" :key="a.id" class="history-card card">
        <div class="history-top">
          <div class="history-meta">
            <span class="doctor-name">Dr. {{ a.doctor_name }}</span>
            <span class="dept-name" v-if="a.doctor_dept">· {{ a.doctor_dept }}</span>
          </div>
          <div class="history-right">
            <span class="date-chip">{{ a.scheduled_date }} at {{ a.scheduled_time }}</span>
            <span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span>
          </div>
        </div>

        <div v-if="a.treatment" class="treatment-section">
          <div class="treat-grid">
            <div class="treat-block">
              <div class="treat-label">Diagnosis</div>
              <div class="treat-value">{{ a.treatment.diagnosis_text }}</div>
            </div>
            <div class="treat-block">
              <div class="treat-label">Prescription</div>
              <div class="treat-value">{{ a.treatment.prescription_text }}</div>
            </div>
            <div v-if="a.treatment.follow_up_notes" class="treat-block full">
              <div class="treat-label">Doctor's Notes</div>
              <div class="treat-value">{{ a.treatment.follow_up_notes }}</div>
            </div>
            <div v-if="a.treatment.next_visit_date" class="treat-block">
              <div class="treat-label">Next Visit</div>
              <div class="treat-value">{{ a.treatment.next_visit_date }}</div>
            </div>
          </div>
        </div>

        <div v-else-if="a.booking_status === 'Booked'" class="pending-tag">
          Treatment to be recorded after visit
        </div>
        <div v-else-if="a.booking_status === 'Cancelled'" class="cancelled-tag">
          Appointment was cancelled
        </div>
      </div>
    </div>
  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'PatientHistory',
  components: { Layout },
  data() {
    return {
      history: [], loading: true, exporting: false, exportMsg: '', exportDone: false,
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
    const { data } = await api.get('/patient/history')
    this.history = data; this.loading = false
  },
  methods: {
    async triggerExport() {
      this.exporting = true
      this.exportDone = false
      this.exportMsg = 'Export queued, please wait…'
      try {
        const { data } = await api.post('/patient/export')
        this.pollTaskStatus(data.task_id)
      } catch {
        this.exportMsg = 'Export request failed. Please try again.'
        this.exporting = false
      }
    },

    pollTaskStatus(taskId) {
      const interval = setInterval(async () => {
        try {
          const { data } = await api.get(`/patient/export/status/${taskId}`)
          if (data.ready && data.successful) {
            clearInterval(interval)
            this.exporting = false
            this.exportDone = true
            this.exportMsg = '✅ Export complete! Click Download CSV to save your file.'
            setTimeout(() => this.exportMsg = '', 8000)
          } else if (data.status === 'FAILURE') {
            clearInterval(interval)
            this.exporting = false
            this.exportMsg = 'Export failed. Please try again.'
          }
        } catch {
          clearInterval(interval)
          this.exporting = false
          this.exportMsg = 'Could not check export status.'
        }
      }, 2000)
    },
    async downloadCsv() {
      try {
        const response = await api.get('/patient/download-csv', { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'treatment_history.csv')
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch {
        this.exportMsg = 'Download failed. Please export first then try again.'
      }
    }
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.history-list { display: flex; flex-direction: column; gap: 16px; }
.history-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
.doctor-name { font-weight: 700; font-size: 16px; }
.dept-name { color: var(--muted); font-size: 14px; margin-left: 4px; }
.history-right { display: flex; align-items: center; gap: 10px; }
.date-chip { background: var(--light); padding: 4px 12px; border-radius: 12px;
  font-size: 12px; color: var(--muted); border: 1px solid #d4e0ec; }
.treatment-section { background: #f8fbff; border-radius: 8px; padding: 16px; border: 1px solid #e2eaf3; }
.treat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.treat-block.full { grid-column: span 2; }
.treat-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .4px;
  color: var(--teal); margin-bottom: 4px; }
.treat-value { font-size: 14px; color: var(--text); line-height: 1.5; }
.pending-tag { font-size: 13px; color: var(--muted); font-style: italic; }
.cancelled-tag { font-size: 13px; color: var(--danger); font-style: italic; }
@media (max-width: 600px) { .treat-grid { grid-template-columns: 1fr; } .treat-block.full { grid-column: 1; } }
</style>
