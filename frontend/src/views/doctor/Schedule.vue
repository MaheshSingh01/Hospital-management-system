<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>My Availability Schedule</h2>
      <button class="btn btn-primary" @click="showForm = !showForm">+ Add Slot</button>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div v-if="showForm" class="card" style="margin-bottom: 20px;">
      <h3 style="margin-bottom: 16px;">Add Availability Slot</h3>
      <p class="hint">You can only set availability for the next 7 days.</p>
      <div class="slot-form">
        <div class="form-group">
          <label>Date</label>
          <input v-model="newSlot.avail_date" type="date" class="form-control" :min="today" :max="maxDate" required />
        </div>
        <div class="form-group">
          <label>Start Time</label>
          <input v-model="newSlot.slot_start" type="time" class="form-control" required />
        </div>
        <div class="form-group">
          <label>End Time</label>
          <input v-model="newSlot.slot_end" type="time" class="form-control" required />
        </div>
        <button class="btn btn-primary" @click="addSlot" :disabled="saving" style="align-self: flex-end; margin-bottom: 16px;">
          {{ saving ? 'Saving…' : 'Add Slot' }}
        </button>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">Loading schedule…</div>
      <div v-else-if="slots.length === 0" class="empty-state">
        <div class="icon">🗓️</div><p>No availability slots set yet</p>
      </div>
      <table v-else>
        <thead><tr><th>Date</th><th>Start Time</th><th>End Time</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="s in slots" :key="s.id">
            <td><strong>{{ s.avail_date }}</strong></td>
            <td>{{ s.slot_start }}</td>
            <td>{{ s.slot_end }}</td>
            <td><button class="btn btn-danger btn-sm" @click="removeSlot(s.id)">Remove</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'DoctorSchedule',
  components: { Layout },
  data() {
    return {
      slots: [], loading: true, saving: false, showForm: false,
      newSlot: { avail_date: '', slot_start: '', slot_end: '' },
      successMsg: '', errMsg: '',
      navItems: [
        { path: '/doctor/dashboard',    icon: 'fa-solid fa-gauge',         label: 'Dashboard' },
        { path: '/doctor/appointments', icon: 'fa-solid fa-calendar-check',label: 'Appointments' },
        { path: '/doctor/patients',     icon: 'fa-solid fa-users',         label: 'My Patients' },
        { path: '/doctor/schedule',     icon: 'fa-solid fa-clock',         label: 'Schedule' },
        { path: '/doctor/profile',      icon: 'fa-solid fa-circle-user',   label: 'Profile' },
      ]
    }
  },
  computed: {
    today() { return new Date().toISOString().split('T')[0] },
    maxDate() {
      const d = new Date(); d.setDate(d.getDate() + 7)
      return d.toISOString().split('T')[0]
    }
  },
  async created() {
    const { data } = await api.get('/doctor/schedule')
    this.slots = data; this.loading = false
  },
  methods: {
    async addSlot() {
      if (!this.newSlot.avail_date || !this.newSlot.slot_start || !this.newSlot.slot_end) {
        this.errMsg = 'All fields are required'; return
      }
      this.saving = true
      try {
        await api.post('/doctor/schedule', this.newSlot)
        this.successMsg = 'Slot added'
        this.newSlot = { avail_date: '', slot_start: '', slot_end: '' }
        this.showForm = false
        const { data } = await api.get('/doctor/schedule')
        this.slots = data
      } catch (err) { this.errMsg = err.response?.data?.error || 'Failed to add slot' }
      finally { this.saving = false }
    },
    async removeSlot(id) {
      await api.delete(`/doctor/schedule/${id}`)
      this.slots = this.slots.filter(s => s.id !== id)
      this.successMsg = 'Slot removed'
    }
  }
}
</script>
