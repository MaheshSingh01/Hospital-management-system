<template>
  <Layout :nav-items="navItems">
    <div class="page-header"><h2>Find a Doctor</h2></div>

    <div class="card" style="margin-bottom: 20px;">
      <div class="search-row">
        <input v-model="filters.name" class="form-control" placeholder="🔍 Search by doctor name…" @input="fetchDoctors" />
        <select v-model="filters.dept_id" class="form-control" @change="fetchDoctors" style="max-width: 220px;">
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="errMsg" class="alert alert-error">{{ errMsg }}</div>

    <div v-if="loading" class="loading">Loading doctors…</div>
    <div v-else-if="doctors.length === 0" class="empty-state card">
      <div class="icon">👨‍⚕️</div><p>No doctors match your search</p>
    </div>
    <div v-else class="doctors-grid">
      <div v-for="doc in doctors" :key="doc.id" class="doctor-card card">
        <div class="doc-top">
          <div class="doc-avatar">{{ initials(doc.full_name) }}</div>
          <div class="doc-info">
            <h3 class="doc-name">Dr. {{ doc.full_name }}</h3>
            <span class="dept-badge">{{ doc.department || 'General' }}</span>
          </div>
          <button class="btn-profile" @click="viewProfile(doc)" title="View Profile">
            <i class="fa-solid fa-circle-info"></i>
          </button>
        </div>

        <div class="slots-section">
          <p class="slots-title">Availability (Next 7 Days)</p>
          <div v-if="doc.available_slots && doc.available_slots.length > 0" class="slots-grid">
          <template v-for="s in doc.available_slots" :key="s.id">
            <button
              v-if="!isSlotBooked(doc, s)"
              class="slot-btn"
              :class="{ selected: selectedSlot?.id === s.id && selectedDoc?.id === doc.id }"
              @click="selectSlot(doc, s)"
            >
              {{ s.avail_date }}<br>
              <small>{{ s.slot_start }} – {{ s.slot_end }}</small>
            </button>
          </template>
          </div>
          <p v-else class="no-slots">No availability set for this week</p>
        </div>

        <button
          v-if="selectedDoc?.id === doc.id && selectedSlot"
          class="btn btn-primary"
          style="width: 100%; margin-top: 12px; justify-content: center;"
          :disabled="booking"
          @click="confirmBooking"
        >
          {{ booking ? 'Booking…' : 'Book This Appointment' }}
        </button>
      </div>
    </div>
<!-- Doctor Profile Modal -->
    <div v-if="showProfileModal" class="modal-overlay" @click.self="showProfileModal = false">
      <div class="modal-box">
        <div class="profile-modal-top">
          <div class="doc-avatar large">{{ initials(profileDoc.full_name) }}</div>
          <div>
            <h3>Dr. {{ profileDoc.full_name }}</h3>
            <span class="dept-badge">{{ profileDoc.department || 'General' }}</span>
          </div>
        </div>
        <div class="profile-modal-body">
          <div v-if="profileDoc.bio" class="bio-section">
            <div class="bio-label">About</div>
            <p class="bio-text">{{ profileDoc.bio }}</p>
          </div>
          <div v-else class="bio-section">
            <p class="bio-text muted">No bio available for this doctor.</p>
          </div>
          <div class="profile-detail">
            <i class="fa-solid fa-building-columns"></i>
            <span>{{ profileDoc.department || 'General Medicine' }}</span>
          </div>
        </div>
        <button class="btn btn-outline" style="width:100%; margin-top:16px;" @click="showProfileModal = false">Close</button>
      </div>
    </div>
  </Layout>
</template>
