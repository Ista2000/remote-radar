"use client";
import axios from "axios";
import { createContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Box, useToast } from "@chakra-ui/react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { SearchProvider } from "./SearchContext";

export interface UserType {
  id: number;
  email: string;
  full_name: string;
  preferred_roles: Array<string>;
  preferred_locations: Array<string>;
  preferred_sources: Array<string>;
  receive_email_alerts?: boolean;
  experience_years?: number;
  resume_url?: string | null;
};

type AuthContextType = {
  user: UserType | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<UserType | null>(null);
  const router = useRouter();
  const toast = useToast();

  useEffect(() => {
    const setUserIfTokenFound = async () => {
      try {
        const token = localStorage.getItem('token');
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        if (user || !token) {
          return;
        }
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth`,
        );
        setUser({
          ...response.data,
          preferred_roles: JSON.parse(response.data.preferred_roles),
          preferred_locations: JSON.parse(response.data.preferred_locations),
          preferred_sources: JSON.parse(response.data.preferred_sources),
        });
      } catch (e) {
        if (window.location.pathname === "/auth") {
          return;
        }
        router.push("/auth");
        toast({
          position: "top-right",
          title: 'Login required',
          description: "Please login to continue",
          status: 'error',
          duration: 1200,
          isClosable: true,
        });
      }
    }

    setUserIfTokenFound();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const formData = new FormData();
      formData.append('username', email);  // Email is treated as username in the backend
      formData.append('password', password);
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/token`,
        formData,
        {
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        }
      );
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      localStorage.setItem('token', response.data.access_token);
      setUser({
        ...response.data.user,
        preferred_roles: JSON.parse(response.data.user.preferred_roles),
        preferred_locations: JSON.parse(response.data.user.preferred_locations),
        preferred_sources: JSON.parse(response.data.user.preferred_sources),
      });
      router.push('/');
      toast({
        title: 'Login success',
        description: `Welcome, ${response.data.user.full_name}`,
        status: 'success',
        duration: 1200,
        isClosable: true,
        position: "top-right",
      });
    } catch (error) {
      console.log('Login failed:', error);
      throw error;
    }
  }

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    router.push('/auth');
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <SearchProvider>
        <Box minH="100vh" display="flex" flexDirection="column">
          <Header />
          <Box as="main" flex="1" marginTop="118px">
            {children}
          </Box>
          <Footer />
        </Box>
      </SearchProvider>
    </AuthContext.Provider>
  );
};

export default AuthContext;
