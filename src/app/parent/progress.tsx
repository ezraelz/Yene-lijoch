import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Screen, TopBar, Card, SectionHeader, ProgressBar } from "../../components/parent/ui";
import { useSelectedChild } from "../../contexts/SelectedChildContext";
import {
  WEEKLY_ACTIVITY,
  SUBJECT_PROGRESS,
  ACHIEVEMENTS,
  NOTIFICATIONS,
} from "../../data/parentMock";
import { ParentColors as C } from "../../constants/parentTheme";

export default function ProgressScreen() {
  const { selectedChild } = useSelectedChild();
  const unread = NOTIFICATIONS.filter((n) => n.unread).length;
  const max = Math.max(...WEEKLY_ACTIVITY.map((d) => d.value));

  return (
    <Screen>
      <TopBar
        title="Progress"
        subtitle={`${selectedChild.name.split(" ")[0]}'s learning this week`}
        unread={unread}
      />

      <Card>
        <Text style={styles.label}>Overall Progress</Text>
        <Text style={styles.big}>{selectedChild.overallProgress}%</Text>
        <ProgressBar value={selectedChild.overallProgress} />
        <Text style={styles.hint}>Keep going — a little practice each day adds up.</Text>
      </Card>

      <SectionHeader title="Weekly Activity" />
      <Card>
        <View style={styles.week}>
          {WEEKLY_ACTIVITY.map((day) => (
            <View key={day.day} style={styles.weekCol}>
              <View style={styles.barWrap}>
                <View
                  style={[
                    styles.weekBar,
                    { height: `${(day.value / max) * 100}%` },
                  ]}
                />
              </View>
              <Text style={styles.weekDay}>{day.day}</Text>
            </View>
          ))}
        </View>
      </Card>

      <SectionHeader title="Subject Progress" />
      <Card>
        {SUBJECT_PROGRESS.map((subject) => (
          <View key={subject.name} style={styles.subject}>
            <View style={styles.subjectTop}>
              <Text style={styles.subjectName}>{subject.name}</Text>
              <Text style={styles.subjectValue}>{subject.value}%</Text>
            </View>
            <ProgressBar value={subject.value} color={subject.color} />
          </View>
        ))}
      </Card>

      <SectionHeader title="Attendance" />
      <Card>
        <View style={styles.attRow}>
          <View>
            <Text style={styles.big}>{selectedChild.attendance}%</Text>
            <Text style={styles.hint}>Present this term</Text>
          </View>
          <View style={styles.attBadge}>
            <Text style={styles.attBadgeText}>Excellent</Text>
          </View>
        </View>
      </Card>

      <SectionHeader title="Learning Streak" />
      <Card>
        <Text style={styles.big}>{selectedChild.streak} days 🔥</Text>
        <Text style={styles.hint}>Practice again tomorrow to keep the streak alive.</Text>
      </Card>

      <SectionHeader title="Achievements" />
      <View style={styles.achievements}>
        {ACHIEVEMENTS.map((item) => (
          <Card key={item.id} style={styles.badgeCard}>
            <Text style={styles.emoji}>{item.emoji}</Text>
            <Text style={styles.badgeTitle}>{item.title}</Text>
          </Card>
        ))}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  label: { color: C.muted, fontWeight: "700", marginBottom: 6 },
  big: { fontSize: 32, fontWeight: "800", color: C.text, marginBottom: 10 },
  hint: { marginTop: 10, color: C.muted, lineHeight: 20 },
  week: { flexDirection: "row", justifyContent: "space-between", height: 140 },
  weekCol: { alignItems: "center", flex: 1 },
  barWrap: {
    flex: 1,
    width: 14,
    backgroundColor: C.primarySoft,
    borderRadius: 8,
    justifyContent: "flex-end",
    overflow: "hidden",
  },
  weekBar: { width: "100%", backgroundColor: C.primary, borderRadius: 8 },
  weekDay: { marginTop: 8, fontSize: 11, fontWeight: "700", color: C.muted },
  subject: { marginBottom: 14 },
  subjectTop: { flexDirection: "row", justifyContent: "space-between", marginBottom: 8 },
  subjectName: { fontWeight: "800", color: C.text },
  subjectValue: { fontWeight: "700", color: C.muted },
  attRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  attBadge: {
    backgroundColor: C.successSoft,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 12,
  },
  attBadgeText: { color: C.success, fontWeight: "800" },
  achievements: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  badgeCard: { width: "47%", alignItems: "center", paddingVertical: 18 },
  emoji: { fontSize: 28, marginBottom: 8 },
  badgeTitle: { fontWeight: "800", color: C.text, textAlign: "center" },
});
