"use client";
import axios from "axios";
import { createContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { UserType, AuthContextType } from "../types/AuthContextType";
import { useToast } from "@chakra-ui/react";

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<UserType | null>(null);
  const router = useRouter();
  const toast = useToast();

  useEffect(() => {
    const setUserIfTokenFound = async () => {
      try {
        const token = localStorage.getItem('token');
        if (user || !token) {
          return;
        }
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth`,
        );
        setUser(response.data);
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
          duration: 5000,
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
      setUser(response.data.user);
      router.push('/');
      toast({
        title: 'Login success',
        description: `Welcome, ${response.data.user.full_name}`,
        status: 'success',
        duration: 5,
      });
    } catch (error) {
      console.log('Login failed:', error);
      throw error;
    }
  }

  const logout = () => {
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
    router.push('/login');
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
