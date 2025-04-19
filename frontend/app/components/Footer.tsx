"use client";

import { Box, Text, Link, Flex, useColorModeValue } from "@chakra-ui/react";

const Footer = () => {
  const bg = useColorModeValue("gray.100", "gray.700");
  const textColor = useColorModeValue("gray.600", "gray.300");
  const subTextColor = useColorModeValue("gray.500", "gray.400");
  const linkColor = useColorModeValue("teal.600", "teal.300");

  return (
    <Box as="footer" bg={bg} py={4} mt={10}>
      <Flex justify="center" align="center" direction="column" gap={2}>
        <Text fontSize="sm" color={textColor}>
          © {new Date().getFullYear()} RemoteRadar. Made with ❤️ to help devs discover better remote jobs.
        </Text>
        <Text fontSize="xs" color={subTextColor}>
          Open source on{" "}
          <Link href="https://github.com/Ista2000/remote-radar" isExternal color={linkColor}>
            GitHub
          </Link>
          . Contributions are welcome!
        </Text>
      </Flex>
    </Box>
  );
};

export default Footer;