import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import {
  Screen,
  TopBar,
  Card,
  SectionHeader,
} from "../../components/parent/ui";
import {
  TEACHER,
  CLASSES,
  TEACHER_EVENTS,
  TEACHER_ACTIVITY,
  TEACHER_UPDATES,
  TODAY_LESSONS,
} from "../../data/teacherMock";
import { ParentColors as C } from "../../constants/parentTheme";

export default function TeacherHome() {
  const unread = TEACHER_UPDATES.filter((u) => u.unread).length;
  const present = CLASSES.reduce((sum, c) => sum + c.presentToday, 0);
  const students = CLASSES.reduce((sum, c) => sum + c.students, 0);
  const nextLesson = TODAY_LESSONS.find((l) => l.status !== "done") ?? TODAY_LESSONS[0];
  const upcoming = TEACHER_EVENTS[0];

  return (
    <Screen>
      <TopBar
        title={`Hi, ${TEACHER.name.split(" ")[0]} 👋`}
        subtitle={`${TEACHER.title} · ${TEACHER.school}`}
        unread={unread}
        bellHref="/teacher/updates"
      />

      <Card style={styles.summary}>
        <Text style={styles.summaryTitle}>Today's Summary</Text>
        <View style={styles.statRow}>
          <Stat label="Classes" value={`${CLASSES.length}`} />
          <Stat label="Present" value={`${present}/${students}`} />
          <Stat label="Lessons" value={`${TODAY_LESSONS.length}`} />
        </View>
        <View style={styles.nextBox}>
          <Ionicons name="time-outline" size={18} color={C.accent} />
          <Text style={styles.nextText}>
            Next: {nextLesson.title} · {nextLesson.time}
          </Text>
        </View>
      </Card>

      <SectionHeader
        title="My Classes"
        action="See all"
        onPress={() => router.push("/teacher/classes")}
      />
      {CLASSES.slice(0, 2).map((item) => (
        <Card
          key={item.id}
          style={styles.classCard}
          onPress={() => router.push(`/teacher/classes/${item.id}`)}
        >
          <View style={styles.classTop}>
            <View style={styles.classIcon}>
              <Ionicons name="people" size={18} color={C.accent} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>{item.name}</Text>
              <Text style={styles.meta}>
                {item.students} students · {item.room}
              </Text>
            </View>
          </View>
          <Text style={styles.meta}>Next lesson: {item.nextLesson}</Text>
        </Card>
      ))}

      <SectionHeader title="Quick Actions" />
      <View style={styles.actions}>
        <Action
          icon="people-outline"
          label="Classes"
          onPress={() => router.push("/teacher/classes")}
        />
        <Action
          icon="calendar-outline"
          label="Schedule"
          onPress={() => router.push("/teacher/schedule")}
        />
        <Action
          icon="checkmark-done-outline"
          label="Attendance"
          onPress={() => router.push(`/teacher/classes/${CLASSES[0].id}`)}
        />
        <Action
          icon="chatbubble-ellipses-outline"
          label="Updates"
          onPress={() => router.push("/teacher/updates")}
        />
      </View>

      <SectionHeader
        title="Upcoming Events"
        action="Calendar"
        onPress={() => router.push("/teacher/schedule")}
      />
      <Card onPress={() => router.push(`/teacher/schedule/${upcoming.id}`)}>
        <Text style={styles.kicker}>Event</Text>
        <Text style={styles.cardTitle}>{upcoming.title}</Text>
        <Text style={styles.meta}>
          {upcoming.date} · {upcoming.time}
        </Text>
        <Text style={styles.meta}>{upcoming.location}</Text>
      </Card>

      <SectionHeader title="Recent Activity" />
      <Card>
        {TEACHER_ACTIVITY.map((item, index) => (
          <View
            key={item.id}
            style={[
              styles.activityRow,
              index < TEACHER_ACTIVITY.length - 1 && styles.activityBorder,
            ]}
          >
            <View style={styles.activityIcon}>
              <Ionicons name="ellipse" size={8} color={C.accent} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.activityTitle}>{item.title}</Text>
              <Text style={styles.meta}>{item.time}</Text>
            </View>
          </View>
        ))}
      </Card>
    </Screen>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function Action({
  icon,
  label,
  onPress,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.action} onPress={onPress}>
      <View style={styles.actionIcon}>
        <Ionicons name={icon} size={20} color={C.accent} />
      </View>
      <Text style={styles.actionLabel}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  summary: { marginBottom: 4 },
  summaryTitle: { fontWeight: "800", color: C.text, marginBottom: 12, fontSize: 16 },
  statRow: { flexDirection: "row", gap: 8 },
  stat: {
    flex: 1,
    backgroundColor: C.accentSoft,
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: "center",
  },
  statValue: { fontWeight: "800", color: C.text, fontSize: 15 },
  statLabel: { marginTop: 4, color: C.muted, fontSize: 11, fontWeight: "600" },
  nextBox: {
    marginTop: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: C.bg,
    borderRadius: 12,
    padding: 10,
  },
  nextText: { flex: 1, color: C.text, fontWeight: "600", fontSize: 13 },
  classCard: { marginBottom: 10 },
  classTop: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 8 },
  classIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: C.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  kicker: { color: C.accent, fontWeight: "800", fontSize: 12, marginBottom: 6 },
  cardTitle: { fontSize: 16, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted, fontSize: 13 },
  actions: { flexDirection: "row", gap: 10 },
  action: { flex: 1, alignItems: "center" },
  actionIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: C.card,
    borderWidth: 1,
    borderColor: C.border,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  actionLabel: { fontSize: 12, fontWeight: "700", color: C.text },
  activityRow: { flexDirection: "row", alignItems: "center", gap: 12, paddingVertical: 10 },
  activityBorder: { borderBottomWidth: 1, borderBottomColor: C.border },
  activityIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: C.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  activityTitle: { fontWeight: "700", color: C.text },
});
