<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>My Appointments</h2>
      <div class="filter-tabs">
        <button v-for="t in tabs" :key="t.val" class="tab-btn" :class="{ active: view === t.val }" @click="switchView(t.val)">
          {{ t.label }}
        </button>
      </div>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div class="card">
      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="appointments.length === 0" class="empty-state">
        <div class="icon">📅</div><p>No appointments in this view</p>
      </div>
      <table v-else>
        <thead>
          <tr><th>Date</th><th>Time</th><th>Patient</th><th>Status</th><th>Treatment</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in appointments" :key="a.id">
            <td>{{ a.scheduled_date }}</td>
            <td>{{ a.scheduled_time }}</td>
            <td><strong>{{ a.patient_name }}</strong></td>
            <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
            <td>
              <span v-if="a.has_treatment" class="badge badge-completed">Recorded</span>
              <span v-else class="badge badge-pending">None</span>
            </td>
            <td>
              <div class="action-btns" v-if="a.booking_status === 'Booked'">
                <button class="btn btn-success btn-sm" @click="openCompleteModal(a)">✓ Complete</button>
                <button class="btn btn-outline btn-sm" @click="openRescheduleModal(a)">↺ Reschedule</button>
                <button class="btn btn-danger btn-sm" @click="openCancelModal(a)">✗ Cancel</button>
              </div>
              <button v-else-if="a.booking_status === 'Completed'" class="btn btn-outline btn-sm" @click="openCompleteModal(a)">
                View/Edit
              </button>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Complete Appointment -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3>Complete Appointment — {{ activeAppt?.patient_name }}</h3>
        <p class="modal-sub">{{ activeAppt?.scheduled_date }} at {{ activeAppt?.scheduled_time }}</p>
        <div class="form-group" style="margin-top: 16px;">
          <label>Diagnosis *</label>
          <textarea v-model="treatForm.diagnosis_text" class="form-control" rows="3" placeholder="Enter diagnosis details…" required></textarea>
        </div>
        <div class="form-group">
          <label>Prescription *</label>
          <textarea v-model="treatForm.prescription_text" class="form-control" rows="3" placeholder="Medicines and dosage…" required></textarea>
        </div>
        <div class="form-group">
          <label>Follow-up Notes</label>
          <textarea v-model="treatForm.follow_up_notes" class="form-control" rows="2" placeholder="Additional notes for patient…"></textarea>
        </div>
        <div class="form-group">
          <label>Next Visit Date</label>
          <input v-model="treatForm.next_visit_date" type="date" class="form-control" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">Close</button>
          <button class="btn btn-success" @click="submitComplete" :disabled="saving">
            {{ saving ? 'Saving…' : 'Mark as Completed' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRescheduleModal" class="modal-overlay" @click.self="showRescheduleModal = false">
      <div class="modal-box">
        <h3>Reschedule Appointment</h3>
        <p class="modal-sub">Patient: <strong>{{ activeAppt?.patient_name }}</strong> — Current: {{ activeAppt?.scheduled_date }} at {{ activeAppt?.scheduled_time }}</p>
        <div v-if="rescheduleErr" class="alert alert-error">{{ rescheduleErr }}</div>
        <div class="form-group" style="margin-top: 16px;">
          <label>New Date</label>
          <input v-model="rescheduleForm.scheduled_date" type="date" class="form-control" :min="today" required />
        </div>
        <div class="form-group">
          <label>New Time</label>
          <input v-model="rescheduleForm.scheduled_time" type="time" class="form-control" required />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showRescheduleModal = false">Cancel</button>
          <button class="btn btn-primary" @click="submitReschedule" :disabled="rescheduling">
            {{ rescheduling ? 'Saving…' : 'Confirm Reschedule' }}
          </button>
        </div>
      </div>
    </div>
    <!-- Cancel Confirmation -->
    <div v-if="showCancelModal" class="modal-overlay" @click.self="showCancelModal = false">
      <div class="modal-box confirm-box">
        <div class="confirm-icon">⚠️</div>
        <h3>Cancel Appointment?</h3>
        <p class="modal-sub">
          You are about to cancel the appointment with
          <strong>{{ activeAppt?.patient_name }}</strong>
          on <strong>{{ activeAppt?.scheduled_date }}</strong>
          at <strong>{{ activeAppt?.scheduled_time }}</strong>.
        </p>
        <p class="confirm-note">This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCancelModal = false">Keep It</button>
          <button class="btn btn-danger" @click="confirmCancel" :disabled="cancelling">
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel It' }}
          </button>
        </div>
      </div>
    </div>
  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'DoctorAppointments',
  components: { Layout },
  data() {
    return {
      appointments: [], view: 'all', loading: true,
      showModal: false, showCancelModal: false,
      activeAppt: null, saving: false, cancelling: false,
      rescheduling: false,
      rescheduleForm: { scheduled_date: '', scheduled_time: '' },
      rescheduleErr: '',
      today: new Date().toISOString().split('T')[0],
      showRescheduleModal: false,
      treatForm: { diagnosis_text: '', prescription_text: '', follow_up_notes: '', next_visit_date: '' },
      successMsg: '', errMsg: '',
      tabs: [{ val: 'all', label: 'All' }, { val: 'today', label: 'Today' }, { val: 'week', label: 'This Week' }],
      navItems: [
        { path: '/doctor/dashboard',    icon: 'fa-solid fa-gauge',         label: 'Dashboard' },
        { path: '/doctor/appointments', icon: 'fa-solid fa-calendar-check',label: 'Appointments' },
        { path: '/doctor/patients',     icon: 'fa-solid fa-users',         label: 'My Patients' },
        { path: '/doctor/schedule',     icon: 'fa-solid fa-clock',         label: 'Schedule' },
        { path: '/doctor/profile',      icon: 'fa-solid fa-circle-user',   label: 'Profile' },
      ]
    }
  },
  async created() { await this.load() },
  methods: {
    async load() {
      this.loading = true
      const { data } = await api.get('/doctor/appointments', { params: { view: this.view } })
      this.appointments = data; this.loading = false
    },
    switchView(v) { this.view = v; this.load() },
    openCompleteModal(appt) {
      this.activeAppt = appt
      const rec = appt.treatment
      this.treatForm = {
        diagnosis_text: rec?.diagnosis_text || '',
        prescription_text: rec?.prescription_text || '',
        follow_up_notes: rec?.follow_up_notes || '',
        next_visit_date: rec?.next_visit_date || ''
      }
      this.showModal = true
    },
    openRescheduleModal(appt) {
      this.activeAppt = appt
      this.rescheduleForm = {
        scheduled_date: appt.scheduled_date,
        scheduled_time: appt.scheduled_time
      }
      this.rescheduleErr = ''
      this.showRescheduleModal = true
    },
    async submitReschedule() {
      if (!this.rescheduleForm.scheduled_date || !this.rescheduleForm.scheduled_time) {
        this.rescheduleErr = 'Please select both date and time'
        return
      }
      this.rescheduling = true
      this.rescheduleErr = ''
      try {
        await api.post(`/doctor/appointments/${this.activeAppt.id}/reschedule`, this.rescheduleForm)
        this.successMsg = 'Appointment rescheduled successfully'
        this.showRescheduleModal = false
        await this.load()
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        this.rescheduleErr = err.response?.data?.error || 'Failed to reschedule'
      } finally { this.rescheduling = false }
    },
    openCancelModal(appt) {
      this.activeAppt = appt
      this.showCancelModal = true
    },
    async submitComplete() {
      if (!this.treatForm.diagnosis_text || !this.treatForm.prescription_text) {
        this.errMsg = 'Diagnosis and prescription are required'
        return
      }
      this.saving = true
      try {
        await api.post(`/doctor/appointments/${this.activeAppt.id}/complete`, this.treatForm)
        this.successMsg = 'Appointment completed and treatment saved'
        this.showModal = false
        await this.load()
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Failed to complete appointment'
        setTimeout(() => this.errMsg = '', 3000)
      } finally { this.saving = false }
    },
    async confirmCancel() {
      this.cancelling = true
      try {
        await api.post(`/doctor/appointments/${this.activeAppt.id}/cancel`)
        this.successMsg = 'Appointment cancelled successfully'
        this.showCancelModal = false
        await this.load()
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Failed to cancel'
        setTimeout(() => this.errMsg = '', 3000)
      } finally { this.cancelling = false }
    }
  }
}
</script>
