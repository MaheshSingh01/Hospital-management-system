<template>
  <div id="hms-app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy:    #0d1b2a;
  --teal:    #1b6ca8;
  --sky:     #3da5d9;
  --mint:    #63d2c9;
  --light:   #f0f6ff;
  --white:   #ffffff;
  --text:    #1e2d3d;
  --muted:   #6b7f93;
  --danger:  #e05c5c;
  --success: #2ecc8a;
  --warning: #f39c12;
  --radius:  10px;
  --shadow:  0 4px 20px rgba(13,27,42,.10);
}

body {
  font-family: 'Times New Roman', Times, serif;
  background: var(--light);
  color: var(--text);
  font-size: 15px;
}

h1, h2, h3 { font-family: 'Times New Roman', Times, serif; color: var(--navy); }

a { color: var(--teal); text-decoration: none; }
a:hover { color: var(--sky); }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 20px;
  border-radius: var(--radius); border: none; cursor: pointer; font-size: 14px;
  font-family: 'Times New Roman', Times, serif; font-weight: 500; transition: all .2s; }
.btn-primary   { background: var(--teal);   color: #fff; }
.btn-primary:hover   { background: var(--sky); }
.btn-success   { background: var(--success); color: #fff; }
.btn-success:hover   { opacity: .85; }
.btn-danger    { background: var(--danger);  color: #fff; }
.btn-danger:hover    { opacity: .85; }
.btn-warning   { background: var(--warning); color: #fff; }
.btn-outline   { background: transparent; border: 1.5px solid var(--teal); color: var(--teal); }
.btn-outline:hover   { background: var(--teal); color: #fff; }
.btn-sm { padding: 6px 13px; font-size: 13px; }

.card { background: var(--white); border-radius: var(--radius); box-shadow: var(--shadow); padding: 24px; }

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 600; }
.badge-booked    { background: #dbeafe; color: #1d4ed8; }
.badge-completed { background: #d1fae5; color: #065f46; }
.badge-cancelled { background: #fee2e2; color: #991b1b; }
.badge-pending   { background: #fef3c7; color: #92400e; }
.badge-verified  { background: #d1fae5; color: #065f46; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px;
  font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .4px; }
.form-control { width: 100%; padding: 10px 14px; border: 1.5px solid #d4e0ec;
  border-radius: var(--radius); font-family: 'Times New Roman', Times, serif; font-size: 14px;
  background: var(--white); color: var(--text); transition: border .2s; }
.form-control:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px rgba(27,108,168,.12); }
.form-control::placeholder { color: #b0bcc9; }

table { width: 100%; border-collapse: collapse; }
thead th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 700;
  text-transform: uppercase; letter-spacing: .5px; color: var(--muted);
  background: var(--light); border-bottom: 2px solid #dde8f5; }
tbody td { padding: 13px 16px; border-bottom: 1px solid #edf2f9; font-size: 14px; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #f8fbff; }

.alert { padding: 12px 16px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
.alert-error   { background: #fee2e2; color: #991b1b; border-left: 4px solid var(--danger); }
.alert-success { background: #d1fae5; color: #065f46; border-left: 4px solid var(--success); }
.alert-info    { background: #dbeafe; color: #1e40af; border-left: 4px solid var(--sky); }

.loading { text-align: center; padding: 40px; color: var(--muted); }
.empty-state { text-align: center; padding: 48px; color: var(--muted); }
.empty-state .icon { font-size: 48px; margin-bottom: 12px; }
</style>
