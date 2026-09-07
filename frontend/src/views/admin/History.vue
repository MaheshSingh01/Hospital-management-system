<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>Treatment History</h2>
      <div style="display:flex; gap:10px;">
        <button class="btn btn-outline" @click="triggerExport" :disabled="exporting">
          {{ exporting ? 'Queuing…' : '⬇ Export as CSV' }}
        </button>
        <button v-if="exportDone" class="btn btn-success" @click="downloadCsv">
          ⬇ Download CSV
        </button>
      </div>
    </div>

    <div v-if="exportMsg" class="alert alert-info">{{ exportMsg }}</div>
    <div v-if="loading" class="loading">Loading history…</div>
    <div v-else-if="history.length === 0" class="empty-state card">
      <div class="icon">📋</div><p>No appointment history found</p>
    </div>
    <div v-else class="history-list">
      <div v-for="a in history" :key="a.id" class="history-card card">
        <div class="history-top">
          <div class="history-meta">
            <span class="doctor-name">Dr. {{ a.doctor_name }}</span>
            <span class="dept-name" v-if="a.doctor_dept">· {{ a.doctor_dept }}</span>
          </div>
          <div class="history-right">
            <span class="date-chip">{{ a.scheduled_date }} at {{ a.scheduled_time }}</span>
            <span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span>
          </div>
        </div>

        <div v-if="a.treatment" class="treatment-section">
          <div class="treat-grid">
            <div class="treat-block">
              <div class="treat-label">Diagnosis</div>
              <div class="treat-value">{{ a.treatment.diagnosis_text }}</div>
            </div>
            <div class="treat-block">
              <div class="treat-label">Prescription</div>
              <div class="treat-value">{{ a.treatment.prescription_text }}</div>
            </div>
            <div v-if="a.treatment.follow_up_notes" class="treat-block full">
              <div class="treat-label">Doctor's Notes</div>
              <div class="treat-value">{{ a.treatment.follow_up_notes }}</div>
            </div>
            <div v-if="a.treatment.next_visit_date" class="treat-block">
              <div class="treat-label">Next Visit</div>
              <div class="treat-value">{{ a.treatment.next_visit_date }}</div>
            </div>
          </div>
        </div>

        <div v-else-if="a.booking_status === 'Booked'" class="pending-tag">
          Treatment to be recorded after visit
        </div>
        <div v-else-if="a.booking_status === 'Cancelled'" class="cancelled-tag">
          Appointment was cancelled
        </div>
      </div>
    </div>
  </Layout>
</template>
