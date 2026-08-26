import React, { useState } from "react";
import { Text, StyleSheet, TextInput, TouchableOpacity, Alert } from "react-native";
import { router } from "expo-router";
import { Screen, TopBar, Card } from "../../../components/parent/ui";
import { TEACHER } from "../../../data/teacherMock";
import { ParentColors as C } from "../../../constants/parentTheme";

export default function TeacherInfoScreen() {
  const [name, setName] = useState(TEACHER.name);
  const [email, setEmail] = useState(TEACHER.email);
  const [phone, setPhone] = useState(TEACHER.phone);
  const [subject, setSubject] = useState(TEACHER.subject);

  return (
    <Screen>
      <TopBar title="Teacher Information" showBell={false} onBack={() => router.back()} />
      <Card>
        <Text style={styles.label}>Full name</Text>
        <TextInput style={styles.input} value={name} onChangeText={setName} />
        <Text style={styles.label}>Email</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />
        <Text style={styles.label}>Phone</Text>
        <TextInput
          style={styles.input}
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
        />
        <Text style={styles.label}>Subject</Text>
        <TextInput style={styles.input} value={subject} onChangeText={setSubject} />
      </Card>
      <TouchableOpacity
        style={styles.button}
        onPress={() => Alert.alert("Saved", "Teacher information was updated.")}
      >
        <Text style={styles.buttonText}>Save changes</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  label: { fontWeight: "700", color: C.text, marginBottom: 8, marginTop: 10 },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: C.border,
    borderRadius: 12,
    paddingHorizontal: 12,
    color: C.text,
    backgroundColor: C.bg,
  },
  button: {
    marginTop: 20,
    height: 54,
    borderRadius: 16,
    backgroundColor: C.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
