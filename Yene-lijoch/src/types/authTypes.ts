export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  bio: string;
  avatar: string;
  created_at: string;
  location: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
}

export interface AuthContext {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  refreshSession: () => Promise<void>;
  updateUser: (user: User) => void;
  hasRole: (roles: string | string[]) => boolean;
  accessToken: string | null;
}
