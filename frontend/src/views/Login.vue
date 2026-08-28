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

<style scoped>
.auth-screen { display: flex; min-height: 100vh; }

/* ── Left Panel ── */
.auth-left {
  flex: 1;
  background-image: url('../../public/healthcare1.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
}

.overlay {
  position: absolute; inset: 0;
  background: rgba(10, 25, 47, 0.72);
}

.auth-left-content {
  position: relative; z-index: 1;
  display: flex; flex-direction: column;
  justify-content: center; gap: 40px;
  padding: 60px 52px; width: 100%;
}

.brand-logo {
  width: 64px; height: 64px; border-radius: 16px;
  background: rgba(255,255,255,0.15);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px; padding: 10px;
}
.pulse-img { width: 40px; height: 40px; object-fit: contain; }

.brand-name {
  font-family: 'Times New Roman', Times, serif;
  color: #fff; font-size: 34px; margin-bottom: 10px; line-height: 1.2;
}
.brand-tagline {
  color: rgba(255,255,255,0.6);
  font-size: 15px; max-width: 300px; line-height: 1.7;
}

.feature-list { display: flex; flex-direction: column; gap: 16px; }
.feature-item {
  display: flex; align-items: center; gap: 16px;
  color: rgba(255,255,255,0.85); font-size: 15px;
}
.feature-icon {
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(61,165,217,0.35);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 16px; font-weight: 700; flex-shrink: 0;
}

.auth-left-footer {
  color: rgba(255,255,255,0.3); font-size: 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 24px; margin-top: auto;
}

/* ── Right Panel ── */
.auth-right {
  width: 500px; background: #f8fafd;
  display: flex; align-items: center; justify-content: center; padding: 48px 40px;
}
.auth-card { width: 100%; max-width: 400px; }

.auth-card-header { text-align: center; margin-bottom: 32px; }
.auth-logo-small {
  width: 52px; height: 52px; border-radius: 14px;
  background: var(--teal);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px; padding: 8px;
}
.pulse-img-sm { width: 32px; height: 32px; object-fit: contain; filter: brightness(0) invert(1); }

.auth-title { font-size: 26px; margin-bottom: 6px; color: var(--navy); }
.auth-sub { color: var(--muted); font-size: 14px; }

.full-width { width: 100%; justify-content: center; padding: 13px; font-size: 15px; margin-top: 8px; }

.auth-footer { text-align: center; margin-top: 24px; color: var(--muted); font-size: 14px; }

@media (max-width: 768px) {
  .auth-left { display: none; }
  .auth-right { width: 100%; padding: 32px 24px; }
}
</style>
