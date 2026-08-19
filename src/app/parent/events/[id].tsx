import React from "react";
import { Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { EVENTS } from "../../../data/parentMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function EventDetails() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const event = EVENTS.find((item) => item.id === id) ?? EVENTS[0];
  const isPast = event.status === "past";
  const isRegistered = event.status === "registered";

  return (
    <Screen>
      <TopBar title="Event Details" showBell={false} onBack={() => router.back()} />

      <Card>
        <Text style={styles.type}>{event.type}</Text>
        <Text style={styles.title}>{event.title}</Text>
        <Text style={styles.meta}>{event.date} · {event.time}</Text>
        <Text style={styles.meta}>{event.location}</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>About</Text>
        <Text style={styles.body}>{event.description}</Text>
      </Card>

      <Card style={{ marginTop: 14 }}>
        <Text style={styles.section}>Status</Text>
        <Text style={styles.body}>
          {isPast
            ? "This event has already taken place."
            : isRegistered
              ? "You are registered. We will send a reminder."
              : "You have not registered yet."}
        </Text>
      </Card>

      {!isPast ? (
        <TouchableOpacity
          style={styles.button}
          onPress={() =>
            Alert.alert(
              isRegistered ? "You're registered" : "Registered",
              isRegistered
                ? "This event is already on your calendar."
                : "This event was added to Registered Events."
            )
          }
        >
          <Text style={styles.buttonText}>
            {isRegistered ? "View Registration" : "Register"}
          </Text>
        </TouchableOpacity>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  type: { color: C.accent, fontWeight: "800", textTransform: "capitalize", marginBottom: 8 },
  title: { fontSize: 22, fontWeight: "800", color: C.text },
  meta: { marginTop: 6, color: C.muted },
  section: { fontWeight: "800", color: C.text, marginBottom: 8, fontSize: 16 },
  body: { color: C.muted, lineHeight: 22 },
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
