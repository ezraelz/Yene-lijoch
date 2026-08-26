import React, { useState } from "react";
import { Text, StyleSheet } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { ParentColors as C } from "../../../constants/parentTheme";

const LANGUAGES = ["English", "Amharic", "Afan Oromo", "Tigrinya"];

export default function TeacherLanguageScreen() {
  const [selected, setSelected] = useState("English");

  return (
    <Screen>
      <TopBar title="Language" showBell={false} onBack={() => router.back()} />
      {LANGUAGES.map((lang) => (
        <Card
          key={lang}
          style={[styles.card, selected === lang && styles.active]}
          onPress={() => setSelected(lang)}
        >
          <Text style={styles.title}>{lang}</Text>
          {selected === lang ? <Text style={styles.check}>Selected</Text> : null}
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 10, flexDirection: "row", justifyContent: "space-between" },
  active: { borderColor: C.accent },
  title: { fontWeight: "800", color: C.text },
  check: { color: C.accent, fontWeight: "700" },
});
