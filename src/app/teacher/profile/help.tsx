import React from "react";
import { Text, StyleSheet, Linking, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { ParentColors as C } from "../../../constants/parentTheme";

const FAQS = [
  {
    q: "How do I take attendance?",
    a: "Open Classes, choose a class, then use the Attendance tab.",
  },
  {
    q: "Where is my lesson schedule?",
    a: "Use the Schedule tab for today's lessons and upcoming events.",
  },
  {
    q: "How do I message a parent?",
    a: "Open a student profile from Class Details, then tap Message parent.",
  },
];

export default function TeacherHelpScreen() {
  return (
    <Screen>
      <TopBar title="Help & Support" showBell={false} onBack={() => router.back()} />
      {FAQS.map((item) => (
        <Card key={item.q} style={{ marginBottom: 12 }}>
          <Text style={styles.q}>{item.q}</Text>
          <Text style={styles.a}>{item.a}</Text>
        </Card>
      ))}
      <TouchableOpacity
        style={styles.button}
        onPress={() => Linking.openURL("mailto:support@yenelijoch.com")}
      >
        <Text style={styles.buttonText}>Contact support</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  q: { fontWeight: "800", color: C.text, marginBottom: 6 },
  a: { color: C.muted, lineHeight: 20 },
  button: {
    marginTop: 8,
    height: 54,
    borderRadius: 16,
    backgroundColor: C.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
