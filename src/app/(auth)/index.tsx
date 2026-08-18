import React from "react";
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import { router } from "expo-router";

export default function WelcomeScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>

        <View style={styles.logo}>
          <Text style={styles.logoText}>YL</Text>
        </View>

        <Text style={styles.title}>
          Yene Lijoch
        </Text>

        <Text style={styles.subtitle}>
          Connecting parents and teachers
          {"\n"}
          to help children grow together.
        </Text>

        <View style={styles.illustration}>
          <Text style={styles.emoji}>
            👨‍👩‍👧‍👦
          </Text>

          <Text style={styles.illustrationText}>
            Learn • Connect • Grow
          </Text>
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/(auth)/login")}
        >
          <Text style={styles.buttonText}>
            Get Started
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.push("/(auth)/login")}
        >
          <Text style={styles.loginText}>
            Already have an account?{" "}
            <Text style={styles.loginBold}>
              Login
            </Text>
          </Text>
        </TouchableOpacity>

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFF9F1",
  },

  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 30,
  },

  logo: {
    width: 90,
    height: 90,
    borderRadius: 28,
    backgroundColor: "#6C63FF",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
  },

  logoText: {
    color: "#FFFFFF",
    fontSize: 30,
    fontWeight: "800",
  },

  title: {
    fontSize: 34,
    fontWeight: "800",
    color: "#25233A",
  },

  subtitle: {
    marginTop: 12,
    textAlign: "center",
    fontSize: 16,
    lineHeight: 24,
    color: "#77758A",
  },

  illustration: {
    width: "100%",
    height: 220,
    marginVertical: 35,
    borderRadius: 30,
    backgroundColor: "#F0EDFF",
    alignItems: "center",
    justifyContent: "center",
  },

  emoji: {
    fontSize: 70,
  },

  illustrationText: {
    marginTop: 15,
    fontSize: 17,
    fontWeight: "700",
    color: "#6C63FF",
  },

  button: {
    width: "100%",
    height: 56,
    borderRadius: 18,
    backgroundColor: "#6C63FF",
    alignItems: "center",
    justifyContent: "center",
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
  },

  loginText: {
    marginTop: 22,
    color: "#77758A",
    fontSize: 14,
  },

  loginBold: {
    color: "#6C63FF",
    fontWeight: "700",
  },
});