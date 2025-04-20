"use client"

import { useState } from "react";
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Spinner,
  FormErrorMessage,
} from "@chakra-ui/react";
import { useAuthContext } from "../hooks/useAuth";
import axios from "axios";

const Login = () => {
  const { user: authUser, login } = useAuthContext();
  const [user, setUser] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(user.email, user.password);
    } catch (e) {
      if (axios.isAxiosError(e)) {
        setError(e.response?.data?.detail || "Login failed");
      } else {
        setError("An unexpected error occured")
      }
    } finally {
      setLoading(false);
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  }

  if (!!authUser) {
    return "ALREADY LOGGED IN";
  }

  return (
    <VStack spacing={4} align="stretch">
      <FormControl>
        <FormLabel htmlFor="email">Email</FormLabel>
        <Input name="email" type="email" onChange={handleChange} />
      </FormControl>

      <FormControl>
        <FormLabel htmlFor="password">Password</FormLabel>
        <Input name="password" type="password" onChange={handleChange} />
      </FormControl>

      <Button colorScheme="teal" onClick={handleSubmit} isDisabled={loading}>
        {loading ? <Spinner size="sm" /> : "Login"}
      </Button>

      <FormControl isInvalid={!!error}>
        <FormErrorMessage>
          {error}
        </FormErrorMessage>
      </FormControl>
    </VStack>
  );
};

export default Login;