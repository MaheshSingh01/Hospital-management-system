<template>
  <Layout :nav-items="navItems">
    <div class="page-header"><h2>My Appointments</h2></div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div class="card">
      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="appointments.length === 0" class="empty-state">
        <div class="icon">📅</div>
        <p>No appointments found. <router-link to="/patient/doctors">Book one now!</router-link></p>
      </div>
      <table v-else>
        <thead>
          <tr><th>Doctor</th><th>Dept.</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in appointments" :key="a.id">
            <td>Dr. {{ a.doctor_name }}</td>
            <td>{{ a.doctor_dept || '—' }}</td>
            <td>{{ a.scheduled_date }}</td>
            <td>{{ a.scheduled_time }}</td>
            <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
            <td>
              <div class="action-btns" v-if="a.booking_status === 'Booked'">
                <button class="btn btn-warning btn-sm" @click="openReschedule(a)">🔄 Reschedule</button>
                <button class="btn btn-danger btn-sm" @click="openCancel(a)">✗ Cancel</button>
              </div>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reschedule -->
    <div v-if="showReschedModal" class="modal-overlay" @click.self="showReschedModal = false">
      <div class="modal-box">
        <h3>Reschedule Appointment</h3>
        <p class="modal-sub">
          Dr. {{ activeAppt?.doctor_name }} —
          Currently: {{ activeAppt?.scheduled_date }} at {{ activeAppt?.scheduled_time }}
        </p>

        <div v-if="rescheduleErr" class="alert alert-error">{{ rescheduleErr }}</div>

        <div v-if="slotsLoading" class="loading" style="margin-top: 16px;">Loading available slots…</div>
        <div v-else-if="availableSlots.length === 0" class="empty-state" style="padding: 20px;">
          <p>No available slots for this doctor in the next 7 days.</p>
        </div>
        <div v-else style="margin-top: 16px;">
          <label class="slot-label">Select a New Slot</label>
          <div class="slots-grid">
            <div
              v-for="slot in availableSlots"
              :key="slot.id"
              class="slot-card"
              :class="{ selected: reschedForm.slot_id === slot.id }"
              @click="selectSlot(slot)"
            >
              <div class="slot-date">{{ slot.avail_date }}</div>
              <div class="slot-time">{{ slot.slot_start }} – {{ slot.slot_end }}</div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="showReschedModal = false">Close</button>
          <button class="btn btn-primary" @click="submitReschedule" :disabled="saving || !reschedForm.slot_id">
            {{ saving ? 'Saving…' : 'Confirm Reschedule' }}
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
          You are about to cancel your appointment with
          <strong>Dr. {{ activeAppt?.doctor_name }}</strong>
          on <strong>{{ activeAppt?.scheduled_date }}</strong> at
          <strong>{{ activeAppt?.scheduled_time }}</strong>.
        </p>
        <p class="confirm-note">This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCancelModal = false">Keep Appointment</button>
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
  name: 'PatientAppointments',
  components: { Layout },
  data() {
    return {
      appointments: [], loading: true, saving: false, cancelling: false,
      showReschedModal: false, showCancelModal: false, activeAppt: null,
      reschedForm: { slot_id: null, scheduled_date: '', scheduled_time: '' },
      availableSlots: [], slotsLoading: false,
      selectedSlot: null, rescheduleErr: '',
      successMsg: '', errMsg: '',
      navItems: [
        { path: '/patient/dashboard',    icon: 'fa-solid fa-gauge',         label: 'Dashboard' },
        { path: '/patient/doctors',      icon: 'fa-solid fa-stethoscope',   label: 'Find Doctors' },
        { path: '/patient/appointments', icon: 'fa-solid fa-calendar-check',label: 'Appointments' },
        { path: '/patient/history',      icon: 'fa-solid fa-clock-rotate-left', label: 'History' },
        { path: '/patient/profile',      icon: 'fa-solid fa-circle-user',   label: 'Profile' },
      ]
    }
  },
  computed: {
    today() { return new Date().toISOString().split('T')[0] }
  },
  async created() {
    const { data } = await api.get('/patient/history')
    this.appointments = data
    this.loading = false
  },
  methods: {
    async openReschedule(a) {
      this.activeAppt = a
      this.reschedForm = { slot_id: null, scheduled_date: '', scheduled_time: '' }
      this.selectedSlot = null
      this.rescheduleErr = ''
      this.availableSlots = []
      this.showReschedModal = true
      this.slotsLoading = true
      try {
        const { data } = await api.get(`/patient/doctors/${a.doctor_id}/availability`)
        this.availableSlots = data.filter(slot => 
          !(slot.avail_date === a.scheduled_date && 
            a.scheduled_time >= slot.slot_start && 
            a.scheduled_time <= slot.slot_end)
        )        
      } catch {
        this.rescheduleErr = 'Failed to load available slots'
      } finally {
        this.slotsLoading = false
      }
    },
    selectSlot(slot) {
      this.reschedForm.slot_id = slot.id
      this.reschedForm.scheduled_date = slot.avail_date
      this.reschedForm.scheduled_time = slot.slot_start
      this.selectedSlot = slot
    },
    openCancel(a) {
      this.activeAppt = a
      this.showCancelModal = true
    },
    async submitReschedule() {
      if (!this.reschedForm.slot_id || !this.reschedForm.scheduled_time) {
        this.rescheduleErr = 'Please select a slot and time'
        return
      }
      this.saving = true; this.rescheduleErr = ''
      try {
        await api.post(`/patient/appointments/${this.activeAppt.id}/reschedule`, {
          scheduled_date: this.reschedForm.scheduled_date,
          scheduled_time: this.reschedForm.scheduled_time
        })
        this.successMsg = 'Appointment rescheduled successfully'
        this.showReschedModal = false
        const { data } = await api.get('/patient/history')
        this.appointments = data
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Failed to reschedule'
        setTimeout(() => this.errMsg = '', 3000)
      } finally { this.saving = false }
    },
    async confirmCancel() {
      this.cancelling = true; this.errMsg = ''
      try {
        await api.post(`/patient/appointments/${this.activeAppt.id}/cancel`)
        this.successMsg = 'Appointment cancelled successfully'
        this.showCancelModal = false
        const { data } = await api.get('/patient/history')
        this.appointments = data
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Failed to cancel'
        setTimeout(() => this.errMsg = '', 3000)
      } finally { this.cancelling = false }
    }
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 20px; }
.action-btns { display: flex; gap: 6px; }
.text-muted { color: var(--muted); font-size: 13px; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(13,27,42,.5);
  display: flex; align-items: center; justify-content: center; z-index: 999;
}
.modal-box {
  background: #fff; border-radius: 12px; padding: 28px;
  width: 520px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
}
.modal-box h3 { margin-bottom: 4px; }
.modal-sub { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.confirm-box { text-align: center; }
.confirm-icon { font-size: 42px; margin-bottom: 12px; }
.confirm-note {
  font-size: 12px; color: #e74c3c; margin-top: 6px;
  font-weight: 600;
}
.slot-label { font-size: 13px; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: .4px; display: block; margin-bottom: 10px; }
.slot-hint { font-weight: 400; color: var(--sky); text-transform: none; }
.slots-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; max-height: 220px; overflow-y: auto; }
.slot-card {
  border: 1.5px solid #d4e0ec; border-radius: 8px; padding: 10px 14px;
  cursor: pointer; transition: all .18s;
}
.slot-card:hover { border-color: var(--teal); background: #f0f9ff; }
.slot-card.selected { border-color: var(--teal); background: var(--teal); color: #fff; }
.slot-date { font-weight: 600; font-size: 13px; }
.slot-time { font-size: 12px; margin-top: 2px; opacity: .8; }
</style>
