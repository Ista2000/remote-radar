"use client";

import {
  Box,
  Heading,
  Text,
  Badge,
  Stack,
  Flex,
  Link,
  Avatar,
  useColorModeValue,
} from "@chakra-ui/react";
import { ExternalLinkIcon } from "@chakra-ui/icons";
import { useAuthContext } from "../hooks/useAuth";
import { AuthProvider } from "../context/AuthContext";

const UserProfile = () => {
  const { user } = useAuthContext();

  const bg = useColorModeValue("white", "gray.800");
  const textSecondary = useColorModeValue("gray.600", "gray.400");
  const border = useColorModeValue("gray.200", "gray.700");

  if (!user) return null;

  const renderBadgeList = (items: Array<string>, colorScheme: string) => {
    return items
      .filter((x) => x.trim())
      .map((item) => (
        <Badge
          key={item.trim()}
          colorScheme={colorScheme}
          px={2}
          py={1}
          borderRadius="md"
        >
          {item.trim()}
        </Badge>
      ));
  };

  return (
    <Flex
      maxW="6xl"
      mx="auto"
      mt={10}
      p={8}
      borderWidth={1}
      borderRadius="2xl"
      boxShadow="lg"
      bg={bg}
      borderColor={border}
      gap={8}
      direction={{ base: "column", md: "row" }}
    >
      {/* Left pane - user details */}
      <Box flex={1}>
        <Flex direction="column" align="center" mb={6}>
          <Avatar size="2xl" name={user.full_name} mb={4} />
          <Heading size="lg" textAlign="center">
            {user.full_name}
          </Heading>
          <Text fontSize="md" color={textSecondary}>
            {user.email}
          </Text>
        </Flex>

        <Stack spacing={4}>
          <Box>
            <Text fontWeight="semibold">Experience</Text>
            <Text color={textSecondary}>{user.experience_years ?? "N/A"} years</Text>
          </Box>

          <Box>
            <Text fontWeight="semibold" mb={1}>Preferred Roles</Text>
            <Flex gap={2} wrap="wrap">
              {renderBadgeList(user.preferred_roles, "blue")}
            </Flex>
          </Box>

          <Box>
            <Text fontWeight="semibold" mb={1}>Preferred Locations</Text>
            <Flex gap={2} wrap="wrap">
              {renderBadgeList(user.preferred_locations, "purple")}
            </Flex>
          </Box>

          <Box>
            <Text fontWeight="semibold" mb={1}>Preferred Sources</Text>
            <Flex gap={2} wrap="wrap">
              {renderBadgeList(user.preferred_sources, "green")}
            </Flex>
          </Box>

          <Box>
            <Text fontWeight="semibold">Email Alerts</Text>
            <Badge colorScheme={user.receive_email_alerts ? "green" : "red"}>
              {user.receive_email_alerts ? "Enabled" : "Disabled"}
            </Badge>
          </Box>
        </Stack>
      </Box>

      {/* Right pane - resume */}
      {user.resume_url && (
        <Box flex={1}>
          <Text fontWeight="semibold" mb={2} textAlign="center">
            Resume:
          </Text>
          <Box
            h="800px"
            border={`1px solid ${border}`}
            borderRadius="md"
            overflow="hidden"
          >
            <iframe
              src={`${process.env.NEXT_PUBLIC_BACKEND_URL}/${user.resume_url}`}
              width="100%"
              height="100%"
              title="Resume PDF"
            />
          </Box>
          <Flex justify="center">
            <Link
              href={`${process.env.NEXT_PUBLIC_BACKEND_URL}/${user.resume_url}`}
              isExternal
              color="teal.400"
              mt={2}
              display="inline-block"
            >
              View in new tab <ExternalLinkIcon mx="2px" />
            </Link>
          </Flex>
        </Box>
      )}
    </Flex>
  );
};

const UserProfilePage = () => (
  <AuthProvider>
    <UserProfile />
  </AuthProvider>
);

export default UserProfilePage;
