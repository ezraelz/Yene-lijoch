import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card, Pill, ProgressBar } from "../../../components/parent/ui";
import { CATEGORIES, LESSONS, Lesson, NOTIFICATIONS } from "../../../data/parentMock";
import { useSelectedChild } from "../../../contexts/SelectedChildContext";
import { ParentColors as C } from "../../../constants/parentTheme";

const FILTERS = ["All Lessons", "Continue", "Recommended", "Completed"] as const;

export default function LessonsScreen() {
  const { selectedChild } = useSelectedChild();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("All Lessons");
  const [category, setCategory] = useState("All");
  const unread = NOTIFICATIONS.filter((n) => n.unread).length;

  const lessons = useMemo(() => {
    return LESSONS.filter((lesson) => {
      const byFilter =
        filter === "All Lessons" ||
        (filter === "Continue" && lesson.status === "continue") ||
        (filter === "Recommended" && lesson.status === "recommended") ||
        (filter === "Completed" && lesson.status === "completed");
      const byCategory = category === "All" || lesson.category === category;
      return byFilter && byCategory;
    });
  }, [filter, category]);

  return (
    <Screen>
      <TopBar
        title="Lessons"
        subtitle={`Learning path for ${selectedChild.name.split(" ")[0]}`}
        unread={unread}
      />

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.row}>
        {FILTERS.map((item) => (
          <Pill
            key={item}
            label={item}
            active={filter === item}
            onPress={() => setFilter(item)}
          />
        ))}
      </ScrollView>

      <Text style={styles.catLabel}>Categories</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.row}>
        {CATEGORIES.map((item) => (
          <Pill
            key={item}
            label={item}
            active={category === item}
            onPress={() => setCategory(item)}
          />
        ))}
      </ScrollView>

      {lessons.map((lesson) => (
        <LessonCard key={lesson.id} lesson={lesson} />
      ))}
    </Screen>
  );
}

function LessonCard({ lesson }: { lesson: Lesson }) {
  return (
    <Card
      style={styles.card}
      onPress={() => router.push(`/parent/lessons/${lesson.id}`)}
    >
      <View style={styles.top}>
        <Text style={styles.subject}>{lesson.subject}</Text>
        <Text style={styles.status}>{lesson.status}</Text>
      </View>
      <Text style={styles.title}>{lesson.title}</Text>
      <Text style={styles.meta}>
        {lesson.duration} · {lesson.teacher}
      </Text>
      <View style={{ marginTop: 12 }}>
        <ProgressBar
          value={lesson.progress}
          color={lesson.status === "completed" ? C.success : C.primary}
        />
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  row: { marginBottom: 12 },
  catLabel: {
    fontWeight: "800",
    color: C.text,
    marginBottom: 10,
    marginTop: 6,
  },
  card: { marginBottom: 12 },
  top: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  subject: { color: C.primary, fontWeight: "800", fontSize: 12 },
  status: { color: C.muted, fontWeight: "700", fontSize: 12, textTransform: "capitalize" },
  title: { fontSize: 16, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted, fontSize: 13 },
});
