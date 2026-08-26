import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { CLASSES, TEACHER_UPDATES } from "../../../data/teacherMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function ClassesScreen() {
  const unread = TEACHER_UPDATES.filter((u) => u.unread).length;

  return (
    <Screen>
      <TopBar
        title="Classes"
        subtitle="Your classes and children"
        unread={unread}
        bellHref="/teacher/updates"
      />

      {CLASSES.map((item) => (
        <Card
          key={item.id}
          style={styles.card}
          onPress={() => router.push(`/teacher/classes/${item.id}`)}
        >
          <View style={styles.row}>
            <View style={styles.icon}>
              <Ionicons name="school-outline" size={22} color={C.accent} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>{item.name}</Text>
              <Text style={styles.meta}>
                {item.grade} · {item.subject}
              </Text>
              <Text style={styles.meta}>
                {item.students} students · {item.room}
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={18} color={C.muted} />
          </View>
          <View style={styles.footer}>
            <Text style={styles.present}>
              Present today: {item.presentToday}/{item.students}
            </Text>
            <Text style={styles.next}>{item.nextLesson}</Text>
          </View>
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 12 },
  row: { flexDirection: "row", alignItems: "center", gap: 12 },
  icon: {
    width: 46,
    height: 46,
    borderRadius: 14,
    backgroundColor: C.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  title: { fontSize: 16, fontWeight: "800", color: C.text },
  meta: { marginTop: 3, color: C.muted, fontSize: 13 },
  footer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: C.border,
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 8,
  },
  present: { color: C.success, fontWeight: "700", fontSize: 12 },
  next: { color: C.muted, fontWeight: "600", fontSize: 12 },
});
