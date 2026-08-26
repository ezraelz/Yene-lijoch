import React from "react";
import { Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { TEACHER_EVENTS } from "../../../data/teacherMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function TeacherEventDetails() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const event = TEACHER_EVENTS.find((item) => item.id === id) ?? TEACHER_EVENTS[0];

  return (
    <Screen>
      <TopBar title="Event Details" showBell={false} onBack={() => router.back()} />

      <Card>
        <Text style={styles.kicker}>Upcoming</Text>
        <Text style={styles.title}>{event.title}</Text>
        <Text style={styles.meta}>
          {event.date} · {event.time}
        </Text>
        <Text style={styles.meta}>{event.location}</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>About</Text>
        <Text style={styles.body}>{event.description}</Text>
      </Card>

      <TouchableOpacity
        style={styles.button}
        onPress={() => Alert.alert("Added", "This event was added to your schedule.")}
      >
        <Text style={styles.buttonText}>Add to my day</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  kicker: { color: C.accent, fontWeight: "800", marginBottom: 8 },
  title: { fontSize: 22, fontWeight: "800", color: C.text },
  meta: { marginTop: 6, color: C.muted },
  section: { fontWeight: "800", color: C.text, marginBottom: 8, fontSize: 16 },
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
