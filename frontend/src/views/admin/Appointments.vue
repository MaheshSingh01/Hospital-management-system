<template>
  <Layout :nav-items="navItems">
    <div class="page-header">
      <h2>All Appointments</h2>
    </div>

    <div class="card filter-bar" style="margin-bottom: 20px;">
      <select v-model="statusFilter" class="form-control" style="max-width: 200px;">
        <option value="">All Statuses</option>
        <option value="Booked">Booked</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <!-- Appointments Table -->
    <div class="card" style="margin-bottom: 30px;">
      <div v-if="loading" class="loading">Loading appointments…</div>
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="icon">📅</div><p>No appointments found</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>#</th><th>Patient</th><th>Doctor</th>
            <th>Department</th><th>Date</th><th>Time</th>
            <th>Status</th><th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in filtered" :key="a.id">
            <td><code>{{ a.display_id }}</code></td>
            <td>{{ a.patient_name }}</td>
            <td>Dr. {{ a.doctor_name }}</td>
            <td>{{ a.doctor_dept || '—' }}</td>
            <td>{{ a.scheduled_date }}</td>
            <td>{{ a.scheduled_time }}</td>
            <td>
              <span class="badge" :class="`badge-${a.booking_status.toLowerCase()}`">
                {{ a.booking_status }}
              </span>
            </td>
            <td>
              <button
                v-if="a.booking_status === 'Booked'"
                class="btn-small btn-danger"
                @click="openCancelModal(a.id)"
              >Cancel</button>
              <span v-else class="muted-text">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Doctor Schedule Management -->
    <div class="card">
      <h3 style="margin-bottom: 16px;">Manage Doctor Availability Slots</h3>

      <div class="form-group" style="max-width: 300px;">
        <label>Select Doctor</label>
        <select v-model="selectedDoctorId" class="form-control" @change="loadDoctorSlots">
          <option value="">-- Choose a doctor --</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">Dr. {{ d.full_name }}</option>
        </select>
      </div>

      <div v-if="selectedDoctorId" class="slot-form">
        <h4 style="margin-bottom: 12px;">Add New Slot</h4>
        <div class="slot-form-row">
          <div class="form-group">
            <label>Date</label>
            <input v-model="newSlot.avail_date" type="date" class="form-control" />
          </div>
          <div class="form-group">
            <label>Start Time</label>
            <input v-model="newSlot.slot_start" type="time" class="form-control" />
          </div>
          <div class="form-group">
            <label>End Time</label>
            <input v-model="newSlot.slot_end" type="time" class="form-control" />
          </div>
          <div class="form-group" style="align-self: flex-end;">
            <button class="btn btn-primary" @click="addSlot">Add Slot</button>
          </div>
        </div>
        <div v-if="slotErr" class="alert alert-error" style="margin-top: 8px;">{{ slotErr }}</div>
        <div v-if="slotSuccess" class="alert alert-success" style="margin-top: 8px;">{{ slotSuccess }}</div>
      </div>

      <div v-if="selectedDoctorId && doctorSlots.length > 0" style="margin-top: 20px;">
        <h4 style="margin-bottom: 12px;">Existing Slots</h4>
        <table>
          <thead>
            <tr><th>Date</th><th>Start</th><th>End</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in doctorSlots" :key="s.id">
              <td>{{ s.avail_date }}</td>
              <td>{{ s.slot_start }}</td>
              <td>{{ s.slot_end }}</td>
              <td>
                <button class="btn-small btn-danger" @click="openRemoveSlotModal(s.id)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="selectedDoctorId" style="margin-top: 16px; color: var(--muted);">
        No slots added for this doctor yet.
      </div>
    </div>

    <!-- Cancel Appointment -->
    <div v-if="showCancelModal" class="modal-overlay" @click.self="showCancelModal = false">
      <div class="modal-box confirm-box">
        <div class="confirm-icon">⚠️</div>
        <h3>Cancel Appointment?</h3>
        <p class="modal-sub">This will cancel the appointment permanently. This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCancelModal = false">Keep It</button>
          <button class="btn-small btn-danger" @click="confirmCancel" :disabled="cancelling">
            {{ cancelling ? 'Cancelling…' : 'Yes, Cancel It' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Remove Slot -->
    <div v-if="showRemoveSlotModal" class="modal-overlay" @click.self="showRemoveSlotModal = false">
      <div class="modal-box confirm-box">
        <div class="confirm-icon">🗑️</div>
        <h3>Remove This Slot?</h3>
        <p class="modal-sub">This availability slot will be permanently removed from the doctor's schedule.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showRemoveSlotModal = false">Keep It</button>
          <button class="btn-small btn-danger" @click="confirmRemoveSlot">Yes, Remove It</button>
        </div>
      </div>
    </div>

  </Layout>
</template>
