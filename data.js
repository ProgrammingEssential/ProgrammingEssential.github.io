// ---- ABC Tutoring: shared data + booking logic ----

const AVATAR_COLORS = ['#3E7C59', '#E8A33D', '#5A82A6', '#B5654A', '#6B8E5A', '#C68F3E'];

const TUTORS = [
  { id: 't1', name: 'Maria Chen', subjects: ['Elementary Math', 'Algebra II'], grades: 'Grades 3–10', rate: 35 },
  { id: 't2', name: 'James Whitfield', subjects: ['Science'], grades: 'Grades 6–12', rate: 40 },
  { id: 't3', name: 'Priya Anand', subjects: ['Elementary Reading'], grades: 'Grades K–5', rate: 30 },
  { id: 't4', name: 'Sam Okafor', subjects: ['Algebra II', 'Elementary Math'], grades: 'Grades 5–9', rate: 38 },
  { id: 't5', name: 'Laura Bennett', subjects: ['Science', 'Elementary Reading'], grades: 'Grades K–8', rate: 32 },
  { id: 't6', name: 'David Kim', subjects: ['Elementary Math', 'Science'], grades: 'Grades 2–7', rate: 34 },
];

const ALL_SUBJECTS = ['Elementary Math', 'Algebra II', 'Science', 'Elementary Reading'];

function initials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function avatarColor(tutorId) {
  const idx = TUTORS.findIndex(t => t.id === tutorId);
  return AVATAR_COLORS[idx % AVATAR_COLORS.length];
}

// Generate upcoming slots for a tutor: a few weekday afternoons over the next 2 weeks.
function generateSlots(tutorId) {
  const idx = TUTORS.findIndex(t => t.id === tutorId);
  const times = ['3:30 PM', '4:30 PM', '5:30 PM'];
  const slots = [];
  const now = new Date();
  let dayOffset = 1;
  let count = 0;
  while (count < 5) {
    const d = new Date(now);
    d.setDate(d.getDate() + dayOffset);
    dayOffset++;
    const day = d.getDay();
    if (day === 0 || day === 6) continue; // skip weekends
    const time = times[(idx + count) % times.length];
    const label = d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) + ' · ' + time;
    slots.push({ id: tutorId + '_' + d.toISOString().slice(0, 10) + '_' + time.replace(/[: ]/g, ''), label });
    count++;
  }
  return slots;
}

// ---- Booking persistence (localStorage stands in for a backend in this prototype) ----
const BOOKINGS_KEY = 'abc_tutoring_bookings';

function getBookedSlotIds() {
  try {
    return JSON.parse(localStorage.getItem(BOOKINGS_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function getAvailableSlots(tutorId) {
  const booked = getBookedSlotIds();
  return generateSlots(tutorId).filter(s => !booked.includes(s.id));
}

function saveBooking(booking) {
  const all = JSON.parse(localStorage.getItem(BOOKINGS_KEY + '_details') || '[]');
  all.push(booking);
  localStorage.setItem(BOOKINGS_KEY + '_details', JSON.stringify(all));

  const bookedIds = getBookedSlotIds();
  bookedIds.push(booking.slotId);
  localStorage.setItem(BOOKINGS_KEY, JSON.stringify(bookedIds));
}

function getTutorById(id) {
  return TUTORS.find(t => t.id === id);
}
