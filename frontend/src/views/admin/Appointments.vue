<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>All Appointments</h2>
    </div>

    <div class="card filter-bar" style="margin-bottom: 20px;">
      <select v-model="statusFilter" class="form-control" style="max-width: 200px;">
        <option value="">All Statuses</option>
        <option value="Booked">Booked</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <!-- Appointments Table -->
    <div class="card" style="margin-bottom: 30px;">
      <div v-if="loading" class="loading">Loading appointments…</div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="icon">📅</div><p>No appointments found</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>#</th><th>Patient</th><th>Doctor</th>
            <th>Department</th><th>Date</th><th>Time</th>
            <th>Status</th><th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in filtered" :key="a.id">
            <td><code>{{ a.display_id }}</code></td>
            <td>{{ a.patient_name }}</td>
            <td>Dr. {{ a.doctor_name }}</td>
            <td>{{ a.doctor_dept || '—' }}</td>
            <td>{{ a.scheduled_date }}</td>
            <td>{{ a.scheduled_time }}</td>
            <td>
              <span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">
                {{ a.booking_status }}
              </span>
            </td>
            <td>
              <button
                v-if="a.booking_status === 'Booked'"
                class="btn-small btn-danger"
                @click="openCancelModal(a.id)"
              >Cancel</button>
              <span v-else class="muted-text">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Doctor Schedule Management -->
    <div class="card">
      <h3 style="margin-bottom: 16px;">Manage Doctor Availability Slots</h3>

      <div class="form-group" style="max-width: 300px;">
        <label>Select Doctor</label>
        <select v-model="selectedDoctorId" class="form-control" @change="loadDoctorSlots">
          <option value="">-- Choose a doctor --</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">Dr. {{ d.full_name }}</option>
        </select>
      </div>

      <div v-if="selectedDoctorId" class="slot-form">
        <h4 style="margin-bottom: 12px;">Add New Slot</h4>
        <div class="slot-form-row">
          <div class="form-group">
            <label>Date</label>
            <input v-model="newSlot.avail_date" type="date" class="form-control" />
          </div>
          <div class="form-group">
            <label>Start Time</label>
            <input v-model="newSlot.slot_start" type="time" class="form-control" />
          </div>
          <div class="form-group">
            <label>End Time</label>
            <input v-model="newSlot.slot_end" type="time" class="form-control" />
          </div>
          <div class="form-group" style="align-self: flex-end;">
            <button class="btn btn-primary" @click="addSlot">Add Slot</button>
          </div>
        </div>
        <div v-if="slotErr" class="alert alert-error" style="margin-top: 8px;">{{ slotErr }}</div>
        <div v-if="slotSuccess" class="alert alert-success" style="margin-top: 8px;">{{ slotSuccess }}</div>
      </div>

      <div v-if="selectedDoctorId && doctorSlots.length > 0" style="margin-top: 20px;">
        <h4 style="margin-bottom: 12px;">Existing Slots</h4>
        <table>
          <thead>
            <tr><th>Date</th><th>Start</th><th>End</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in doctorSlots" :key="s.id">
              <td>{{ s.avail_date }}</td>
              <td>{{ s.slot_start }}</td>
              <td>{{ s.slot_end }}</td>
              <td>
                <button class="btn-small btn-danger" @click="openRemoveSlotModal(s.id)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="selectedDoctorId" style="margin-top: 16px; color: var(--muted);">
        No slots added for this doctor yet.
      </div>
    </div>

    <!-- Cancel Appointment -->
    <div v-if="showCancelModal" class="modal-overlay" @click.self="showCancelModal = false">
      <div class="modal-box confirm-box">
        <div class="confirm-icon">⚠️</div>
        <h3>Cancel Appointment?</h3>
        <p class="modal-sub">This will cancel the appointment permanently. This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCancelModal = false">Keep It</button>
          <button class="btn-small btn-danger" @click="confirmCancel" :disabled="cancelling">
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel It' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Remove Slot -->
    <div v-if="showRemoveSlotModal" class="modal-overlay" @click.self="showRemoveSlotModal = false">
      <div class="modal-box confirm-box">
        <div class="confirm-icon">🗑️</div>
        <h3>Remove This Slot?</h3>
        <p class="modal-sub">This availability slot will be permanently removed from the doctor's schedule.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showRemoveSlotModal = false">Keep It</button>
          <button class="btn-small btn-danger" @click="confirmRemoveSlot">Yes, Remove It</button>
        </div>
      </div>
    </div>

  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'AdminAppointments',
  components: { Layout },
  data() {
    return {
      appointments: [], statusFilter: '', loading: true,
      successMsg: '', errMsg: '',
      doctors: [], selectedDoctorId: '',
      doctorSlots: [],
      newSlot: { avail_date: '', slot_start: '', slot_end: '' },
      slotErr: '', slotSuccess: '',
      showCancelModal: false, cancelTargetId: null, cancelling: false,
      showRemoveSlotModal: false, removeTargetId: null,
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
    const [apptRes, docRes] = await Promise.all([
      api.get('/admin/appointments'),
      api.get('/admin/doctors')
    ])
    this.appointments = apptRes.data
    this.doctors = docRes.data
    this.loading = false
  },
  computed: {
    filtered() {
      if (!this.statusFilter) return this.appointments
      return this.appointments.filter(a => a.booking_status === this.statusFilter)
    }
  },
  methods: {
    openCancelModal(id) {
      this.cancelTargetId = id
      this.showCancelModal = true
    },
    async confirmCancel() {
      this.cancelling = true
      try {
        await api.post(`/admin/appointments/${this.cancelTargetId}/cancel`)
        this.successMsg = 'Appointment cancelled successfully'
        const appt = this.appointments.find(a => a.id === this.cancelTargetId)
        if (appt) appt.booking_status = 'Cancelled'
        this.showCancelModal = false
        setTimeout(() => this.successMsg = '', 3000)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Failed to cancel appointment'
        setTimeout(() => this.errMsg = '', 3000)
      } finally { this.cancelling = false }
    },
    async loadDoctorSlots() {
      if (!this.selectedDoctorId) return
      const { data } = await api.get(`/admin/doctors/${this.selectedDoctorId}/schedule`)
      this.doctorSlots = data
    },
    async addSlot() {
      this.slotErr = ''; this.slotSuccess = ''
      if (!this.newSlot.avail_date || !this.newSlot.slot_start || !this.newSlot.slot_end) {
        this.slotErr = 'Please fill in all slot fields'
        return
      }
      try {
        await api.post(`/admin/doctors/${this.selectedDoctorId}/schedule`, this.newSlot)
        this.slotSuccess = 'Slot added successfully'
        this.newSlot = { avail_date: '', slot_start: '', slot_end: '' }
        await this.loadDoctorSlots()
        setTimeout(() => this.slotSuccess = '', 3000)
      } catch (err) {
        this.slotErr = err.response?.data?.error || 'Failed to add slot'
      }
    },
    openRemoveSlotModal(slotId) {
      this.removeTargetId = slotId
      this.showRemoveSlotModal = true
    },
    async confirmRemoveSlot() {
      await api.delete(`/admin/schedule/${this.removeTargetId}`)
      this.doctorSlots = this.doctorSlots.filter(s => s.id !== this.removeTargetId)
      this.showRemoveSlotModal = false
    }
  }
}
</script>
<style scoped>
.page-header { margin-bottom: 20px; }
.filter-bar { display: flex; align-items: center; gap: 12px; }
.btn-small {
  padding: 4px 12px; border-radius: 6px; border: none;
  cursor: pointer; font-size: 12px; font-weight: 600;
}
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.muted-text { color: var(--muted); font-size: 13px; }
.slot-form { margin-top: 20px; padding-top: 16px; border-top: 1px solid #e8edf2; }
.slot-form-row { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-start; }
.modal-overlay { position: fixed; inset: 0; background: rgba(13,27,42,.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-box { background: #fff; border-radius: 12px; padding: 28px; width: 420px; max-width: 95vw; }
.modal-box h3 { margin-bottom: 4px; }
.modal-sub { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.confirm-box { text-align: center; }
.confirm-icon { font-size: 42px; margin-bottom: 12px; }
</style>
