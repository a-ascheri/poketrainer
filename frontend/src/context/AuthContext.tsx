import {
  createContext,
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
} from '@services/auth/authStorage';

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  rememberedUsername: string;
  signIn: (token: string, username: string) => void;
  signOut: (keepUsername?: boolean) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setTokenState] = useState<string | null>(getToken());
  const [rememberedUsername, setRememberedUsername] =
    useState<string>(getLastUsername());

  const signIn = (nextToken: string, username: string) => {
    setToken(nextToken);
    setTokenState(nextToken);
    setLastUsername(username);
    setRememberedUsername(username);
  };

  const signOut = (keepUsername = true) => {
    removeToken();
    setTokenState(null);

    if (!keepUsername) {
      clearLastUsername();
      setRememberedUsername('');
    }
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      rememberedUsername,
      signIn,
      signOut,
    }),
    [rememberedUsername, token],
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
