import React from "react";
import { Text, StyleSheet, Alert } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card, Avatar, MenuRow } from "../../../components/parent/ui";
import { PARENT, NOTIFICATIONS } from "../../../data/parentMock";
import { useSelectedChild } from "../../../contexts/SelectedChildContext";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function ProfileScreen() {
  const { selectedChild, childrenList } = useSelectedChild();
  const unread = NOTIFICATIONS.filter((n) => n.unread).length;

  return (
    <Screen>
      <TopBar title="Profile" subtitle="Account and family settings" unread={unread} />

      <Card style={styles.hero}>
        <Avatar child={selectedChild} size={64} />
        <Text style={styles.name}>{PARENT.name}</Text>
        <Text style={styles.meta}>{PARENT.email}</Text>
        <Text style={styles.meta}>{PARENT.role} · {childrenList.length} children</Text>
      </Card>

      <Card style={{ marginTop: 16 }}>
        <MenuRow
          icon="person-outline"
          title="Parent Profile"
          subtitle="Name, email, and phone"
          onPress={() => router.push("/parent/profile/account")}
        />
        <MenuRow
          icon="people-outline"
          title="My Children"
          subtitle="Manage connected children"
          onPress={() => router.push("/parent/profile/children")}
        />
        <MenuRow
          icon="settings-outline"
          title="Account Settings"
          subtitle="Password and privacy"
          onPress={() => router.push("/parent/profile/settings")}
        />
        <MenuRow
          icon="globe-outline"
          title="Language"
          subtitle="English"
          onPress={() => router.push("/parent/profile/language")}
        />
        <MenuRow
          icon="notifications-outline"
          title="Notifications Settings"
          subtitle="Choose what you receive"
          onPress={() => router.push("/parent/profile/notification-settings")}
        />
        <MenuRow
          icon="help-circle-outline"
          title="Help & Support"
          subtitle="FAQs and contact"
          onPress={() => router.push("/parent/profile/help")}
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
