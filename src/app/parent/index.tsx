import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function ParentHome() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Parent Dashboard
      </Text>

      <Text style={styles.subtitle}>
        Welcome to Yene Lijoch 👋
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFF9F1",
    justifyContent: "center",
    alignItems: "center",
  },

  title: {
    fontSize: 28,
    fontWeight: "800",
    color: "#25233A",
  },

  subtitle: {
    marginTop: 10,
    color: "#77758A",
  },
});