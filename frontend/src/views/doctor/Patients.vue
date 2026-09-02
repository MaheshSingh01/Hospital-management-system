<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>My Patients</h2>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">Loading patients…</div>
      <div v-else-if="patients.length === 0" class="empty-state">
        <div class="icon">🧑</div><p>No patients assigned yet</p>
      </div>
      <table v-else>
        <thead><tr><th>ID</th><th>Name</th><th>Contact</th><th>Address</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="p in patients" :key="p.id">
            <td><code>{{ p.display_id }}</code></td>
            <td><strong>{{ p.full_name }}</strong></td>
            <td>{{ p.contact_num || '—' }}</td>
            <td>{{ p.home_address || '—' }}</td>
            <td><button class="btn btn-outline btn-sm" @click="viewHistory(p)">📋 Full History</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Patient History Modal -->
    <div v-if="showHistory" class="modal-overlay" @click.self="showHistory = false">
      <div class="modal-box large">
        <div class="history-header">
          <div>
            <h3>{{ selectedPatient?.full_name }}</h3>
            <p class="modal-sub">{{ selectedPatient?.display_id }} · {{ selectedPatient?.contact_num }}</p>
          </div>
          <button class="close-btn" @click="showHistory = false">✕</button>
        </div>

        <div v-if="historyLoading" class="loading">Loading history…</div>
        <div v-else-if="history.length === 0" class="empty-state">
          <div class="icon">📋</div><p>No appointment history yet</p>
        </div>
        <div v-else class="history-list">
          <div v-for="a in history" :key="a.id" class="history-item" :class="`status-${a.booking_status.toLowerCase()}`">
            <div class="history-top">
              <div class="history-date">
                <strong>{{ a.scheduled_date }}</strong> at {{ a.scheduled_time }}
              </div>
              <span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span>
            </div>
            <div v-if="a.treatment" class="treatment-box">
              <div class="treat-row"><span class="treat-label">Diagnosis:</span> {{ a.treatment.diagnosis_text }}</div>
              <div class="treat-row"><span class="treat-label">Prescription:</span> {{ a.treatment.prescription_text }}</div>
              <div v-if="a.treatment.follow_up_notes" class="treat-row">
                <span class="treat-label">Notes:</span> {{ a.treatment.follow_up_notes }}
              </div>
              <div v-if="a.treatment.next_visit_date" class="treat-row">
                <span class="treat-label">Next Visit:</span> {{ a.treatment.next_visit_date }}
              </div>
            </div>
            <div v-else-if="a.booking_status === 'Booked'" class="no-treatment">
              <em>Treatment not yet recorded</em>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>
