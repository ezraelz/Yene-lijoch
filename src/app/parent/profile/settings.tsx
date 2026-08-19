import React, { useState } from "react";
import { View, Text, StyleSheet, Switch, Alert, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function AccountSettingsScreen() {
  const [privateProfile, setPrivateProfile] = useState(true);

  return (
    <Screen>
      <TopBar title="Account Settings" showBell={false} onBack={() => router.back()} />
      <Card>
        <View style={styles.row}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Private profile</Text>
            <Text style={styles.sub}>Only teachers and linked family can see details.</Text>
          </View>
          <Switch
            value={privateProfile}
            onValueChange={setPrivateProfile}
            trackColor={{ true: C.primary }}
          />
        </View>
      </Card>

      <TouchableOpacity
        style={styles.button}
        onPress={() => router.push("/(auth)/reset-password")}
      >
        <Text style={styles.buttonText}>Change password</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.ghost}
        onPress={() => Alert.alert("Delete account", "This action will be available after backend setup.")}
      >
        <Text style={styles.ghostText}>Delete account</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "center", gap: 12 },
  title: { fontWeight: "800", color: C.text, fontSize: 15 },
  sub: { marginTop: 4, color: C.muted, fontSize: 13, lineHeight: 18 },
  button: {
    marginTop: 20,
    height: 54,
    borderRadius: 16,
    backgroundColor: C.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
  ghost: { marginTop: 14, alignItems: "center" },
  ghostText: { color: C.danger, fontWeight: "700" },
});
