// hooks/useRoleNavigation.ts
import { useRouter } from "expo-router";
import { useAuth } from "./useAuth";

export const useRoleNavigation = () => {
  const router = useRouter();
  const { user } = useAuth();

  const navigateBasedOnRole = () => {
    const userRole = user?.role_name || '';

    switch (userRole.toLowerCase()) {
      case 'teacher':
        router.replace("/teacher");
        break;
      case 'parent':
        router.replace("/parent");
        break;
      case 'student':
        router.replace("/");
        break;
      case 'pastor':
        router.replace("/");
        break;
      default:
        router.replace("/");
        break;
    }
  };

  const getDashboardRoute = (): string => {
    const userRole = user?.role_name || '';

    switch (userRole.toLowerCase()) {
      case 'teacher':
        return "/teacher";
      case 'parent':
        return "/parent";
      case 'student':
        return "/student";
      case 'pastor':
        return "/pastor";
      default:
        return "/";
    }
  };

  return { navigateBasedOnRole, getDashboardRoute };
};