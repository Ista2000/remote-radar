"use client"

import { useState } from "react";
import { AuthProvider } from "../context/AuthContext";
import Login from "./Login";
import { Box, Divider, Flex, Text, useRadio, useRadioGroup, UseRadioProps } from "@chakra-ui/react";
import Signup from "./Signup";

interface RadioCardProps extends UseRadioProps {
  children: React.ReactNode
}

const RadioCard = (props: RadioCardProps) => {
  const { getInputProps, getRadioProps } = useRadio(props)

  const input = getInputProps()
  const checkbox = getRadioProps()

  return (
    <Box as='label' width='100%'>
      <input {...input} />
      <Box
        {...checkbox}
        cursor='pointer'
        borderWidth='1px'
        boxShadow='md'
        _checked={{
          bg: 'teal.600',
          color: 'white',
          borderColor: 'teal.600',
        }}
        px={5}
        py={3}
      >
        {props.children}
      </Box>
    </Box>
  )
}

const AuthPage = () => {
  const [selectedPage, setSelectedPage] = useState('login');
  const { getRootProps, getRadioProps } = useRadioGroup({
    name: 'authPage',
    value: selectedPage,
    onChange: s => setSelectedPage(s),
  });

  const group = getRootProps();
  return (
    <AuthProvider>
      <Box maxW="lg" mx="auto" mt={10} p={6} boxShadow="md" borderRadius="md">
        <Flex {...group} gap={1}>
          <RadioCard key="login" {...getRadioProps({value: "login"})}>
            <Text align='center'>Login</Text>
          </RadioCard>
          <RadioCard key="signup" {...getRadioProps({value: "signup"})}>
          <Text align='center'>Signup</Text>
          </RadioCard>
        </Flex>
        <Divider margin="18px 0" />
        {selectedPage === 'login' ? <Login /> : <Signup onSignupSuccess={() => setSelectedPage('login')} />}
      </Box>
    </AuthProvider>
  )
};

export default AuthPage;