<template>
  <div class="auth-screen">
    <div class="auth-left">
      <div class="overlay"></div>
      <div class="auth-left-content">
        <div class="brand">
          <div class="brand-logo">
            <img src="/pulse.png" alt="pulse" class="pulse-img" />
          </div>
          <h1 class="brand-name">Nivea Health Care</h1>
          <p class="brand-tagline">Streamlining hospital care, one appointment at a time.</p>
        </div>

        <div class="feature-list">
          <div class="feature-item" v-for="f in features" :key="f.text">
            <div class="feature-icon">{{ f.symbol }}</div>
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
            <img src="/pulse.png" alt="pulse" class="pulse-img-sm" />
          </div>
          <h2 class="auth-title">Welcome back</h2>
          <p class="auth-sub">Sign in to your account to continue</p>
        </div>

        <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

        <form @submit.prevent="doLogin">
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" class="form-control"
              placeholder="Enter your username" required />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input v-model="form.password" type="password" class="form-control"
              placeholder="Enter your password" required />
          </div>
          <button class="btn btn-primary full-width" :disabled="loading">
            {{ loading ? 'Signing in…' : 'Sign In' }}
          </button>
        </form>

        <p class="auth-footer">
          New patient? <router-link to="/register">Create an account</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  name: 'LoginPage',
  data() {
    return {
      form: { username: '', password: '' },
      errMsg: '',
      loading: false,
      features: [
        { symbol: '✓', text: 'Easy appointment booking' },
        { symbol: '✓', text: 'Connect with verified doctors' },
        { symbol: '✓', text: 'Full treatment history' },
        { symbol: '✓', text: 'Daily appointment reminders' },
      ]
    }
  },
  methods: {
    async doLogin() {
      this.errMsg = ''
      this.loading = true
      try {
        const { data } = await api.post('/auth/login', this.form)
        localStorage.setItem('hms_token', data.token)
        localStorage.setItem('hms_role',  data.role)
        localStorage.setItem('hms_name',  data.full_name)
        localStorage.setItem('hms_id',    data.user_id)
        this.$router.push(`/${data.role}/dashboard`)
      } catch (err) {
        this.errMsg = err.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
