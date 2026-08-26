import React from "react";
import { Text, StyleSheet, Alert } from "react-native";
import { router } from "expo-router";
import {
  Screen,
  TopBar,
  Card,
  PersonAvatar,
  MenuRow,
} from "../../../components/parent/ui";
import { TEACHER, CLASSES, TEACHER_UPDATES } from "../../../data/teacherMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function TeacherProfileScreen() {
  const unread = TEACHER_UPDATES.filter((u) => u.unread).length;

  return (
    <Screen>
      <TopBar
        title="Profile"
        subtitle="Teacher account and settings"
        unread={unread}
        bellHref="/teacher/updates"
      />

      <Card style={styles.hero}>
        <PersonAvatar initials="HB" color={C.accent} size={64} />
        <Text style={styles.name}>{TEACHER.name}</Text>
        <Text style={styles.meta}>{TEACHER.title}</Text>
        <Text style={styles.meta}>
          {TEACHER.subject} · {CLASSES.length} classes
        </Text>
      </Card>

      <Card style={{ marginTop: 16 }}>
        <MenuRow
          icon="person-outline"
          title="Teacher Information"
          subtitle="Name, email, and subject"
          onPress={() => router.push("/teacher/profile/info")}
        />
        <MenuRow
          icon="settings-outline"
          title="Settings"
          subtitle="Password and privacy"
          onPress={() => router.push("/teacher/profile/settings")}
        />
        <MenuRow
          icon="globe-outline"
          title="Language"
          subtitle="English"
          onPress={() => router.push("/teacher/profile/language")}
        />
        <MenuRow
          icon="help-circle-outline"
          title="Help & Support"
          subtitle="FAQs and contact"
          onPress={() => router.push("/teacher/profile/help")}
        />
        <MenuRow
          icon="log-out-outline"
          title="Logout"
          subtitle="Return to login"
          danger
          onPress={() =>
            Alert.alert("Logout", "Are you sure you want to log out?", [
              { text: "Cancel", style: "cancel" },
              {
                text: "Logout",
                style: "destructive",
                onPress: () => router.replace("/(auth)/login"),
              },
            ])
          }
        />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { alignItems: "center", paddingVertical: 24 },
  name: { marginTop: 12, fontSize: 20, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted },
});
