"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { 
  getAccessToken, 
  getRefreshToken, 
  setTokens, 
  clearTokens,
  isTokenValid,
  isTokenExpired,
  decodeToken,
  api
} from "../services/api";
import { toast } from "sonner";
import { AuthContext, AuthState, User } from "../types/authTypes";
import { useRouter } from "expo-router";

export function useAuth(): AuthContext {
  const router = useRouter();
  
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    accessToken: null,
    refreshToken: null,
  });

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const accessToken = getAccessToken();
      const refreshToken = getRefreshToken();

      if (!accessToken && !refreshToken) {
        setState(prev => ({ ...prev, isLoading: false, isAuthenticated: false }));
        return;
      }

      if (accessToken && isTokenValid(accessToken)) {
        try {
          const user = await fetchCurrentUser();
          if (user) {
            setState({
              user,
              isLoading: false,
              isAuthenticated: true,
              accessToken,
              refreshToken,
            });
            return;
          }
        } catch (error) {
          console.error("Failed to fetch user:", error);
        }
      }

      // If token is expired, try to refresh
      if (refreshToken) {
        try {
          await refreshSession();
        } catch (error) {
          clearTokens();
          setState({
            user: null,
            isLoading: false,
            isAuthenticated: false,
            accessToken: null,
            refreshToken: null,
          });
        }
      } else {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };

    checkAuth();
  }, []);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!state.isAuthenticated || !state.accessToken) return;

    const token = decodeToken(state.accessToken);
    if (!token) return;

    const expiresIn = token.exp * 1000 - Date.now();
    const refreshThreshold = 5 * 60 * 1000; // Refresh 5 minutes before expiry

    if (expiresIn < refreshThreshold) {
      // Token is about to expire, refresh it
      refreshSession();
    }

    // Set interval to check token expiry
    const interval = setInterval(() => {
      if (isTokenExpired(state.accessToken!)) {
        refreshSession();
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [state.isAuthenticated, state.accessToken]);

  // Fetch current user from API
  const fetchCurrentUser = useCallback(async (): Promise<User | null> => {
    try {
      const response = await api.get("/user/");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch user:", error);
      return null;
    }
  }, []);

  // Login function
  const login = useCallback(
    async (username: string, password: string, rememberMe: boolean = false) => {
      try {
        const response = await api.post("/login/", {
          username,
          password,
        });

        const { access, refresh } = response.data;

        // Store tokens
        setTokens(access, refresh);

        // Fetch user data
        const user = await fetchCurrentUser();
        if (!user) {
          throw new Error("Failed to fetch user data");
        }

        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
          accessToken: access,
          refreshToken: refresh,
        });

        toast.success("Login successful!");
        
        // Redirect to chat
        router.push("/");
      } catch (error: any) {
        console.error("Login error:", error);
        // Redirect to login page
        router.push("/login");
        let errorMessage = "Login failed. Please try again.";
        if (error.response?.status === 401) {
          errorMessage = "Invalid username or password.";
        } else if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        }
        
        toast.error(errorMessage);
        throw error;
        
      }
    },
    [router, fetchCurrentUser]
  );

  // Register function
  const register = useCallback(
    async (username: string, email: string, password: string) => {
      try {
        const response = await api.post("/register/", {
          username,
          email,
          password,
        });

        const { access, refresh } = response.data;

        // Store tokens
        setTokens(access, refresh);

        // Fetch user data
        const user = await fetchCurrentUser();
        if (!user) {
          throw new Error("Failed to fetch user data");
        }

        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
          accessToken: access,
          refreshToken: refresh,
        });

        toast.success("Registration successful!");
        
        // Redirect to chat
        router.push("/");
      } catch (error: any) {
        console.error("Registration error:", error);
        // Redirect to signup page
        router.push("/signup");
        let errorMessage = "Registration failed. Please try again.";
        if (error.response?.status === 400) {
          errorMessage = "Username or email already exists.";
        } else if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        }
        
        toast.error(errorMessage);
        throw error;
      }
    },
    [router, fetchCurrentUser]
  );

  // Logout function
  const logout = useCallback(async () => {
    try {
      // Call logout API if needed
      await api.post("/logout/").catch(() => {});
    } catch (error) {
      console.error("Logout API error:", error);
    } finally {
      // Clear tokens and state
      clearTokens();
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        accessToken: null,
        refreshToken: null,
      });
      
      toast.success("Logged out successfully");
      router.push("/login");
    }
  }, [router]);

  // Refresh session
  const refreshSession = useCallback(async () => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error("No refresh token");
      }

      const response = await api.post("/refresh/", {
        refresh: refreshToken,
      });

      const { access } = response.data;
      const currentRefresh = refreshToken;
      
      setTokens(access, currentRefresh);

      // Fetch updated user data
      const user = await fetchCurrentUser();
      
      setState(prev => ({
        ...prev,
        user: user || prev.user,
        accessToken: access,
        isAuthenticated: true,
      }));

      return access;
    } catch (error) {
      console.error("Session refresh failed:", error);
      clearTokens();
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        accessToken: null,
        refreshToken: null,
      });
      router.push("/login");
      throw error;
    }
  }, [router, fetchCurrentUser]);

  // Update user data
  const updateUser = useCallback((user: User) => {
    setState(prev => ({ ...prev, user }));
  }, []);

  // Check if user has specific role
  const hasRole = useCallback(
    (roles: string | string[]) => {
      if (!state.user) return false;
      
      const userRoles = (state.user as any).roles || [];
      const roleList = Array.isArray(roles) ? roles : [roles];
      
      return roleList.some(role => userRoles.includes(role));
    },
    [state.user]
  );

  return {
    user: state.user,
    isLoading: state.isLoading,
    isAuthenticated: state.isAuthenticated,
    accessToken: state.accessToken,
    login,
    logout,
    register,
    refreshSession,
    updateUser,
    hasRole,
  };
}