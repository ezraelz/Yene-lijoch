import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  const goToLogin = () => {
    router.replace("/(auth)/login");
  };

  const goToResetPassword = () => {
    router.push("/(auth)/reset-password");
  };

  const handleSendReset = () => {
    const trimmed = email.trim();

    if (!trimmed) {
      Alert.alert("Missing email", "Please enter the email for your account.");
      return;
    }

    const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed);
    if (!isValidEmail) {
      Alert.alert("Invalid email", "Please enter a valid email address.");
      return;
    }

    // Backend reset email will be connected here later
    setSent(true);
    Alert.alert(
      "Reset link sent",
      "Continue to set a new password for your account.",
      [
        { text: "Back to Login", style: "cancel", onPress: goToLogin },
        { text: "Reset Password", onPress: goToResetPassword },
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={styles.content}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={goToLogin}
            accessibilityRole="button"
            accessibilityLabel="Back to login"
          >
            <Ionicons name="arrow-back" size={24} color="#25233A" />
          </TouchableOpacity>

          <Text style={styles.title}>Forgot Password?</Text>
          <Text style={styles.subtitle}>
            Enter the email linked to your Yene Lijoch account and we will send
            you a reset link.
          </Text>

          <Text style={styles.label}>Email</Text>
          <View style={styles.inputWrapper}>
            <Ionicons
              name="mail-outline"
              size={20}
              color="#77758A"
              style={styles.inputIcon}
            />
            <TextInput
              style={styles.input}
              placeholder="Enter your email"
              placeholderTextColor="#999"
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              value={email}
              onChangeText={setEmail}
              editable={!sent}
            />
          </View>

          <TouchableOpacity
            style={styles.button}
            onPress={handleSendReset}
            activeOpacity={0.8}
          >
            <Text style={styles.buttonText}>Send Reset Link</Text>
            <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
          </TouchableOpacity>

          <TouchableOpacity onPress={goToResetPassword}>
            <Text style={styles.loginLink}>
              Already have a reset link?{" "}
              <Text style={styles.loginBold}>Reset Password</Text>
            </Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={goToLogin}>
            <Text style={styles.loginLink}>
              Remember your password?{" "}
              <Text style={styles.loginBold}>Login</Text>
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
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
    paddingHorizontal: 30,
  },
  backButton: {
    position: "absolute",
    top: 12,
    left: 0,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 5,
    elevation: 2,
  },
  title: {
    fontSize: 30,
    fontWeight: "800",
    color: "#25233A",
  },
  subtitle: {
    fontSize: 15,
    color: "#77758A",
    marginTop: 8,
    marginBottom: 35,
    lineHeight: 22,
  },
  label: {
    fontSize: 14,
    fontWeight: "700",
    color: "#25233A",
    marginBottom: 8,
  },
  inputWrapper: {
    height: 55,
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E8E5EF",
    borderRadius: 16,
    paddingHorizontal: 15,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 25,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontSize: 15,
    color: "#25233A",
  },
  button: {
    height: 56,
    borderRadius: 18,
    backgroundColor: "#6C63FF",
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "row",
    gap: 10,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
  },
  loginLink: {
    textAlign: "center",
    color: "#77758A",
    marginTop: 25,
  },
  loginBold: {
    color: "#6C63FF",
    fontWeight: "700",
  },
});
