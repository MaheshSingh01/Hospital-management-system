<template>
  <div class="auth-screen">
    <div class="auth-left">
      <div class="overlay"></div>
      <div class="auth-left-content">
        <div class="brand-logo">
          <img src="../../public/pulse.png" alt="pulse" class="pulse-img" />
        </div>
        <h1 class="brand-name">Nivea Health Care</h1>
        <p class="brand-tagline">Join thousands of patients managing their health with ease.</p>

        <div class="feature-list">
          <div class="feature-item" v-for="f in features" :key="f.text">
            <div class="feature-icon">✓</div>
            <span>{{ f.text }}</span>
          </div>
        </div>

        <div class="auth-left-footer">
          <span>Trusted by healthcare professionals</span>
        </div>
      </div>
    </div>

    <div class="auth-right">
      <div class="auth-card">
        <div class="auth-card-header">
          <div class="auth-logo-small">
            <img src="../../public/pulse.png" alt="pulse" class="pulse-img-sm" />
          </div>
          <h2 class="auth-title">Create Account</h2>
          <p class="auth-sub">Patient registration only. Doctors are added by admin.</p>
        </div>

        <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>
        <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

        <form @submit.prevent="doRegister">
          <div class="form-group">
            <label>Full Name</label>
            <input v-model="form.full_name" class="form-control"
              placeholder="Your full name" required />
          </div>
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" class="form-control"
              placeholder="Choose a username" required />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input v-model="form.password" type="password" class="form-control"
              placeholder="Choose a strong password" required minlength="6" />
          </div>
          <div class="form-group">
            <label>Contact Number</label>
            <input
              v-model="form.contact_num"
              class="form-control"
              placeholder="Your phone number"
              inputmode="numeric"
              @input="form.contact_num = form.contact_num.replace(/\D/g, '')"
              maxlength="15"
            />
          </div>
          <div class="form-group">
            <label>Address</label>
            <input v-model="form.home_address" class="form-control"
              placeholder="Your home address" />
          </div>
          <div class="form-group">
            <label>Email Address</label>
            <input v-model="form.email" type="email" class="form-control"
              placeholder="Your email address" required />
          </div>
          <button class="btn btn-primary full-width" :disabled="loading">
            {{ loading ? 'Creating account…' : 'Create Account' }}
          </button>
        </form>

        <p class="auth-footer">
          Already have an account? <router-link to="/login">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  name: 'RegisterPage',
  data() {
    return {
      form: { username: '', password: '', full_name: '', contact_num: '', home_address: '', email: '' },
      errMsg: '', successMsg: '', loading: false,
      features: [
        { text: 'Easy appointment booking' },
        { text: 'Connect with verified doctors' },
        { text: 'Full treatment history' },
        { text: 'Daily appointment reminders' },
      ]
    }
  },
  methods: {
    async doRegister() {
      this.errMsg = ''
      this.successMsg = ''
      this.loading = true
      try {
        await api.post('/auth/register', this.form)
        this.successMsg = 'Account created! Redirecting to login…'
        setTimeout(() => this.$router.push('/login'), 1500)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
