import React, { useMemo, useState } from "react";
import { Text, StyleSheet, ScrollView } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card, Pill, SectionHeader } from "../../../components/parent/ui";
import { EVENTS, EventItem, NOTIFICATIONS } from "../../../data/parentMock";
import { ParentColors as C } from "../../../constants/parentTheme";

const FILTERS = ["Upcoming", "Registered", "Past"] as const;
const DAYS = [
  { d: "Thu", n: "20" },
  { d: "Fri", n: "21" },
  { d: "Sat", n: "22" },
  { d: "Sun", n: "23" },
  { d: "Mon", n: "24" },
  { d: "Tue", n: "25" },
  { d: "Wed", n: "26" },
];

export default function EventsScreen() {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("Upcoming");
  const [selectedDay, setSelectedDay] = useState("22");
  const unread = NOTIFICATIONS.filter((n) => n.unread).length;

  const events = useMemo(() => {
    return EVENTS.filter((event) => {
      if (filter === "Upcoming") return event.status === "upcoming";
      if (filter === "Registered") return event.status === "registered";
      return event.status === "past";
    });
  }, [filter]);

  return (
    <Screen>
      <TopBar title="Events" subtitle="School and learning calendar" unread={unread} />

      <SectionHeader title="Event Calendar" />
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 8 }}>
        {DAYS.map((day) => {
          const active = selectedDay === day.n;
          return (
            <Card
              key={day.n}
              style={[styles.day, active && styles.dayActive]}
              onPress={() => setSelectedDay(day.n)}
            >
              <Text style={[styles.dayName, active && { color: "#fff" }]}>{day.d}</Text>
              <Text style={[styles.dayNum, active && { color: "#fff" }]}>{day.n}</Text>
            </Card>
          );
        })}
      </ScrollView>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 8 }}>
        {FILTERS.map((item) => (
          <Pill
            key={item}
            label={item === "Upcoming" ? "Upcoming Events" : item === "Registered" ? "Registered Events" : "Past Events"}
            active={filter === item}
            onPress={() => setFilter(item)}
          />
        ))}
      </ScrollView>

      {events.length === 0 ? (
        <Card>
          <Text style={styles.empty}>No events in this list yet.</Text>
        </Card>
      ) : (
        events.map((event) => <EventCard key={event.id} event={event} />)
      )}
    </Screen>
  );
}

function EventCard({ event }: { event: EventItem }) {
  return (
    <Card style={{ marginBottom: 12 }} onPress={() => router.push(`/parent/events/${event.id}`)}>
      <Text style={styles.type}>{event.type}</Text>
      <Text style={styles.title}>{event.title}</Text>
      <Text style={styles.meta}>
        {event.date} · {event.time}
      </Text>
      <Text style={styles.meta}>{event.location}</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  day: { width: 62, alignItems: "center", marginRight: 8, paddingVertical: 12 },
  dayActive: { backgroundColor: C.primary, borderColor: C.primary },
  dayName: { color: C.muted, fontWeight: "700", fontSize: 12 },
  dayNum: { marginTop: 4, fontSize: 18, fontWeight: "800", color: C.text },
  type: { color: C.accent, fontWeight: "800", fontSize: 12, textTransform: "capitalize", marginBottom: 6 },
  title: { fontSize: 16, fontWeight: "800", color: C.text },
  meta: { marginTop: 4, color: C.muted, fontSize: 13 },
  empty: { color: C.muted, textAlign: "center" },
});
