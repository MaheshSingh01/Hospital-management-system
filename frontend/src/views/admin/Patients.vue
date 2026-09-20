<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Patient Management</h2>
    </div>

    <div class="card" style="margin-bottom: 20px;">
      <input v-model="searchKw" class="form-control" placeholder="🔍 Search by name, username or contact…" @input="fetchPatients" />
    </div>

    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <div class="card">
      <div v-if="loading" class="loading">Loading patients…</div>
      <div v-else-if="patients.length === 0" class="empty-state">
        <div class="icon">🧑</div><p>No patients found</p>
      </div>
      <table v-else>
        <thead>
          <tr><th>ID</th><th>Name</th><th>Username</th><th>Contact</th><th>Address</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in patients" :key="p.id">
            <td><code>{{ p.display_id }}</code></td>
            <td><strong>{{ p.full_name }}</strong></td>
            <td>{{ p.username }}</td>
            <td>{{ p.contact_num || '—' }}</td>
            <td>{{ p.home_address || '—' }}</td>
            <td>
              <div class="action-btns">
                <button class="btn btn-outline btn-sm" @click="openEdit(p)">Edit</button>
                <button class="btn btn-danger btn-sm" @click="deletePatient(p.id, p.full_name)">Remove</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Patient -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3>Edit Patient</h3>
        <div class="form-group"><label>Full Name</label>
          <input v-model="form.full_name" class="form-control" /></div>
        <div class="form-group"><label>Contact Number</label>
          <input v-model="form.contact_num" class="form-control" /></div>
        <div class="form-group"><label>Address</label>
          <input v-model="form.home_address" class="form-control" /></div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="savePatient" :disabled="saving">{{ saving ? 'Saving…' : 'Save Changes' }}</button>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '../../components/Layout.vue'
import api from '../../api'
export default {
  name: 'AdminPatients',
  components: { Layout },
  data() {
    return {
      patients: [], searchKw: '', loading: true, saving: false,
      showModal: false, editId: null,
      form: { full_name: '', contact_num: '', home_address: '' },
      errMsg: '', successMsg: '',
      navItems: [
        { path: '/admin/dashboard',    icon: 'fa-solid fa-gauge',          label: 'Dashboard' },
        { path: '/admin/doctors',      icon: 'fa-solid fa-user-doctor',    label: 'Doctors' },
        { path: '/admin/patients',     icon: 'fa-solid fa-users',          label: 'Patients' },
        { path: '/admin/appointments', icon: 'fa-solid fa-calendar-check', label: 'Appointments' },
        { path: '/admin/departments',  icon: 'fa-solid fa-building-columns',label: 'Departments' },
      ]
    }
  },
  async created() { await this.fetchPatients() },
  methods: {
    async fetchPatients() {
      this.loading = true
      try {
        const { data } = await api.get('/admin/patients', { params: { search: this.searchKw } })
        this.patients = data
      } catch { this.errMsg = 'Failed to load patients' } finally { this.loading = false }
    },
    openEdit(p) {
      this.editId = p.id
      this.form = { full_name: p.full_name, contact_num: p.contact_num || '', home_address: p.home_address || '' }
      this.showModal = true
    },
    async savePatient() {
      this.saving = true
      try {
        await api.put(`/admin/patients/${this.editId}`, this.form)
        this.successMsg = 'Patient updated successfully'
        this.showModal = false
        await this.fetchPatients()
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Update failed'
      } finally { this.saving = false }
    },
    async deletePatient(id, name) {
      if (!confirm(`Remove patient ${name}? This action is permanent.`)) return
      await api.delete(`/admin/patients/${id}`)
      this.successMsg = `${name} has been removed`
      await this.fetchPatients()
    }
  }
}
</script>
