<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Doctor Management</h2>
      <button class="btn btn-primary" @click="openAddModal">+ Add Doctor</button>
    </div>

    <!-- Search bar -->
    <div class="card" style="margin-bottom: 20px;">
      <div class="search-row">
        <input v-model="searchKw" class="form-control" placeholder="🔍 Search by name or department…" @input="fetchDoctors" />
      </div>
    </div>

    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div class="card">
      <div v-if="loading" class="loading">Loading doctors…</div>
      <div v-else-if="doctors.length === 0" class="empty-state">
        <div class="icon">👨‍⚕️</div>
        <p>No doctors found</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>ID</th><th>Name</th><th>USERNAME</th><th>Department</th><th>Contact</th>
            <th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in doctors" :key="doc.id">
            <td><code>{{ doc.display_id }}</code></td>
            <td><strong>{{ doc.full_name }}</strong></td>
            <td>{{ doc.username }}</td>
            <td>{{ doc.department || '—' }}</td>
            <td>{{ doc.contact_num || '—' }}</td>
            <td>
              <span class="badge" :class="doc.is_verified ? 'badge-verified' : 'badge-pending'">
                {{ doc.is_verified ? 'Verified' : 'Pending' }}
              </span>
            </td>
            <td>
              <div class="action-btns">
                <button v-if="!doc.is_verified" class="btn btn-success btn-sm" @click="verifyDoctor(doc.id)">✓ Verify</button>
                <button class="btn btn-outline btn-sm" @click="openEditModal(doc)">Edit</button>
                <button class="btn btn-danger btn-sm" @click="deleteDoctor(doc.id, doc.full_name)">Remove</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Doctor -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <h3>{{ editMode ? 'Edit Doctor' : 'Add New Doctor' }}</h3>
        <div v-if="modalErr" class="alert alert-error">{{ modalErr }}</div>

        <div class="form-group">
          <label>Full Name</label>
          <input v-model="form.full_name" class="form-control" placeholder="Doctor's full name" required />
        </div>
        <div v-if="!editMode" class="form-group">
          <label>Username</label>
          <input v-model="form.username" class="form-control" placeholder="Login username" required />
        </div>
        <div class="form-group">
          <label>{{ editMode ? 'New Password (leave blank to keep)' : 'Password' }}</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="Password" :required="!editMode" />
        </div>
        <div class="form-group">
          <label>Department</label>
          <select v-model="form.dept_id" class="form-control">
            <option value="">— No department —</option>
            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Contact Number</label>
          <input v-model="form.contact_num" class="form-control" placeholder="Phone number" />
        </div>
        <div class="form-group">
          <label>Email Address</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="doctor@example.com" />
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="saveDoctor" :disabled="saving">
            {{ saving ? 'Saving…' : (editMode ? 'Update Doctor' : 'Add Doctor') }}
          </button>
        </div>
      </div>
    </div>
  </Layout>
</template>
