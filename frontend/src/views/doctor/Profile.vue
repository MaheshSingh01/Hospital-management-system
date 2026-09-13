<template>
  <Layout :nav-items="navItems">
    <div class="page-header"><h2>My Profile</h2></div>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else class="profile-layout">
      <div class="card profile-card">
        <div class="avatar">{{ initials }}</div>
        <h3>Dr. {{ profile.full_name }}</h3>
        <p class="dept-tag">{{ profile.department || 'No Department Assigned' }}</p>
        <code>{{ profile.display_id }}</code>
      </div>
      <div class="card profile-form">
        <h3 style="margin-bottom: 20px;">Edit Profile</h3>
        <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
        <div class="form-group"><label>Contact Number</label>
          <input v-model="form.contact_num" class="form-control" /></div>
        <div class="form-group"><label>Home Address</label>
          <input v-model="form.home_address" class="form-control" /></div>
        <div class="form-group"><label>Email Address</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="your@email.com" /></div>
        <div class="form-group"><label>Bio / About Me</label>
          <textarea v-model="form.bio" class="form-control" rows="3" placeholder="Write a short bio about your experience and specialization…"></textarea></div>
        <button class="btn btn-primary" @click="save" :disabled="saving">{{ saving ? 'Saving…' : 'Save Changes' }}</button>
      </div>
    </div>
  </Layout>
</template>
<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'DoctorProfile',
  components: { Layout },
  data() {
    return {
      profile: {}, loading: true, saving: false, successMsg: '',
      form: { contact_num: '', home_address: '', email: '', bio: '' },
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
    initials() {
      return this.profile.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'DR'
    }
  },
  async created() {
    const { data } = await api.get('/doctor/profile')
    this.profile = data
    this.form = { contact_num: data.contact_num || '', home_address: data.home_address || '', email: data.email || '', bio: data.bio || '' }
    this.loading = false
  },
  methods: {
    async save() {
      this.saving = true
      try {
        await api.put('/doctor/profile', this.form)
        this.successMsg = 'Profile updated successfully'
        const { data } = await api.get('/doctor/profile')
        this.profile = data
      } finally { this.saving = false }
    }
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.profile-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
.profile-card { text-align: center; }
.avatar {
  width: 80px; height: 80px; border-radius: 50%; background: var(--teal);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 700; margin: 0 auto 14px;
}
.profile-card h3 { margin-bottom: 6px; }
.dept-tag { color: var(--muted); font-size: 14px; margin-bottom: 8px; }
@media (max-width: 700px) { .profile-layout { grid-template-columns: 1fr; } }
</style>
