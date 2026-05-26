import {
  createContext,
  useCallback,
  useEffect,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import {
  clearLastUsername,
  getLastUsername,
  getToken,
  removeToken,
  setLastUsername,
  setToken,
} from '../services/auth/authStorage';
import {
  changePassword,
  getCurrentUserProfile,
  type UserProfile,
} from '../services/auth/authService';

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  rememberedUsername: string;
  profile: UserProfile | null;
  signIn: (token: string, username: string) => Promise<void>;
  signOut: (keepUsername?: boolean) => void;
  refreshProfile: () => Promise<void>;
  completePasswordChange: (
    currentPassword: string,
    newPassword: string,
  ) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setTokenState] = useState<string | null>(getToken());
  const [rememberedUsername, setRememberedUsername] =
    useState<string>(getLastUsername());
  const [profile, setProfile] = useState<UserProfile | null>(null);

  const refreshProfile = useCallback(async () => {
    if (!getToken()) {
      setProfile(null);
      return;
    }
    const nextProfile = await getCurrentUserProfile();
    setProfile(nextProfile);
  }, []);

  const signIn = useCallback(async (nextToken: string, username: string) => {
    setToken(nextToken);
    setTokenState(nextToken);
    setLastUsername(username);
    setRememberedUsername(username);
    await refreshProfile();
  }, [refreshProfile]);

  const signOut = useCallback((keepUsername = true) => {
    removeToken();
    setTokenState(null);
    setProfile(null);

    if (!keepUsername) {
      clearLastUsername();
      setRememberedUsername('');
    }
  }, []);

  const completePasswordChange = useCallback(async (
    currentPassword: string,
    newPassword: string,
  ) => {
    await changePassword(currentPassword, newPassword);
    await refreshProfile();
  }, [refreshProfile]);

  useEffect(() => {
    if (!token) {
      return;
    }

    refreshProfile().catch(() => {
      removeToken();
      clearLastUsername();
      setTokenState(null);
      setRememberedUsername('');
      setProfile(null);
    });
  }, [token, refreshProfile]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      rememberedUsername,
      profile,
      signIn,
      signOut,
      refreshProfile,
      completePasswordChange,
    }),
    [
      completePasswordChange,
      profile,
      refreshProfile,
      rememberedUsername,
      signIn,
      signOut,
      token,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }

  return context;
};
