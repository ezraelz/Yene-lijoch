import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { Screen, TopBar, Card, Pill } from "../../components/parent/ui";
import { TEACHER_UPDATES, TeacherUpdate } from "../../data/teacherMock";
import { ParentColors as C } from "../../constants/parentTheme";

const FILTERS = ["Notifications", "Announcements", "Messages"] as const;

export default function UpdatesScreen() {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("Notifications");
  const unread = TEACHER_UPDATES.filter((u) => u.unread).length;

  const items = useMemo(() => {
    const key = filter.toLowerCase() as TeacherUpdate["type"];
    return TEACHER_UPDATES.filter((item) => item.type === key);
  }, [filter]);

  return (
    <Screen>
      <TopBar
        title="Updates"
        subtitle="Notifications, announcements, and messages"
        showBell={false}
        unread={unread}
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
        <Card key={item.id} style={[styles.card, item.unread && styles.unread]}>
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>{item.title}</Text>
              <Text style={styles.body}>{item.body}</Text>
              <Text style={styles.time}>{item.time}</Text>
            </View>
            {item.unread ? <View style={styles.dot} /> : null}
          </View>
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 10 },
  unread: { borderColor: C.accent },
  row: { flexDirection: "row", alignItems: "flex-start", gap: 8 },
  title: { fontWeight: "800", color: C.text, fontSize: 15 },
  body: { marginTop: 4, color: C.muted, lineHeight: 20 },
  time: { marginTop: 8, color: C.muted, fontSize: 12 },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: C.accent,
    marginTop: 6,
  },
});
