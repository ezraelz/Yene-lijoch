import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card, Avatar } from "../../../components/parent/ui";
import { useSelectedChild } from "../../../contexts/SelectedChildContext";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function MyChildrenScreen() {
  const { childrenList, selectedId, setSelectedId } = useSelectedChild();

  return (
    <Screen>
      <TopBar title="My Children" showBell={false} onBack={() => router.back()} />

      {childrenList.map((child) => {
        const active = child.id === selectedId;
        return (
          <Card
            key={child.id}
            style={[styles.card, active && styles.active]}
            onPress={() => setSelectedId(child.id)}
          >
            <View style={styles.row}>
              <Avatar child={child} size={52} />
              <View style={{ flex: 1 }}>
                <Text style={styles.name}>{child.name}</Text>
                <Text style={styles.meta}>
                  {child.grade} · Age {child.age}
                </Text>
                <Text style={styles.meta}>{child.school}</Text>
              </View>
            </View>
          </Card>
        );
      })}

      <TouchableOpacity
        style={styles.button}
        onPress={() =>
          Alert.alert("Add child", "Child linking will be connected to the backend next.")
        }
      >
        <Text style={styles.buttonText}>Add child</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 12 },
  active: { borderColor: C.primary },
  row: { flexDirection: "row", gap: 12, alignItems: "center" },
  name: { fontWeight: "800", fontSize: 16, color: C.text },
  meta: { marginTop: 3, color: C.muted, fontSize: 13 },
  button: {
    marginTop: 8,
    height: 54,
    borderRadius: 16,
    backgroundColor: C.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
