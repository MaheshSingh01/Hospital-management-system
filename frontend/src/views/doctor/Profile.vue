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
