<template>
  <Layout :nav-items="navItems">
    <div class="page-header"><h2>My Profile</h2></div>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else class="profile-layout">
      <div class="card profile-card">
        <div class="avatar">{{ initials }}</div>
        <h3>{{ profile.full_name }}</h3>
        <code>{{ profile.display_id }}</code>
        <div class="info-list">
          <div class="info-row"><span>📞</span> {{ profile.contact_num || 'Not provided' }}</div>
          <div class="info-row"><span>📧</span> {{ profile.email || 'Not provided' }}</div>
          <div class="info-row"><span>🏠</span> {{ profile.home_address || 'Not provided' }}</div>
        </div>
      </div>
      <div class="card profile-form">
        <h3 style="margin-bottom: 20px;">Edit Profile</h3>
        <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
        <div class="form-group">
          <label>Full Name</label>
          <input v-model="form.full_name" class="form-control" />
        </div>
        <div class="form-group">
          <label>Contact Number</label>
          <input v-model="form.contact_num" class="form-control" />
        </div>
        <div class="form-group">
          <label>Email Address</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="your@email.com" />
        </div>
        <div class="form-group">
          <label>Home Address</label>
          <input v-model="form.home_address" class="form-control" />
        </div>
        <button class="btn btn-primary" @click="save" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'PatientProfile',
  components: { Layout },
  data() {
    return {
      profile: {}, loading: true, saving: false, successMsg: '',
      form: { full_name: '', contact_num: '', home_address: '', email: '' },
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
    initials() {
      return this.profile.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'PT'
    }
  },
  async created() {
    const { data } = await api.get('/patient/profile')
    this.profile = data
    this.form = {
      full_name: data.full_name || '',
      contact_num: data.contact_num || '',
      home_address: data.home_address || '',
      email: data.email || ''
    }
    this.loading = false
  },
  methods: {
    async save() {
      this.saving = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        await api.put('/patient/profile', this.form)
        this.successMsg = 'Profile updated successfully!'
        const { data } = await api.get('/patient/profile')
        this.profile = data
        localStorage.setItem('hms_name', data.full_name)
        setTimeout(() => this.successMsg = '', 3000)
      } catch(e) {
        this.errorMsg = e.response?.data?.error || 'Failed to update profile'
      } finally { 
        this.saving = false 
      }
    }
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.profile-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
.profile-card { text-align: center; }
.avatar {
  width: 80px; height: 80px; border-radius: 50%; background: var(--sky);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 700; margin: 0 auto 14px;
}
.profile-card h3 { margin-bottom: 6px; }
.info-list { margin-top: 16px; text-align: left; }
.info-row {
  padding: 8px 0; border-bottom: 1px solid #edf2f9;
  font-size: 14px; display: flex; gap: 10px; color: var(--muted);
}
@media (max-width: 700px) { .profile-layout { grid-template-columns: 1fr; } }
</style>
