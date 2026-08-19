import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen, TopBar, Card, SectionHeader, Avatar, ProgressBar } from "../../components/parent/ui";
import { useSelectedChild } from "../../contexts/SelectedChildContext";
import { PARENT, LESSONS, EVENTS, ACTIVITIES, NOTIFICATIONS } from "../../data/parentMock";
import { ParentColors as C } from "../../constants/parentTheme";

export default function ParentHome() {
  const { childrenList, selectedChild, selectedId, setSelectedId } = useSelectedChild();
  const todayLesson = LESSONS.find((l) => l.status === "continue") ?? LESSONS[0];
  const upcoming = EVENTS.find((e) => e.status !== "past") ?? EVENTS[0];
  const unread = NOTIFICATIONS.filter((n) => n.unread).length;

  return (
    <Screen>
      <TopBar
        title={`Hi, ${PARENT.name.split(" ")[0]} 👋`}
        subtitle="Here's how your child is doing today"
        unread={unread}
      />

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.childRow}
      >
        {childrenList.map((child) => {
          const active = child.id === selectedId;
          return (
            <TouchableOpacity
              key={child.id}
              style={[styles.childChip, active && styles.childChipActive]}
              onPress={() => setSelectedId(child.id)}
            >
              <Avatar child={child} size={36} />
              <View>
                <Text style={[styles.childName, active && { color: "#fff" }]}>
                  {child.name.split(" ")[0]}
                </Text>
                <Text style={[styles.childGrade, active && { color: "#E8E4FF" }]}>
                  {child.grade}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <Card style={styles.summary}>
        <View style={styles.summaryTop}>
          <Avatar child={selectedChild} size={56} />
          <View style={{ flex: 1 }}>
            <Text style={styles.summaryName}>{selectedChild.name}</Text>
            <Text style={styles.summaryMeta}>
              {selectedChild.grade} · {selectedChild.school}
            </Text>
          </View>
        </View>
        <View style={styles.statRow}>
          <Stat label="Progress" value={`${selectedChild.overallProgress}%`} />
          <Stat label="Attendance" value={`${selectedChild.attendance}%`} />
          <Stat label="Streak" value={`${selectedChild.streak} days`} />
        </View>
      </Card>

      <SectionHeader
        title="Today's Lesson"
        action="See all"
        onPress={() => router.push("/parent/lessons")}
      />
      <Card onPress={() => router.push(`/parent/lessons/${todayLesson.id}`)}>
        <Text style={styles.kicker}>{todayLesson.subject}</Text>
        <Text style={styles.cardTitle}>{todayLesson.title}</Text>
        <Text style={styles.cardMeta}>
          {todayLesson.duration} · {todayLesson.teacher}
        </Text>
        <View style={{ marginTop: 12 }}>
          <ProgressBar value={todayLesson.progress} />
        </View>
        <Text style={styles.progressLabel}>{todayLesson.progress}% complete</Text>
      </Card>

      <SectionHeader
        title="Upcoming Event"
        action="Calendar"
        onPress={() => router.push("/parent/events")}
      />
      <Card onPress={() => router.push(`/parent/events/${upcoming.id}`)}>
        <View style={styles.eventRow}>
          <View style={styles.eventIcon}>
            <Ionicons name="calendar" size={22} color={C.accent} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>{upcoming.title}</Text>
            <Text style={styles.cardMeta}>
              {upcoming.date} · {upcoming.time}
            </Text>
            <Text style={styles.cardMeta}>{upcoming.location}</Text>
          </View>
        </View>
      </Card>

      <SectionHeader
        title="Progress Overview"
        action="Details"
        onPress={() => router.push("/parent/progress")}
      />
      <View style={styles.overviewRow}>
        <Card style={styles.overviewCard}>
          <Text style={styles.overviewValue}>{selectedChild.overallProgress}%</Text>
          <Text style={styles.overviewLabel}>Overall</Text>
        </Card>
        <Card style={styles.overviewCard}>
          <Text style={styles.overviewValue}>{selectedChild.attendance}%</Text>
          <Text style={styles.overviewLabel}>Attendance</Text>
        </Card>
      </View>

      <SectionHeader title="Recent Activity" />
      <Card>
        {ACTIVITIES.map((item, index) => (
          <View
            key={item.id}
            style={[
              styles.activityRow,
              index < ACTIVITIES.length - 1 && styles.activityBorder,
            ]}
          >
            <View style={styles.activityIcon}>
              <Ionicons name={item.icon} size={18} color={C.primary} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.activityTitle}>{item.title}</Text>
              <Text style={styles.cardMeta}>{item.time}</Text>
            </View>
          </View>
        ))}
      </Card>

      <SectionHeader title="Quick Actions" />
      <View style={styles.actions}>
        <Action
          icon="book-outline"
          label="Lessons"
          onPress={() => router.push("/parent/lessons")}
        />
        <Action
          icon="stats-chart-outline"
          label="Progress"
          onPress={() => router.push("/parent/progress")}
        />
        <Action
          icon="calendar-outline"
          label="Events"
          onPress={() => router.push("/parent/events")}
        />
        <Action
          icon="chatbubble-ellipses-outline"
          label="Teacher"
          onPress={() => router.push("/parent/notifications")}
        />
      </View>
    </Screen>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function Action({
  icon,
  label,
  onPress,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.action} onPress={onPress}>
      <View style={styles.actionIcon}>
        <Ionicons name={icon} size={20} color={C.primary} />
      </View>
      <Text style={styles.actionLabel}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  childRow: { gap: 10, paddingBottom: 4 },
  childChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: C.card,
    borderWidth: 1,
    borderColor: C.border,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 18,
  },
  childChipActive: {
    backgroundColor: C.primary,
    borderColor: C.primary,
  },
  childName: { fontWeight: "800", color: C.text, fontSize: 13 },
  childGrade: { color: C.muted, fontSize: 11, marginTop: 1 },
  summary: { marginTop: 16 },
  summaryTop: { flexDirection: "row", alignItems: "center", gap: 12 },
  summaryName: { fontSize: 18, fontWeight: "800", color: C.text },
  summaryMeta: { marginTop: 4, color: C.muted, fontSize: 13 },
  statRow: { flexDirection: "row", marginTop: 16, gap: 8 },
  stat: {
    flex: 1,
    backgroundColor: C.primarySoft,
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: "center",
  },
  statValue: { fontWeight: "800", color: C.text, fontSize: 15 },
  statLabel: { marginTop: 4, color: C.muted, fontSize: 11, fontWeight: "600" },
  kicker: { color: C.primary, fontWeight: "800", fontSize: 12, marginBottom: 6 },
  cardTitle: { fontSize: 16, fontWeight: "800", color: C.text },
  cardMeta: { marginTop: 4, color: C.muted, fontSize: 13 },
  progressLabel: { marginTop: 8, color: C.muted, fontSize: 12, fontWeight: "600" },
  eventRow: { flexDirection: "row", gap: 12, alignItems: "center" },
  eventIcon: {
    width: 46,
    height: 46,
    borderRadius: 14,
    backgroundColor: C.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  overviewRow: { flexDirection: "row", gap: 10 },
  overviewCard: { flex: 1, alignItems: "center" },
  overviewValue: { fontSize: 26, fontWeight: "800", color: C.primary },
  overviewLabel: { marginTop: 4, color: C.muted, fontWeight: "600" },
  activityRow: { flexDirection: "row", alignItems: "center", gap: 12, paddingVertical: 10 },
  activityBorder: { borderBottomWidth: 1, borderBottomColor: C.border },
  activityIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: C.primarySoft,
    alignItems: "center",
    justifyContent: "center",
  },
  activityTitle: { fontWeight: "700", color: C.text },
  actions: { flexDirection: "row", gap: 10 },
  action: { flex: 1, alignItems: "center" },
  actionIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: C.card,
    borderWidth: 1,
    borderColor: C.border,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  actionLabel: { fontSize: 12, fontWeight: "700", color: C.text },
});
