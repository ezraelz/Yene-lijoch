import React from "react";
import { Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import {
  Screen,
  TopBar,
  Card,
  PersonAvatar,
  ProgressBar,
} from "../../../../components/parent/ui";
import { STUDENTS, CLASSES } from "../../../../data/teacherMock";
import { ParentColors as C } from "../../../../constants/parentTheme";

export default function StudentDetails() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const student = STUDENTS.find((s) => s.id === id) ?? STUDENTS[0];
  const classItem = CLASSES.find((c) => c.id === student.classId);

  return (
    <Screen>
      <TopBar
        title="Student Details"
        showBell={false}
        onBack={() => router.back()}
      />

      <Card style={styles.hero}>
        <PersonAvatar
          initials={student.initials}
          color={student.color}
          size={72}
        />
        <Text style={styles.name}>{student.name}</Text>
        <Text style={styles.meta}>
          {student.grade} · {classItem?.name ?? "Class"}
        </Text>
        <Text style={styles.meta}>Parent: {student.parent}</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>Progress</Text>
        <ProgressBar value={student.progress} color={C.accent} />
        <Text style={styles.meta}>{student.progress}% overall</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>Attendance</Text>
        <Text style={styles.big}>{student.attendance}%</Text>
        <Text style={styles.meta}>Present this term</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>Teacher notes</Text>
        <Text style={styles.body}>{student.notes}</Text>
      </Card>

      <TouchableOpacity
        style={styles.button}
        onPress={() =>
          Alert.alert("Message parent", `A message draft for ${student.parent} will open here.`)
        }
      >
        <Text style={styles.buttonText}>Message parent</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { alignItems: "center", paddingVertical: 24 },
  name: { marginTop: 12, fontSize: 20, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted },
  section: { fontWeight: "800", color: C.text, marginBottom: 10, fontSize: 16 },
  big: { fontSize: 28, fontWeight: "800", color: C.text },
  body: { color: C.muted, lineHeight: 22 },
  button: {
    marginTop: 20,
    height: 54,
    borderRadius: 16,
    backgroundColor: C.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
