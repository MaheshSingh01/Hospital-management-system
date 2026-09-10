<template>
  <Layout :nav-items="navItems">
    <div class="page-header"><h2>Find a Doctor</h2></div>

    <div class="card" style="margin-bottom: 20px;">
      <div class="search-row">
        <input v-model="filters.name" class="form-control" placeholder="🔍 Search by doctor name…" @input="fetchDoctors" />
        <select v-model="filters.dept_id" class="form-control" @change="fetchDoctors" style="max-width: 220px;">
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div v-if="loading" class="loading">Loading doctors…</div>
    <div v-else-if="doctors.length === 0" class="empty-state card">
      <div class="icon">👨‍⚕️</div><p>No doctors match your search</p>
    </div>
    <div v-else class="doctors-grid">
      <div v-for="doc in doctors" :key="doc.id" class="doctor-card card">
        <div class="doc-top">
          <div class="doc-avatar">{{ initials(doc.full_name) }}</div>
          <div class="doc-info">
            <h3 class="doc-name">Dr. {{ doc.full_name }}</h3>
            <span class="dept-badge">{{ doc.department || 'General' }}</span>
          </div>
          <button class="btn-profile" @click="viewProfile(doc)" title="View Profile">
            <i class="fa-solid fa-circle-info"></i>
          </button>
        </div>

        <div class="slots-section">
          <p class="slots-title">Availability (Next 7 Days)</p>
          <div v-if="doc.available_slots && doc.available_slots.length > 0" class="slots-grid">
          <template v-for="s in doc.available_slots" :key="s.id">
            <button
              v-if="!isSlotBooked(doc, s)"
              class="slot-btn"
              :class="{ selected: selectedSlot?.id === s.id && selectedDoc?.id === doc.id }"
              @click="selectSlot(doc, s)"
            >
              {{ s.avail_date }}<br>
              <small>{{ s.slot_start }} – {{ s.slot_end }}</small>
            </button>
          </template>
          </div>
          <p v-else class="no-slots">No availability set for this week</p>
        </div>

        <button
          v-if="selectedDoc?.id === doc.id && selectedSlot"
          class="btn btn-primary"
          style="width: 100%; margin-top: 12px; justify-content: center;"
          :disabled="booking"
          @click="confirmBooking"
        >
          {{ booking ? 'Booking…' : 'Book This Appointment' }}
        </button>
      </div>
    </div>
<!-- Doctor Profile Modal -->
    <div v-if="showProfileModal" class="modal-overlay" @click.self="showProfileModal = false">
      <div class="modal-box">
        <div class="profile-modal-top">
          <div class="doc-avatar large">{{ initials(profileDoc.full_name) }}</div>
          <div>
            <h3>Dr. {{ profileDoc.full_name }}</h3>
            <span class="dept-badge">{{ profileDoc.department || 'General' }}</span>
          </div>
        </div>
        <div class="profile-modal-body">
          <div v-if="profileDoc.bio" class="bio-section">
            <div class="bio-label">About</div>
            <p class="bio-text">{{ profileDoc.bio }}</p>
          </div>
          <div v-else class="bio-section">
            <p class="bio-text muted">No bio available for this doctor.</p>
          </div>
          <div class="profile-detail">
            <i class="fa-solid fa-building-columns"></i>
            <span>{{ profileDoc.department || 'General Medicine' }}</span>
          </div>
        </div>
        <button class="btn btn-outline" style="width:100%; margin-top:16px;" @click="showProfileModal = false">Close</button>
      </div>
    </div>
  </Layout>
</template>

<script>
/* eslint-disable */
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'PatientDoctors',
  components: { Layout },
  data() {
    return {
      doctors: [], departments: [], loading: true,
      filters: { name: '', dept_id: '' },
      selectedDoc: null, selectedSlot: null,
      booking: false,
      bookedSlotIds: [],
      successMsg: '', errMsg: '',
      showProfileModal: false, profileDoc: {},
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
    await Promise.all([this.fetchDoctors(), this.fetchDepts(), this.fetchMyBookedSlots()])
  },
  methods: {
    async fetchDoctors() {
      this.loading = true
      const { data } = await api.get('/patient/doctors', { params: this.filters })
      this.doctors = data
      this.loading = false
    },
    async fetchDepts() {
      const { data } = await api.get('/patient/dashboard')
      this.departments = data.departments || []
    },
    async fetchMyBookedSlots() {
      try {
        const { data } = await api.get('/patient/history')
        this.bookedSlotIds = data
          .filter(a => a.booking_status === 'Booked')
          .map(a => `${a.doctor_id}_${a.scheduled_date}_${a.scheduled_time}`)
      } catch (e) {}
    },
    isSlotBooked(doc, slot) {
      return this.bookedSlotIds.includes(`${doc.id}_${slot.avail_date}_${slot.slot_start}`)
    },
    initials(name) {
      return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '??'
    },
    viewProfile(doc) {
      this.profileDoc = doc
      this.showProfileModal = true
    },
    selectSlot(doc, slot) {
      if (this.isSlotBooked(doc, slot)) return
      this.selectedDoc = doc
      this.selectedSlot = slot
    },
    async confirmBooking() {
      if (!this.selectedDoc || !this.selectedSlot) return
      this.booking = true
      this.errMsg = ''
      try {
        await api.post('/patient/appointments/book', {
          doctor_id: this.selectedDoc.id,
          scheduled_date: this.selectedSlot.avail_date,
          scheduled_time: this.selectedSlot.slot_start
        })
        this.successMsg = `Appointment booked with Dr. ${this.selectedDoc.full_name} on ${this.selectedSlot.avail_date} at ${this.selectedSlot.slot_start}`
        this.bookedSlotIds.push(`${this.selectedDoc.id}_${this.selectedSlot.avail_date}_${this.selectedSlot.slot_start}`)
        this.selectedDoc = null
        this.selectedSlot = null
        setTimeout(() => this.successMsg = '', 4000)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Booking failed'
        setTimeout(() => this.errMsg = '', 4000)
      } finally {
        this.booking = false
      }
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
