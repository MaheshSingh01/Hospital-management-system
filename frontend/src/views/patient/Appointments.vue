<template>
  <Layout :nav-items="navItems">
    <div class="page-header"><h2>My Appointments</h2></div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div class="card">
      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="appointments.length === 0" class="empty-state">
        <div class="icon">📅</div>
        <p>No appointments found. <router-link to="/patient/doctors">Book one now!</router-link></p>
      </div>
      <table v-else>
        <thead>
          <tr><th>Doctor</th><th>Dept.</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in appointments" :key="a.id">
            <td>Dr. {{ a.doctor_name }}</td>
            <td>{{ a.doctor_dept || '—' }}</td>
            <td>{{ a.scheduled_date }}</td>
            <td>{{ a.scheduled_time }}</td>
            <td><span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">{{ a.booking_status }}</span></td>
            <td>
              <div class="action-btns" v-if="a.booking_status === 'Booked'">
                <button class="btn btn-warning btn-sm" @click="openReschedule(a)">🔄 Reschedule</button>
                <button class="btn btn-danger btn-sm" @click="openCancel(a)">✗ Cancel</button>
              </div>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reschedule -->
    <div v-if="showReschedModal" class="modal-overlay" @click.self="showReschedModal = false">
      <div class="modal-box">
        <h3>Reschedule Appointment</h3>
        <p class="modal-sub">
          Dr. {{ activeAppt?.doctor_name }} —
          Currently: {{ activeAppt?.scheduled_date }} at {{ activeAppt?.scheduled_time }}
        </p>

        <div v-if="rescheduleErr" class="alert alert-error">{{ rescheduleErr }}</div>

        <div v-if="slotsLoading" class="loading" style="margin-top: 16px;">Loading available slots…</div>
        <div v-else-if="availableSlots.length === 0" class="empty-state" style="padding: 20px;">
          <p>No available slots for this doctor in the next 7 days.</p>
        </div>
        <div v-else style="margin-top: 16px;">
          <label class="slot-label">Select a New Slot</label>
          <div class="slots-grid">
            <div
              v-for="slot in availableSlots"
              :key="slot.id"
              class="slot-card"
              :class="{ selected: reschedForm.slot_id === slot.id }"
              @click="selectSlot(slot)"
            >
              <div class="slot-date">{{ slot.avail_date }}</div>
              <div class="slot-time">{{ slot.slot_start }} – {{ slot.slot_end }}</div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="showReschedModal = false">Close</button>
          <button class="btn btn-primary" @click="submitReschedule" :disabled="saving || !reschedForm.slot_id">
            {{ saving ? 'Saving…' : 'Confirm Reschedule' }}
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
          You are about to cancel your appointment with
          <strong>Dr. {{ activeAppt?.doctor_name }}</strong>
          on <strong>{{ activeAppt?.scheduled_date }}</strong> at
          <strong>{{ activeAppt?.scheduled_time }}</strong>.
        </p>
        <p class="confirm-note">This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCancelModal = false">Keep Appointment</button>
          <button class="btn btn-danger" @click="confirmCancel" :disabled="cancelling">
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel It' }}
          </button>
        </div>
      </div>
    </div>

  </Layout>
</template>
