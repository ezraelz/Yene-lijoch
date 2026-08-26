export type TeacherClass = {
  id: string;
  name: string;
  grade: string;
  subject: string;
  room: string;
  students: number;
  presentToday: number;
  nextLesson: string;
};

export type Student = {
  id: string;
  name: string;
  initials: string;
  color: string;
  classId: string;
  grade: string;
  attendance: number;
  progress: number;
  parent: string;
  notes: string;
};

export type TeacherLesson = {
  id: string;
  title: string;
  classId: string;
  time: string;
  duration: string;
  room: string;
  status: "done" | "now" | "upcoming";
};

export type TeacherEvent = {
  id: string;
  title: string;
  date: string;
  time: string;
  location: string;
  description: string;
};

export type TeacherUpdate = {
  id: string;
  title: string;
  body: string;
  time: string;
  type: "notifications" | "announcements" | "messages";
  unread: boolean;
};

export const TEACHER = {
  name: "Hana Bekele",
  title: "Homeroom Teacher",
  email: "teacher@test.com",
  phone: "+251 91 888 2211",
  subject: "Amharic & Science",
  school: "Yene Lijoch Academy",
};

export const CLASSES: TeacherClass[] = [
  {
    id: "g3-amharic",
    name: "Grade 3 Amharic",
    grade: "Grade 3",
    subject: "Amharic",
    room: "Room 12",
    students: 24,
    presentToday: 23,
    nextLesson: "Today, 10:30 AM",
  },
  {
    id: "g3-science",
    name: "Grade 3 Science",
    grade: "Grade 3",
    subject: "Science",
    room: "Room 12",
    students: 24,
    presentToday: 22,
    nextLesson: "Today, 1:00 PM",
  },
  {
    id: "g1-home",
    name: "Grade 1 Homeroom",
    grade: "Grade 1",
    subject: "Homeroom",
    room: "Room 4",
    students: 18,
    presentToday: 18,
    nextLesson: "Tomorrow, 8:15 AM",
  },
];

export const STUDENTS: Student[] = [
  {
    id: "selam",
    name: "Selam Abebe",
    initials: "SA",
    color: "#6C63FF",
    classId: "g3-amharic",
    grade: "Grade 3",
    attendance: 96,
    progress: 78,
    parent: "Tsegaab Melat",
    notes: "Strong reader. Encourage more speaking practice.",
  },
  {
    id: "yonas",
    name: "Yonas Tadesse",
    initials: "YT",
    color: "#F28C28",
    classId: "g3-amharic",
    grade: "Grade 3",
    attendance: 88,
    progress: 64,
    parent: "Marta Tadesse",
    notes: "Needs extra support with fidel tracing.",
  },
  {
    id: "liya",
    name: "Liya Mekonnen",
    initials: "LM",
    color: "#2BB673",
    classId: "g3-amharic",
    grade: "Grade 3",
    attendance: 100,
    progress: 91,
    parent: "Daniel Mekonnen",
    notes: "Excellent participation this week.",
  },
  {
    id: "abel",
    name: "Abel Abebe",
    initials: "AA",
    color: "#3B82F6",
    classId: "g1-home",
    grade: "Grade 1",
    attendance: 91,
    progress: 64,
    parent: "Tsegaab Melat",
    notes: "Settling well. Loves story time.",
  },
  {
    id: "sara",
    name: "Sara Hailu",
    initials: "SH",
    color: "#E5484D",
    classId: "g3-science",
    grade: "Grade 3",
    attendance: 93,
    progress: 72,
    parent: "Bethlehem Hailu",
    notes: "Curious about animals and experiments.",
  },
];

export const TODAY_LESSONS: TeacherLesson[] = [
  {
    id: "l1",
    title: "Amharic Letters: ሀ to ነ",
    classId: "g3-amharic",
    time: "8:30 AM",
    duration: "40 min",
    room: "Room 12",
    status: "done",
  },
  {
    id: "l2",
    title: "Reading Circle",
    classId: "g3-amharic",
    time: "10:30 AM",
    duration: "30 min",
    room: "Room 12",
    status: "now",
  },
  {
    id: "l3",
    title: "Ethiopian Animals",
    classId: "g3-science",
    time: "1:00 PM",
    duration: "45 min",
    room: "Room 12",
    status: "upcoming",
  },
];

export const TEACHER_EVENTS: TeacherEvent[] = [
  {
    id: "te1",
    title: "Parent-Teacher Conference",
    date: "Aug 22, 2026",
    time: "4:00 PM",
    location: "Room 12",
    description: "Meet families from Grade 3 Amharic to review progress and goals.",
  },
  {
    id: "te2",
    title: "Science Fair Preview",
    date: "Aug 25, 2026",
    time: "10:00 AM",
    location: "School Hall",
    description: "Grade 3 presents mini experiments. Coordinate booth setup at 9:15 AM.",
  },
  {
    id: "te3",
    title: "Staff Planning",
    date: "Aug 27, 2026",
    time: "3:30 PM",
    location: "Teachers' Lounge",
    description: "Weekly planning for next term lessons and attendance follow-up.",
  },
];

export const TEACHER_UPDATES: TeacherUpdate[] = [
  {
    id: "u1",
    title: "Selam completed a lesson",
    body: "Story Time: The Clever Fox is marked complete.",
    time: "12 min ago",
    type: "notifications",
    unread: true,
  },
  {
    id: "u2",
    title: "Attendance reminder",
    body: "2 students in Grade 3 Science are still unmarked.",
    time: "40 min ago",
    type: "notifications",
    unread: true,
  },
  {
    id: "u3",
    title: "Assembly on Friday",
    body: "All Grade 3 classes should arrive at the hall by 8:50 AM.",
    time: "Yesterday",
    type: "announcements",
    unread: false,
  },
  {
    id: "u4",
    title: "New reading books",
    body: "Library dropped Amharic readers in Room 12 this morning.",
    time: "2 days ago",
    type: "announcements",
    unread: false,
  },
  {
    id: "u5",
    title: "Message from Tsegaab",
    body: "Can we talk about Selam's speaking practice this week?",
    time: "1 hour ago",
    type: "messages",
    unread: true,
  },
  {
    id: "u6",
    title: "Message from Marta",
    body: "Yonas will leave 20 minutes early on Thursday.",
    time: "Yesterday",
    type: "messages",
    unread: false,
  },
];

export const TEACHER_ACTIVITY = [
  { id: "a1", title: "Marked Grade 3 Amharic attendance", time: "Today, 8:20 AM" },
  { id: "a2", title: "Started Reading Circle", time: "Today, 10:30 AM" },
  { id: "a3", title: "Sent note to Selam's parent", time: "Yesterday" },
  { id: "a4", title: "Registered for conference", time: "Yesterday" },
];

export const WEEK_DAYS = [
  { d: "Thu", n: "20" },
  { d: "Fri", n: "21" },
  { d: "Sat", n: "22" },
  { d: "Sun", n: "23" },
  { d: "Mon", n: "24" },
  { d: "Tue", n: "25" },
  { d: "Wed", n: "26" },
];
