import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { Screen, TopBar, Card, Pill } from "../../components/parent/ui";
import { NOTIFICATIONS, NotificationItem } from "../../data/parentMock";
import { ParentColors as C } from "../../constants/parentTheme";
import { router } from "expo-router";

const FILTERS = ["All", "Learning", "Teacher", "Events", "Attendance", "System"] as const;

export default function NotificationsScreen() {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("All");

  const items = useMemo(() => {
    if (filter === "All") return NOTIFICATIONS;
    return NOTIFICATIONS.filter(
      (item) => item.category === filter.toLowerCase()
    );
  }, [filter]);

  return (
    <Screen>
      <TopBar
        title="Notifications"
        subtitle="Learning, teachers, and school updates"
        showBell={false}
        onBack={() => router.back()}
      />

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 12 }}>
        {FILTERS.map((item) => (
          <Pill
            key={item}
            label={item}
            active={filter === item}
            onPress={() => setFilter(item)}
          />
        ))}
      </ScrollView>

      {items.map((item) => (
        <Notice key={item.id} item={item} />
      ))}
    </Screen>
  );
}

function Notice({ item }: { item: NotificationItem }) {
  return (
    <Card style={[styles.card, item.unread && styles.unread]}>
      <View style={styles.row}>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>{item.title}</Text>
          <Text style={styles.body}>{item.body}</Text>
          <Text style={styles.time}>{item.time} · {item.category}</Text>
        </View>
        {item.unread ? <View style={styles.dot} /> : null}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 10 },
  unread: { borderColor: C.primary },
  row: { flexDirection: "row", alignItems: "flex-start", gap: 8 },
  title: { fontWeight: "800", color: C.text, fontSize: 15 },
  body: { marginTop: 4, color: C.muted, lineHeight: 20 },
  time: { marginTop: 8, color: C.muted, fontSize: 12, textTransform: "capitalize" },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: C.primary,
    marginTop: 6,
  },
});
