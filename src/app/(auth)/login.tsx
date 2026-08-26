import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useAuth } from "@/hooks/useAuth";
import { useRoleNavigation } from "@/hooks/useRoleNavigation";

// Define error response type
interface ErrorResponse {
  response?: {
    status?: number;
    data?: {
      detail?: string;
    };
  };
}

export default function LoginScreen(): React.ReactElement {
  const { navigateBasedOnRole, getDashboardRoute } = useRoleNavigation()
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  const { login } = useAuth();

  const handleLogin = async (): Promise<void> => {
    // Validate input
    if (!username || !password) {
      Alert.alert(
        "Missing Information",
        "Please enter your username and password."
      );
      return;
    }

    // Validate username (at least 3 characters)
    if (username.length < 3) {
      Alert.alert(
        "Invalid Username",
        "Username must be at least 3 characters long."
      );
      return;
    }

    setIsLoading(true);

    try {
      // Use the login function from the auth hook
      await login(username, password, false);
      navigateBasedOnRole(); // Navigate based on role
      getDashboardRoute();
      // The hook will handle navigation automatically
    } catch (error: unknown) {
      // Type guard to check if error has response property
      const err = error as ErrorResponse;
      
      // Error is already handled by the hook with toast
      // Show a fallback alert for any unhandled errors
      if (err.response?.status === 401) {
        Alert.alert(
          "Login Failed",
          "Invalid username or password. Please try again."
        );
      } else if (err.response?.data?.detail) {
        Alert.alert("Login Failed", err.response.data.detail);
      } else {
        Alert.alert(
          "Login Failed",
          "An unexpected error occurred. Please try again."
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>Welcome Back 👋</Text>

        <Text style={styles.subtitle}>
          Login to your Yene Lijoch account
        </Text>

        {/* Username */}
        <Text style={styles.label}>Username</Text>

        <View style={styles.inputWrapper}>
          <Ionicons
            name="person-outline"
            size={20}
            color="#77758A"
            style={styles.inputIcon}
          />

          <TextInput
            style={styles.input}
            placeholder="Enter your username"
            placeholderTextColor="#999"
            autoCapitalize="none"
            autoCorrect={false}
            value={username}
            onChangeText={setUsername}
            editable={!isLoading}
          />
        </View>

        {/* Password */}
        <Text style={styles.label}>Password</Text>

        <View style={styles.inputWrapper}>
          <Ionicons
            name="lock-closed-outline"
            size={20}
            color="#77758A"
            style={styles.inputIcon}
          />

          <TextInput
            style={styles.input}
            placeholder="Enter your password"
            placeholderTextColor="#999"
            secureTextEntry={!showPassword}
            value={password}
            onChangeText={setPassword}
            editable={!isLoading}
          />

          <TouchableOpacity
            onPress={() => setShowPassword(!showPassword)}
            style={styles.eyeButton}
            disabled={isLoading}
          >
            <Ionicons
              name={showPassword ? "eye-off-outline" : "eye-outline"}
              size={21}
              color="#77758A"
            />
          </TouchableOpacity>
        </View>

        {/* Forgot Password */}
        <TouchableOpacity
          style={styles.forgot}
          onPress={() => router.push("/(auth)/forgot-password")}
          disabled={isLoading}
        >
          <Text style={styles.forgotText}>Forgot Password?</Text>
        </TouchableOpacity>

        {/* Login Button */}
        <TouchableOpacity
          style={[styles.button, isLoading && styles.buttonDisabled]}
          onPress={handleLogin}
          activeOpacity={0.8}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <>
              <Text style={styles.buttonText}>Login</Text>
              <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
            </>
          )}
        </TouchableOpacity>

        {/* Signup */}
        <TouchableOpacity
          onPress={() => router.push("/(auth)/signup")}
          disabled={isLoading}
        >
          <Text style={styles.signup}>
            Don't have an account?{" "}
            <Text style={styles.signupBold}>Sign Up</Text>
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

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
    marginBottom: 20,
  },

  inputIcon: {
    marginRight: 10,
  },

  input: {
    flex: 1,
    fontSize: 15,
    color: "#25233A",
  },

  eyeButton: {
    padding: 5,
  },

  forgot: {
    alignItems: "flex-end",
    marginBottom: 25,
  },

  forgotText: {
    color: "#6C63FF",
    fontWeight: "600",
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

  buttonDisabled: {
    opacity: 0.7,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
  },

  signup: {
    textAlign: "center",
    color: "#77758A",
    marginTop: 25,
  },

  signupBold: {
    color: "#6C63FF",
    fontWeight: "700",
  },
});