export type Child = {
  id: string;
  name: string;
  grade: string;
  school: string;
  age: number;
  avatarColor: string;
  initials: string;
  attendance: number;
  overallProgress: number;
  streak: number;
};

export type Lesson = {
  id: string;
  title: string;
  subject: string;
  category: string;
  duration: string;
  progress: number;
  status: "continue" | "recommended" | "completed";
  teacher: string;
  description: string;
};

export type EventItem = {
  id: string;
  title: string;
  date: string;
  time: string;
  location: string;
  type: "school" | "learning" | "community";
  status: "upcoming" | "registered" | "past";
  description: string;
};

export type NotificationItem = {
  id: string;
  title: string;
  body: string;
  time: string;
  category: "learning" | "teacher" | "events" | "attendance" | "system";
  unread: boolean;
};

export type Activity = {
  id: string;
  title: string;
  time: string;
  icon: "book-outline" | "trophy-outline" | "calendar-outline" | "checkmark-circle-outline";
};

export const PARENT = {
  name: "Tsegaab Melat",
  email: "parent@test.com",
  phone: "+251 91 234 5678",
  role: "Parent",
};

export const CHILDREN: Child[] = [
  {
    id: "selam",
    name: "Selam Abebe",
    grade: "Grade 3",
    school: "Yene Lijoch Academy",
    age: 8,
    avatarColor: "#6C63FF",
    initials: "SA",
    attendance: 96,
    overallProgress: 78,
    streak: 12,
  },
  {
    id: "abel",
    name: "Abel Abebe",
    grade: "Grade 1",
    school: "Yene Lijoch Academy",
    age: 6,
    avatarColor: "#F28C28",
    initials: "AA",
    attendance: 91,
    overallProgress: 64,
    streak: 5,
  },
];

export const LESSONS: Lesson[] = [
  {
    id: "1",
    title: "Amharic Letters: ሀ to ነ",
    subject: "Amharic",
    category: "Language",
    duration: "18 min",
    progress: 62,
    status: "continue",
    teacher: "Mrs. Hana",
    description:
      "Practice reading and writing the first set of Amharic fidel with sounds, tracing, and short words.",
  },
  {
    id: "2",
    title: "Adding Within 20",
    subject: "Math",
    category: "Math",
    duration: "15 min",
    progress: 40,
    status: "continue",
    teacher: "Mr. Dawit",
    description:
      "Build number sense with visual blocks, number lines, and quick practice quizzes.",
  },
  {
    id: "3",
    title: "Ethiopian Animals",
    subject: "Science",
    category: "Science",
    duration: "12 min",
    progress: 0,
    status: "recommended",
    teacher: "Mrs. Hana",
    description:
      "Discover animals of Ethiopia, their habitats, and a short matching game.",
  },
  {
    id: "4",
    title: "Story Time: The Clever Fox",
    subject: "Reading",
    category: "Language",
    duration: "10 min",
    progress: 100,
    status: "completed",
    teacher: "Mrs. Hana",
    description: "Listen to a short story, answer 4 questions, and earn a reading badge.",
  },
  {
    id: "5",
    title: "Shapes Around Us",
    subject: "Math",
    category: "Math",
    duration: "14 min",
    progress: 100,
    status: "completed",
    teacher: "Mr. Dawit",
    description: "Identify circles, triangles, and rectangles in everyday objects.",
  },
  {
    id: "6",
    title: "Kindness in Class",
    subject: "Social",
    category: "Social",
    duration: "8 min",
    progress: 0,
    status: "recommended",
    teacher: "Mr. Yonas",
    description: "A short lesson on sharing, listening, and being a good classmate.",
  },
];

export const CATEGORIES = ["All", "Language", "Math", "Science", "Social"];

export const EVENTS: EventItem[] = [
  {
    id: "e1",
    title: "Parent-Teacher Conference",
    date: "Aug 22, 2026",
    time: "4:00 PM",
    location: "Room 12, Main Building",
    type: "school",
    status: "registered",
    description:
      "Meet Selam's teachers to review progress, attendance, and goals for the next term.",
  },
  {
    id: "e2",
    title: "Science Fair Preview",
    date: "Aug 25, 2026",
    time: "10:00 AM",
    location: "School Hall",
    type: "learning",
    status: "upcoming",
    description: "Children present mini experiments. Parents are welcome to visit booths.",
  },
  {
    id: "e3",
    title: "Reading Circle",
    date: "Aug 28, 2026",
    time: "3:30 PM",
    location: "Library",
    type: "community",
    status: "upcoming",
    description: "Join a 40-minute family reading session with Amharic and English stories.",
  },
  {
    id: "e4",
    title: "Sports Day",
    date: "Aug 10, 2026",
    time: "9:00 AM",
    location: "Playground",
    type: "school",
    status: "past",
    description: "Team games, relays, and certificates for participation.",
  },
];

export const NOTIFICATIONS: NotificationItem[] = [
  {
    id: "n1",
    title: "Lesson completed",
    body: "Selam finished Story Time: The Clever Fox.",
    time: "12 min ago",
    category: "learning",
    unread: true,
  },
  {
    id: "n2",
    title: "Note from Mrs. Hana",
    body: "Great participation in Amharic class today.",
    time: "1 hour ago",
    category: "teacher",
    unread: true,
  },
  {
    id: "n3",
    title: "Event reminder",
    body: "Parent-Teacher Conference is on Aug 22 at 4:00 PM.",
    time: "Yesterday",
    category: "events",
    unread: false,
  },
  {
    id: "n4",
    title: "Attendance update",
    body: "Selam was present all week. Attendance is 96%.",
    time: "2 days ago",
    category: "attendance",
    unread: false,
  },
  {
    id: "n5",
    title: "App update",
    body: "New progress charts are available in the Progress tab.",
    time: "3 days ago",
    category: "system",
    unread: false,
  },
];

export const ACTIVITIES: Activity[] = [
  {
    id: "a1",
    title: "Completed Story Time",
    time: "Today, 10:20 AM",
    icon: "trophy-outline",
  },
  {
    id: "a2",
    title: "Continued Amharic Letters",
    time: "Today, 9:05 AM",
    icon: "book-outline",
  },
  {
    id: "a3",
    title: "Marked present",
    time: "Today, 8:15 AM",
    icon: "checkmark-circle-outline",
  },
  {
    id: "a4",
    title: "Registered for conference",
    time: "Yesterday",
    icon: "calendar-outline",
  },
];

export const WEEKLY_ACTIVITY = [
  { day: "Mon", value: 40 },
  { day: "Tue", value: 70 },
  { day: "Wed", value: 55 },
  { day: "Thu", value: 90 },
  { day: "Fri", value: 65 },
  { day: "Sat", value: 30 },
  { day: "Sun", value: 20 },
];

export const SUBJECT_PROGRESS = [
  { name: "Amharic", value: 82, color: "#6C63FF" },
  { name: "Math", value: 74, color: "#F28C28" },
  { name: "Science", value: 61, color: "#2BB673" },
  { name: "Reading", value: 88, color: "#3B82F6" },
];

export const ACHIEVEMENTS = [
  { id: "g1", title: "7-Day Streak", emoji: "🔥" },
  { id: "g2", title: "First 10 Lessons", emoji: "📘" },
  { id: "g3", title: "Kind Helper", emoji: "💛" },
  { id: "g4", title: "Math Star", emoji: "⭐" },
];
