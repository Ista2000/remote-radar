"use client";
import {
  Box,
  Text,
  Flex,
  Badge,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Stack,
  Button,
  Wrap,
  WrapItem,
  HStack,
  Icon,
  useColorModeValue,
  Tooltip,
  Link,
} from "@chakra-ui/react";
import { AtSignIcon, CalendarIcon, ExternalLinkIcon, InfoOutlineIcon, StarIcon, TimeIcon, ViewIcon } from "@chakra-ui/icons";

export interface JobType {
    company: string;
    description: string;
    id: number,
    is_active: boolean;
    location: string;
    posted_at: string;
    required_experience: number;
    role: string;
    salary_currency: string;
    salary_from_levels_fyi: boolean;
    salary_max: number;
    salary_min: number;
    source: string;
    title: string;
    url: string;
  }

interface JobCardProps {
  job: JobType;
}

const JobCard = ({ job }: JobCardProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgSection = useColorModeValue("gray.50", "gray.700");
  const textColor = useColorModeValue("gray.700", "gray.200");
  const cardBg = useColorModeValue("white", "gray.800");
  const descriptionBg = useColorModeValue("gray.50", "gray.700");
  const descriptionTextColor = useColorModeValue("gray.700", "gray.100");
  return (
    <>
      <Box
        p={4}
        borderWidth="1px"
        borderRadius="2xl"
        boxShadow="md"
        _hover={{ boxShadow: "xl", cursor: "pointer" }}
        transition="0.3s"
        onClick={onOpen}
        margin="24px 0"
      >
        <Flex justify="space-between" mb={2}>
          <Text fontWeight="bold" fontSize="lg">
            {job.title}
          </Text>
          <Badge colorScheme={job.is_active ? "green" : "red"}>
            {job.is_active ? "Active" : "Closed"}
          </Badge>
        </Flex>
        <Text fontSize="md" color="gray.600">
          {job.company} · {job.location}
        </Text>
          <Text fontSize="sm" color="gray.500" mt={1}>
            {job.required_experience}+ yrs · {job.role}
            { job.salary_currency && job.salary_min && job.salary_max && ` · ${job.salary_currency} ${job.salary_min} - ${job.salary_max}` }
          </Text>
        <Text fontSize="2xs" color="gray.500" mt={1}>
          From {job.source}
        </Text>
      </Box>

      <Modal isOpen={isOpen} onClose={onClose} size="5xl" isCentered>
        <ModalOverlay />
        <ModalContent borderRadius="2xl" p={4}>
          <ModalHeader>{job.title} @ {job.company}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={6}>
              {/* Job Overview Section */}
              <Box bg={bgSection} p={4} borderRadius="md" boxShadow="sm">
                <Text fontSize="lg" fontWeight="bold" mb={3} color={textColor}>
                  Job Overview
                </Text>
                <Wrap spacing="12px">
                  <WrapItem>
                    <Box px={4} py={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                      <HStack>
                        <Icon as={InfoOutlineIcon} color="teal.400" />
                        <Text fontWeight="medium" color={textColor}>Role:</Text>
                        <Text color={textColor}>{job.role}</Text>
                      </HStack>
                    </Box>
                  </WrapItem>
                  <WrapItem>
                    <Box px={4} py={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                      <HStack>
                        <Icon as={TimeIcon} color="blue.400" />
                        <Text fontWeight="medium" color={textColor}>Experience:</Text>
                        <Text color={textColor}>{job.required_experience}+ yrs</Text>
                      </HStack>
                    </Box>
                  </WrapItem>
                  <WrapItem>
                    <Box px={4} py={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                      <HStack>
                        <Icon as={CalendarIcon} color="purple.400" />
                        <Text fontWeight="medium" color={textColor}>Posted:</Text>
                        <Text color={textColor}>
                          {new Intl.DateTimeFormat('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          }).format(new Date(job.posted_at))}
                        </Text>
                      </HStack>
                    </Box>
                  </WrapItem>
                  <WrapItem>
                    <Box px={4} py={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                      <HStack>
                        <Icon as={AtSignIcon} color="orange.400" />
                        <Text fontWeight="medium" color={textColor}>Location:</Text>
                        <Text color={textColor}>{job.location}</Text>
                      </HStack>
                    </Box>
                  </WrapItem>
                  {job.salary_currency && job.salary_max && job.salary_min && (
                    <WrapItem>
                      <Box px={4} py={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                        <HStack>
                          <Icon as={StarIcon} color="green.400" />
                          <Text fontWeight="medium" color={textColor}>Salary:</Text>
                          <Text color={textColor}>
                            {job.salary_currency} {job.salary_min} - {job.salary_max}
                          </Text>
                          {job.salary_from_levels_fyi && (
                            <Tooltip label="Salary information sourced from levels.fyi" hasArrow>
                              <Link href="https://www.levels.fyi/" target="_blank"><Badge colorScheme="blue" ml={2}>levels.fyi</Badge></Link>
                            </Tooltip>
                          )}
                        </HStack>
                      </Box>
                    </WrapItem>
                  )}
                  <WrapItem>
                    <Box px={4} py={2} bg={cardBg} borderRadius="md" boxShadow="sm">
                      <HStack>
                        <Icon as={ViewIcon} color="gray.400" />
                        <Text fontWeight="medium" color={textColor}>Source:</Text>
                        <Text color={textColor}>{job.source}</Text>
                      </HStack>
                    </Box>
                  </WrapItem>
                </Wrap>
              </Box>

              {/* Job Description */}
              <Box>
                <Text fontSize="lg" fontWeight="bold" mb={2} color={textColor} paddingLeft={4}>
                  Description
                </Text>
                <Box
                  bg={descriptionBg}
                  padding="24px"
                  borderRadius="md"
                  boxShadow="sm"
                  fontSize="sm"
                  color={descriptionTextColor}
                  maxHeight="400px"
                  overflowY="auto"
                  dangerouslySetInnerHTML={{ __html: job.description }}
                  sx={{
                    // Custom CSS
                    "ul": {
                      listStyleType: "disc",
                      paddingLeft: "1.5rem",
                    },
                    "li": {
                      marginBottom: "0.3rem",
                      color: descriptionTextColor,
                    },
                    "h1": {
                      fontSize: "24px",
                      marginBottom: "0.6rem",
                    },
                    "p": {
                      marginBottom: "0.5rem",
                    }
                  }}
                />
              </Box>

              {/* External Link */}
              <Flex justify="end">
                <Button
                  mt={2}
                  colorScheme="teal"
                  rightIcon={<ExternalLinkIcon />}
                  as="a"
                  href={job.url}
                  target="_blank"
                >
                  View Original Posting
                </Button>
              </Flex>
            </Stack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default JobCard;