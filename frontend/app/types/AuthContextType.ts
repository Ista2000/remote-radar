export type UserType = {
  id: number;
  email: string;
  full_name: string;
  // add more fields as needed
};

export type AuthContextType = {
  user: UserType | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};