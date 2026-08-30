<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>My Appointments</h2>
      <div class="filter-tabs">
        <button v-for="t in tabs" :key="t.val" class="tab-btn" :class="{ active: view === t.val }" @click="switchView(t.val)">
          {{ t.label }}
        </button>
      </div>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div class="card">
      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="appointments.length === 0" class="empty-state">
        <div class="icon">📅</div><p>No appointments in this view</p>
      </div>
      <table v-else>
        <thead>
          <tr><th>Date</th><th>Time</th><th>Patient</th><th>Status</th><th>Treatment</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in appointments" :key="a.id">
            <td>{{ a.scheduled_date }}</td>
            <td>{{ a.scheduled_time }}</td>
            <td><strong>{{ a.patient_name }}</strong></td>
            <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
            <td>
              <span v-if="a.has_treatment" class="badge badge-completed">Recorded</span>
              <span v-else class="badge badge-pending">None</span>
            </td>
            <td>
              <div class="action-btns" v-if="a.booking_status === 'Booked'">
                <button class="btn btn-success btn-sm" @click="openCompleteModal(a)">✓ Complete</button>
                <button class="btn btn-outline btn-sm" @click="openRescheduleModal(a)">↺ Reschedule</button>
                <button class="btn btn-danger btn-sm" @click="openCancelModal(a)">✗ Cancel</button>
              </div>
              <button v-else-if="a.booking_status === 'Completed'" class="btn btn-outline btn-sm" @click="openCompleteModal(a)">
                View/Edit
              </button>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Complete Appointment -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3>Complete Appointment — {{ activeAppt?.patient_name }}</h3>
        <p class="modal-sub">{{ activeAppt?.scheduled_date }} at {{ activeAppt?.scheduled_time }}</p>
        <div class="form-group" style="margin-top: 16px;">
          <label>Diagnosis *</label>
          <textarea v-model="treatForm.diagnosis_text" class="form-control" rows="3" placeholder="Enter diagnosis details…" required></textarea>
        </div>
        <div class="form-group">
          <label>Prescription *</label>
          <textarea v-model="treatForm.prescription_text" class="form-control" rows="3" placeholder="Medicines and dosage…" required></textarea>
        </div>
        <div class="form-group">
          <label>Follow-up Notes</label>
          <textarea v-model="treatForm.follow_up_notes" class="form-control" rows="2" placeholder="Additional notes for patient…"></textarea>
        </div>
        <div class="form-group">
          <label>Next Visit Date</label>
          <input v-model="treatForm.next_visit_date" type="date" class="form-control" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">Close</button>
          <button class="btn btn-success" @click="submitComplete" :disabled="saving">
            {{ saving ? 'Saving…' : 'Mark as Completed' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRescheduleModal" class="modal-overlay" @click.self="showRescheduleModal = false">
      <div class="modal-box">
        <h3>Reschedule Appointment</h3>
        <p class="modal-sub">Patient: <strong>{{ activeAppt?.patient_name }}</strong> — Current: {{ activeAppt?.scheduled_date }} at {{ activeAppt?.scheduled_time }}</p>
        <div v-if="rescheduleErr" class="alert alert-error">{{ rescheduleErr }}</div>
        <div class="form-group" style="margin-top: 16px;">
          <label>New Date</label>
          <input v-model="rescheduleForm.scheduled_date" type="date" class="form-control" :min="today" required />
        </div>
        <div class="form-group">
          <label>New Time</label>
          <input v-model="rescheduleForm.scheduled_time" type="time" class="form-control" required />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showRescheduleModal = false">Cancel</button>
          <button class="btn btn-primary" @click="submitReschedule" :disabled="rescheduling">
            {{ rescheduling ? 'Saving…' : 'Confirm Reschedule' }}
          </button>
        </div>
      </div>
    </div>
    <!-- Cancel Confirmation -->
    <div v-if="showCancelModal" class="modal-overlay" @click.self="showCancelModal = false">
      <div class="modal-box confirm-box">
        <div class="confirm-icon">⚠️</div>
        <h3>Cancel Appointment?</h3>
        <p class="modal-sub">
          You are about to cancel the appointment with
          <strong>{{ activeAppt?.patient_name }}</strong>
          on <strong>{{ activeAppt?.scheduled_date }}</strong>
          at <strong>{{ activeAppt?.scheduled_time }}</strong>.
        </p>
        <p class="confirm-note">This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCancelModal = false">Keep It</button>
          <button class="btn btn-danger" @click="confirmCancel" :disabled="cancelling">
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel It' }}
          </button>
        </div>
      </div>
    </div>
  </Layout>
</template>
