<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Departments</h2>
      <button class="btn btn-primary" @click="openAdd">+ Add Department</button>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div class="dept-grid">
      <div v-for="d in departments" :key="d.id" class="dept-card card">
        <div class="dept-top">
          <div class="dept-icon">🏥</div>
          <div class="dept-actions">
            <button class="btn btn-outline btn-sm" @click="openEdit(d)">Edit</button>
            <button class="btn btn-danger btn-sm" @click="deleteDept(d.id, d.name)">Delete</button>
          </div>
        </div>
        <h3 class="dept-name">{{ d.name }}</h3>
        <p class="dept-desc">{{ d.description }}</p>
        <div class="dept-count">{{ d.doctor_count }} doctor(s) assigned</div>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3>{{ editMode ? 'Edit Department' : 'New Department' }}</h3>
        <div class="form-group"><label>Name</label>
          <input v-model="form.name" class="form-control" placeholder="e.g. Cardiology" /></div>
        <div class="form-group"><label>Description</label>
          <textarea v-model="form.description" class="form-control" rows="3" placeholder="Brief description…"></textarea></div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="saveDept" :disabled="saving">{{ saving ? 'Saving…' : 'Save' }}</button>
        </div>
      </div>
    </div>
  </Layout>
</template>
