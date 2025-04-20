"use client";
import { Box, Flex, Text, Button, Spacer, Avatar, HStack, useColorMode, Switch, Icon, Menu, MenuButton, MenuList, MenuItem, Divider, Container, VStack, Link, InputGroup, InputLeftElement, Input, InputRightElement } from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "../hooks/useAuth";
import { ChevronDownIcon, MoonIcon, SearchIcon, SunIcon } from "@chakra-ui/icons";
import { useSearchContext } from "../context/SearchContext";

const Header = () => {
  const router = useRouter();
  const { user, logout } = useAuthContext();
  const { searchTerm, setSearchTerm } = useSearchContext();
  const { colorMode, toggleColorMode } = useColorMode();
  const textColor = colorMode === 'dark' ? 'white' : 'black';

  return (
    <Box as="header" bg="teal.600" color="white" px={6} py={4} boxShadow="sm" position="fixed" w="100vw">
      <Flex align="center">
        <Text fontSize="xl" fontWeight="bold" cursor="pointer" onClick={() => user ? router.push("/") : router.push("/auth")}>
          RemoteRadar
        </Text>
        <Spacer />
        {user && (
          <InputGroup
            maxW="400px"
            mr={4}
            transition="all 0.3s ease"
            transform="auto"
            _hover={{
              transform: "scale(1.03)",
              filter: "brightness(1.05)",
            }}
            boxShadow={`0 0 8px ${colorMode === "light" ? "rgba(0, 128, 128, 0.3)" : "rgba(0, 255, 255, 0.4)"}`}
            borderRadius="xl"
          >
            <InputLeftElement pointerEvents="none">
              <SearchIcon
                color={colorMode === "light" ? "gray.500" : "gray.300"}
                transition="color 0.3s ease"
              />
            </InputLeftElement>

            <Input
              type="text"
              placeholder="Search jobs..."
              bg={colorMode === "light" ? "white" : "gray.700"}
              color={colorMode === "light" ? "black" : "white"}
              _placeholder={{ color: colorMode === "light" ? "gray.500" : "gray.400" }}
              borderRadius="xl"
              size="md"
              px={4}
              py={2}
              pr="2.5rem"
              focusBorderColor="teal.400"
              boxShadow={`inset 0 0 4px ${colorMode === "light" ? "teal.200" : "teal.500"}`}
              transition="all 0.3s ease"
              _focus={{
                boxShadow: `0 0 0 2px ${colorMode === "light" ? "teal.300" : "teal.600"}`,
              }}
              onChange={(e) => setSearchTerm(e.target.value)}
              value={searchTerm}
            />

            {searchTerm && (
              <InputRightElement cursor="pointer" onClick={() => setSearchTerm("")}>
                <Text
                  fontSize="lg"
                  fontWeight="bold"
                  color={colorMode === "light" ? "gray.500" : "gray.400"}
                  _hover={{ color: "red.400" }}
                  transition="color 0.2s"
                >
                  ×
                </Text>
              </InputRightElement>
            )}
          </InputGroup>
        )}
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
                    <Link href="/profile/edit" color={textColor} fontSize="xs">Edit profile</Link>
                  </VStack>
                </HStack>
                <Divider height="16px"/>
                <MenuItem color={textColor} onClick={() => router.push("/profile")}>Profile</MenuItem>
                <MenuItem color={textColor} onClick={() => router.push("/profile/edit/preferences")}>Preferences</MenuItem>
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
