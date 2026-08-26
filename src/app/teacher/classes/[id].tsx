import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import {
  Screen,
  TopBar,
  Card,
  Pill,
  PersonAvatar,
  ProgressBar,
} from "../../../components/parent/ui";
import {
  CLASSES,
  STUDENTS,
  TODAY_LESSONS,
} from "../../../data/teacherMock";
import { ParentColors as C } from "../../../constants/parentTheme";

const TABS = ["Students", "Attendance", "Lessons", "Info"] as const;

export default function ClassDetails() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const classItem = CLASSES.find((c) => c.id === id) ?? CLASSES[0];
  const [tab, setTab] = useState<(typeof TABS)[number]>("Students");
  const students = useMemo(
    () => STUDENTS.filter((s) => s.classId === classItem.id),
    [classItem.id]
  );
  const lessons = useMemo(
    () => TODAY_LESSONS.filter((l) => l.classId === classItem.id),
    [classItem.id]
  );
  const [present, setPresent] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(students.map((s) => [s.id, true]))
  );

  return (
    <Screen>
      <TopBar
        title={classItem.name}
        subtitle={`${classItem.room} · ${classItem.students} students`}
        showBell={false}
        onBack={() => router.back()}
      />

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 12 }}>
        {TABS.map((item) => (
          <Pill
            key={item}
            label={item}
            active={tab === item}
            onPress={() => setTab(item)}
          />
        ))}
      </ScrollView>

      {tab === "Students" ? (
        students.length === 0 ? (
          <Card>
            <Text style={styles.empty}>No students listed for this class yet.</Text>
          </Card>
        ) : (
          students.map((student) => (
            <Card
              key={student.id}
              style={styles.card}
              onPress={() => router.push(`/teacher/classes/student/${student.id}`)}
            >
              <View style={styles.row}>
                <PersonAvatar
                  initials={student.initials}
                  color={student.color}
                  size={46}
                />
                <View style={{ flex: 1 }}>
                  <Text style={styles.title}>{student.name}</Text>
                  <Text style={styles.meta}>
                    Progress {student.progress}% · Attendance {student.attendance}%
                  </Text>
                </View>
              </View>
            </Card>
          ))
        )
      ) : null}

      {tab === "Attendance" ? (
        <Card>
          <Text style={styles.section}>Mark attendance</Text>
          {students.map((student, index) => (
            <View
              key={student.id}
              style={[
                styles.attRow,
                index < students.length - 1 && styles.border,
              ]}
            >
              <PersonAvatar
                initials={student.initials}
                color={student.color}
                size={36}
              />
              <Text style={styles.attName}>{student.name}</Text>
              <TouchableOpacity
                style={[
                  styles.attBtn,
                  present[student.id] ? styles.present : styles.absent,
                ]}
                onPress={() =>
                  setPresent((prev) => ({
                    ...prev,
                    [student.id]: !prev[student.id],
                  }))
                }
              >
                <Text style={styles.attBtnText}>
                  {present[student.id] ? "Present" : "Absent"}
                </Text>
              </TouchableOpacity>
            </View>
          ))}
          <TouchableOpacity
            style={styles.save}
            onPress={() => Alert.alert("Saved", "Attendance was updated for today.")}
          >
            <Text style={styles.saveText}>Save attendance</Text>
          </TouchableOpacity>
        </Card>
      ) : null}

      {tab === "Lessons" ? (
        lessons.length === 0 ? (
          <Card>
            <Text style={styles.empty}>No lessons scheduled for this class today.</Text>
          </Card>
        ) : (
          lessons.map((lesson) => (
            <Card key={lesson.id} style={styles.card}>
              <Text style={styles.kicker}>{lesson.status}</Text>
              <Text style={styles.title}>{lesson.title}</Text>
              <Text style={styles.meta}>
                {lesson.time} · {lesson.duration} · {lesson.room}
              </Text>
            </Card>
          ))
        )
      ) : null}

      {tab === "Info" ? (
        <Card>
          <Text style={styles.section}>Class Information</Text>
          <Info label="Grade" value={classItem.grade} />
          <Info label="Subject" value={classItem.subject} />
          <Info label="Room" value={classItem.room} />
          <Info label="Students" value={`${classItem.students}`} />
          <Info label="Present today" value={`${classItem.presentToday}`} />
          <Info label="Next lesson" value={classItem.nextLesson} />
          <View style={{ marginTop: 14 }}>
            <Text style={styles.meta}>Class progress overview</Text>
            <View style={{ marginTop: 8 }}>
              <ProgressBar value={76} color={C.accent} />
            </View>
          </View>
        </Card>
      ) : null}
    </Screen>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 10 },
  row: { flexDirection: "row", alignItems: "center", gap: 12 },
  title: { fontSize: 15, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted, fontSize: 13 },
  empty: { color: C.muted, textAlign: "center" },
  section: { fontWeight: "800", color: C.text, fontSize: 16, marginBottom: 10 },
  attRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingVertical: 10,
  },
  border: { borderBottomWidth: 1, borderBottomColor: C.border },
  attName: { flex: 1, fontWeight: "700", color: C.text },
  attBtn: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 999,
  },
  present: { backgroundColor: C.successSoft },
  absent: { backgroundColor: "#FDECEC" },
  attBtnText: { fontWeight: "800", fontSize: 12, color: C.text },
  save: {
    marginTop: 14,
    height: 48,
    borderRadius: 14,
    backgroundColor: C.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  saveText: { color: "#fff", fontWeight: "800" },
  kicker: {
    color: C.accent,
    fontWeight: "800",
    fontSize: 12,
    textTransform: "capitalize",
    marginBottom: 6,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: C.border,
  },
  infoLabel: { color: C.muted, fontWeight: "600" },
  infoValue: { color: C.text, fontWeight: "800" },
});
