"use client";
import { Box, Flex, Text, Button, Spacer, Avatar, HStack, useColorMode, Switch, Icon, Menu, MenuButton, MenuList, MenuItem, Divider, Container, VStack, Link } from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "../hooks/useAuth";
import { ChevronDownIcon, MoonIcon, SunIcon } from "@chakra-ui/icons";

const Header = () => {
  const router = useRouter();
  const { user, logout } = useAuthContext();
  const { colorMode, toggleColorMode } = useColorMode();
  const textColor = colorMode === 'dark' ? 'white' : 'black';

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
              <Icon as={SunIcon} color={'orange.400'} /> :
              <Icon as={MoonIcon} color={'blue.300'} />}
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
          <HStack spacing={4} height="100%">
            <Menu>
              <MenuButton as={Button} variant="ghost" size="sm" leftIcon={<Avatar name={user.full_name} size="sm" />} padding="24px 8px">
                <Icon as={ChevronDownIcon}/>
              </MenuButton>
              <MenuList>
                <HStack padding="12px">
                  <Avatar name={user.full_name} size="sm" />
                  <VStack align="start" spacing={0}>
                    <Text color={textColor}>{user.full_name}</Text>
                    <Link href="/edit" color={textColor} fontSize="xs">Edit profile</Link>
                  </VStack>
                </HStack>
                <Divider height="16px"/>
                <MenuItem color={textColor} onClick={() => router.push(user.email + "/profile")}>Profile</MenuItem>
                <MenuItem color={textColor} onClick={() => router.push(user.email + "/preferences")}>Preferences</MenuItem>
                <MenuItem color={textColor} onClick={logout}>Logout</MenuItem>
              </MenuList>
            </Menu>
          </HStack>
        ) : (
          <HStack spacing={4}>
            <Button variant="ghost" size="sm" onClick={() => router.push("/auth")}>
              <Text>Login</Text>
            </Button>
          </HStack>
        )}
      </Flex>
    </Box>
  );
};

export default Header;
