import React from "react";
import { Text, StyleSheet, Linking, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { ParentColors as C } from "../../../constants/parentTheme";

const FAQS = [
  {
    q: "How do I switch between children?",
    a: "Use the child selector on Home, or open My Children in Profile.",
  },
  {
    q: "Where can I see today's lesson?",
    a: "Home shows Today's Lesson. Open Lessons for the full list.",
  },
  {
    q: "How do I register for an event?",
    a: "Open Events, tap an event, then tap Register.",
  },
];

export default function HelpScreen() {
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
    backgroundColor: C.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
