"use client";
import { Box, Flex, Text, Button, Spacer, Avatar, HStack, useColorMode, Switch, Icon } from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "../hooks/useAuth";
import { MoonIcon, SunIcon } from "@chakra-ui/icons";

const Header = () => {
  const router = useRouter();
  const { user, logout } = useAuthContext();
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Box as="header" bg="teal.600" color="white" px={6} py={4} boxShadow="sm">
      <Flex align="center">
        <Text fontSize="xl" fontWeight="bold" cursor="pointer" onClick={() => user ? router.push("/") : router.push("/auth")}>
          RemoteRadar
        </Text>
        <Spacer />
        <Flex align="center" gap={2} marginRight="8px">
          <Text fontSize="sm">
            {colorMode === "light" ?
              <>Light <Icon as={SunIcon} color={colorMode === 'light' ? 'orange.400' : 'gray.500'} /></> :
              <>Dark <Icon as={MoonIcon} color={colorMode === 'dark' ? 'blue.300' : 'gray.500'} /></>}
          </Text>
          <HStack spacing={2}>
            <Switch
                colorScheme="teal"
                isChecked={colorMode === 'dark'}
                onChange={toggleColorMode}
                aria-label="Toggle dark mode"
                size="lg"
            />
          </HStack>
        </Flex>
        {user ? (
          <HStack spacing={4}>
            <Avatar name={user.full_name} size="sm" />
            <Text display={{ base: "none", md: "block" }}>{user.full_name}</Text>
            <Button variant="outline" size="sm" onClick={logout}>
              Logout
            </Button>
          </HStack>
        ) : (
          <HStack spacing={4}>
            <Button variant="ghost" size="sm" onClick={() => router.push("/auth")}>
              Login
            </Button>
          </HStack>
        )}
      </Flex>
    </Box>
  );
};

export default Header;