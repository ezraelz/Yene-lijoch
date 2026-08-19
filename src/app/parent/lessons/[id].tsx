import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { Screen, TopBar, Card, ProgressBar } from "../../../components/parent/ui";
import { LESSONS } from "../../../data/parentMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function LessonDetails() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const lesson = LESSONS.find((item) => item.id === id) ?? LESSONS[0];

  return (
    <Screen>
      <TopBar
        title="Lesson Details"
        showBell={false}
        onBack={() => router.back()}
      />

      <Card>
        <Text style={styles.kicker}>{lesson.subject} · {lesson.category}</Text>
        <Text style={styles.title}>{lesson.title}</Text>
        <Text style={styles.meta}>
          {lesson.duration} · {lesson.teacher}
        </Text>
        <View style={{ marginTop: 16 }}>
          <ProgressBar value={lesson.progress} />
        </View>
        <Text style={styles.progress}>{lesson.progress}% complete</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>About this lesson</Text>
        <Text style={styles.body}>{lesson.description}</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>What your child will do</Text>
        <Text style={styles.body}>1. Watch a short guided video</Text>
        <Text style={styles.body}>2. Complete a practice activity</Text>
        <Text style={styles.body}>3. Take a 4-question check</Text>
      </Card>

      <TouchableOpacity
        style={styles.button}
        onPress={() =>
          Alert.alert(
            "Continue learning",
            "Lesson player will be connected to the learning backend next."
          )
        }
      >
        <Text style={styles.buttonText}>
          {lesson.status === "completed" ? "Review Lesson" : "Continue Learning"}
        </Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  kicker: { color: C.primary, fontWeight: "800", fontSize: 12, marginBottom: 8 },
  title: { fontSize: 22, fontWeight: "800", color: C.text },
  meta: { marginTop: 6, color: C.muted },
  progress: { marginTop: 8, color: C.muted, fontWeight: "600" },
  section: { fontWeight: "800", color: C.text, marginBottom: 8, fontSize: 16 },
  body: { color: C.muted, lineHeight: 22, marginBottom: 4 },
  button: {
    marginTop: 20,
    height: 54,
    borderRadius: 16,
    backgroundColor: C.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
