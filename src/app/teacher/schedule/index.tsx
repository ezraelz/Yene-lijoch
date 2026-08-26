import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card, SectionHeader } from "../../../components/parent/ui";
import {
  WEEK_DAYS,
  TODAY_LESSONS,
  TEACHER_EVENTS,
  CLASSES,
  TEACHER_UPDATES,
} from "../../../data/teacherMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function ScheduleScreen() {
  const [selectedDay, setSelectedDay] = useState("22");
  const unread = TEACHER_UPDATES.filter((u) => u.unread).length;

  return (
    <Screen>
      <TopBar
        title="Schedule"
        subtitle="Lessons and events"
        unread={unread}
        bellHref="/teacher/updates"
      />

      <SectionHeader title="Calendar" />
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 8 }}>
        {WEEK_DAYS.map((day) => {
          const active = selectedDay === day.n;
          return (
            <Card
              key={day.n}
              style={[styles.day, active && styles.dayActive]}
              onPress={() => setSelectedDay(day.n)}
            >
              <Text style={[styles.dayName, active && { color: "#fff" }]}>{day.d}</Text>
              <Text style={[styles.dayNum, active && { color: "#fff" }]}>{day.n}</Text>
            </Card>
          );
        })}
      </ScrollView>

      <SectionHeader title="Today's Lessons" />
      {TODAY_LESSONS.map((lesson) => {
        const classItem = CLASSES.find((c) => c.id === lesson.classId);
        return (
          <Card
            key={lesson.id}
            style={styles.card}
            onPress={() => router.push(`/teacher/classes/${lesson.classId}`)}
          >
            <View style={styles.lessonTop}>
              <Text style={styles.status}>{lesson.status}</Text>
              <Text style={styles.time}>{lesson.time}</Text>
            </View>
            <Text style={styles.title}>{lesson.title}</Text>
            <Text style={styles.meta}>
              {classItem?.name ?? "Class"} · {lesson.duration} · {lesson.room}
            </Text>
          </Card>
        );
      })}

      <SectionHeader title="Upcoming Events" />
      {TEACHER_EVENTS.map((event) => (
        <Card
          key={event.id}
          style={styles.card}
          onPress={() => router.push(`/teacher/schedule/${event.id}`)}
        >
          <Text style={styles.kicker}>Event</Text>
          <Text style={styles.title}>{event.title}</Text>
          <Text style={styles.meta}>
            {event.date} · {event.time}
          </Text>
          <Text style={styles.meta}>{event.location}</Text>
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  day: { width: 62, alignItems: "center", marginRight: 8, paddingVertical: 12 },
  dayActive: { backgroundColor: C.accent, borderColor: C.accent },
  dayName: { color: C.muted, fontWeight: "700", fontSize: 12 },
  dayNum: { marginTop: 4, fontSize: 18, fontWeight: "800", color: C.text },
  card: { marginBottom: 10 },
  lessonTop: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  status: {
    color: C.accent,
    fontWeight: "800",
    fontSize: 12,
    textTransform: "capitalize",
  },
  time: { color: C.muted, fontWeight: "700", fontSize: 12 },
  kicker: { color: C.accent, fontWeight: "800", fontSize: 12, marginBottom: 6 },
  title: { fontSize: 16, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted, fontSize: 13 },
});
