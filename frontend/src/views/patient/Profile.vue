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
