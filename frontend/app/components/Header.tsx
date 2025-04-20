"use client";
import {
  Box,
  Flex,
  Text,
  Button,
  Avatar,
  HStack,
  useColorMode,
  Switch,
  Icon,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
  VStack,
  Link,
  InputGroup,
  InputLeftElement,
  Input,
  InputRightElement,
  useBreakpointValue,
  IconButton,
  Collapse,
  useDisclosure,
  Stack,
  Spacer
} from "@chakra-ui/react";
import {
  ChevronDownIcon,
  MoonIcon,
  SearchIcon,
  SunIcon,
  HamburgerIcon,
  CloseIcon,
} from "@chakra-ui/icons";
import { useRouter } from "next/navigation";
import { useAuthContext } from "../hooks/useAuth";
import { useSearchContext } from "../context/SearchContext";
import JobSearchBar from "./JobSearchBar";

const Header = () => {
  const router = useRouter();
  const { user, logout } = useAuthContext();
  const { searchTerm, setSearchTerm } = useSearchContext();
  const { colorMode, toggleColorMode } = useColorMode();
  const { isOpen, onToggle } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const textColor = colorMode === "dark" ? "white" : "black";

  return (
    <Box h="100px" as="header" bg="teal.600" color="white" px={6} py={4} boxShadow="md" position="fixed" w="100vw" zIndex={10}>
      <Flex align="center" justify="space-between">
        <Text
          fontSize="xl"
          fontWeight="bold"
          cursor="pointer"
          onClick={() => user ? router.push("/") : router.push("/auth")}
          transition="transform 0.2s ease"
          _hover={{ transform: "scale(1.05)", color: "teal.200" }}
        >
          RemoteRadar
        </Text>
        <Spacer />
        {/* Hamburger for mobile */}
        {isMobile ? (
          <IconButton
            icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
            variant="ghost"
            color="white"
            onClick={onToggle}
            aria-label="Toggle navigation"
          />
        ) : (
          <>
            {user && <JobSearchBar />}
            <Spacer />
            <Flex align="center" gap={2} mr={4}>
              <Icon as={colorMode === "light" ? SunIcon : MoonIcon} color={colorMode === "light" ? "orange.400" : "blue.300"} />
              <Switch
                colorScheme="teal"
                isChecked={colorMode === "dark"}
                onChange={toggleColorMode}
                size="lg"
                aria-label="Toggle dark mode"
              />
            </Flex>

            {user ? (
              <Menu>
                <MenuButton as={Button} variant="ghost" size="lg" leftIcon={<Avatar size="sm" name={user.full_name}/>}>
                  <ChevronDownIcon />
                </MenuButton>
                <MenuList>
                  <HStack padding="12px">
                    <Avatar name={user.full_name} size="sm" />
                    <VStack align="start" spacing={0}>
                      <Text color={textColor}>{user.full_name}</Text>
                      <Link href="/profile/edit" fontSize="xs" color="teal.500">Edit profile</Link>
                    </VStack>
                  </HStack>
                  <Divider />
                  <MenuItem color={textColor} onClick={() => router.push("/profile")}>Profile</MenuItem>
                  <MenuItem color={textColor} onClick={() => router.push("/profile/edit/preferences")}>Preferences</MenuItem>
                  <MenuItem color={textColor} onClick={logout}>Logout</MenuItem>
                </MenuList>
              </Menu>
            ) : (
              <Button variant="ghost" size="sm" onClick={() => router.push("/auth")}>
                Login
              </Button>
            )}
          </>
        )}
      </Flex>

      {/* Mobile dropdown */}
      <Collapse in={isOpen} animateOpacity>
        <Stack mt={4} spacing={4} display={{ md: "none" }}>
          {user && (
            <InputGroup borderRadius="xl">
              <InputLeftElement pointerEvents="none">
                <SearchIcon color="gray.300" />
              </InputLeftElement>
              <Input
                type="text"
                placeholder="Search jobs..."
                bg="gray.700"
                color="white"
                borderRadius="xl"
                onChange={(e) => setSearchTerm(e.target.value)}
                value={searchTerm}
              />
              {searchTerm && (
                <InputRightElement cursor="pointer" onClick={() => setSearchTerm("")}>
                  <Text fontSize="lg" fontWeight="bold" color="gray.400" _hover={{ color: "red.400" }}>
                    ×
                  </Text>
                </InputRightElement>
              )}
            </InputGroup>
          )}

          <Flex align="center" justify="space-between" mt="8px">
            <Text fontSize="lg" mr="8px">
              {colorMode === "light" ? <SunIcon color="orange.400" /> : <MoonIcon color="blue.300" />}
            </Text>
            <Switch
              colorScheme="teal"
              isChecked={colorMode === "dark"}
              onChange={toggleColorMode}
              aria-label="Toggle dark mode"
              size="lg"
            />
            <Spacer />
          </Flex>

          {user ? (
            <>
              <Button borderRadius={0} mt="8px" w="100%" onClick={() => router.push("/profile")}>Profile</Button>
              <Button borderRadius={0} mt="8px" w="100%" onClick={() => router.push("/profile/edit/preferences")}>Preferences</Button>
              <Button borderRadius={0} mt="8px" w="100%" onClick={logout}>Logout</Button>
            </>
          ) : (
            <Button borderRadius={0} mt="8px" w="100%" onClick={() => router.push("/auth")}>Login</Button>
          )}
        </Stack>
      </Collapse>
    </Box>
  );
};

export default Header;
