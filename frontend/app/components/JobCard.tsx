"use client";
import {
  Box,
  Badge,
  Button,
  Flex,
  HStack,
  Icon,
  Tooltip,
  Link,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Stack,
  Tabs,
  TabList,
  Tab,
  TabPanel,
  TabPanels,
  Skeleton,
  Text,
  Textarea,
  Wrap,
  WrapItem,
  useColorModeValue,
  useDisclosure,
  useToast,
} from "@chakra-ui/react";
import {
  AtSignIcon,
  CalendarIcon,
  ExternalLinkIcon,
  InfoOutlineIcon,
  StarIcon,
  TimeIcon,
  ViewIcon
} from "@chakra-ui/icons";
import { useState } from "react";
import axios from "axios";

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

const currencyToLocale: Record<string, string> = {
  USD: "en-US",
  INR: "en-IN",
  EUR: "de-DE",
  GBP: "en-GB",
  JPY: "ja-JP",
  CNY: "zh-CN",
  CAD: "en-CA",
  AUD: "en-AU",
  SGD: "en-SG",
  // Add more as needed
};

const formatSalary = (amount: number, currency = "USD") => {
  const locale = currencyToLocale[currency] || "en-US"; // fallback
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 0, // Optional: removes decimals
  }).format(amount);
}

const JobCard = ({ job }: JobCardProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgSection = useColorModeValue("gray.50", "gray.700");
  const textColor = useColorModeValue("gray.700", "gray.200");
  const cardBg = useColorModeValue("white", "gray.800");
  const descriptionBg = useColorModeValue("gray.50", "gray.700");
  const descriptionTextColor = useColorModeValue("gray.700", "gray.100");
  const [loading, setLoading] = useState(false);
  const [coverLetter, setCoverLetter] = useState<string | null>(null);
  const toast = useToast();

  console.log(coverLetter);

  const handleGenerateCoverLetter = () => {
    setLoading(true);
    const generateCoverLetter = async () => {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/job/generate-cover?job_url=${encodeURIComponent(job.url)}`);
        setCoverLetter(response.data);
      } catch (e) {
        console.log(e);
        toast({
          position: "top-right",
          title: 'Cannot generate cover letter',
          description: "Cannot generate cover letter",
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    generateCoverLetter();
  }

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
          <Badge colorScheme={job.is_active ? "green" : "red"} h="18px">
            {job.is_active ? "Active" : "Closed"}
          </Badge>
        </Flex>
        <Text fontSize="md" color="gray.600">
          {job.company} · {job.location}
        </Text>
          <Text fontSize="sm" color="gray.500" mt={1}>
            {job.required_experience}+ yrs · {job.role}
            { job.salary_currency && job.salary_min && job.salary_max && ` · ${formatSalary(job.salary_min, job.salary_currency)} - ${formatSalary(job.salary_max, job.salary_currency)}` }
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
                            {formatSalary(job.salary_min, job.salary_currency)} - {formatSalary(job.salary_max, job.salary_currency)}
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
              <Tabs>
                <TabList>
                  <Tab>
                    <Text fontSize="lg" fontWeight="bold" mb={2} color={textColor} paddingLeft={4}>
                      Description
                    </Text>
                  </Tab>
                  <Tab>
                  <Text fontSize="lg" fontWeight="bold" mb={2} color={textColor} paddingLeft={4}>
                      Generate cover letter
                    </Text>
                  </Tab>
                </TabList>
                <TabPanels>
                  <TabPanel>
                    <Box
                      bg={descriptionBg}
                      padding="24px"
                      borderRadius="md"
                      boxShadow="sm"
                      fontSize="sm"
                      color={descriptionTextColor}
                      maxHeight="450px"
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
                  </TabPanel>
                  <TabPanel>
                  <Box
                      bg={descriptionBg}
                      padding="24px"
                      borderRadius="md"
                      boxShadow="sm"
                      fontSize="sm"
                      color={descriptionTextColor}
                      maxHeight="450px"
                      overflowY="auto"
                    >
                      {loading || !coverLetter ? <Skeleton size="lg" height="250px"/> :
                        <Textarea
                          value={coverLetter}
                          onChange={e => setCoverLetter(e.target.value)}
                          placeholder='Cover letter'
                          size='sm'
                          h="250px"
                          maxH="420px"
                        />}
                      <Text fontSize="sm" color="red">NOTE: The cover letter is not saved and it can only be generated until we hit LLM Rate Limits.</Text>
                      <Button
                        size="lg"
                        bgColor="teal"
                        color="white"
                        mt="16px"
                        onClick={handleGenerateCoverLetter}
                      >
                        Generate cover letter
                      </Button>
                    </Box>
                  </TabPanel>
                </TabPanels>
              </Tabs>

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