export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  sex: "M" | "F" | "Other" | null;
  phone: number;
  age: number | null;
  date_of_birth: string | null;
  contact: string | null;
  address: string | null;
  bio: string | null;
  role: string;
  role_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  profile_image: string | null;
  created_at: string;
  last_seen: string | null;
  permissions: string[];
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
