"use client"
import { Container, Divider, Flex, HStack, Select, Skeleton, Text, useToast } from "@chakra-ui/react";
import { AuthProvider } from "./context/AuthContext";
import { useEffect, useRef, useState } from "react";
import axios from "axios";
import JobCard, { JobType } from "./components/JobCard";
import { FilterType, useSearchContext } from "./context/SearchContext";
import { useDebounce } from "./hooks/useDebounce";

const filterNotSet = (filter: FilterType): boolean => {
  return !filter.location && !filter.min_experience && !filter.max_experience && !filter.remote && !filter.role && !filter.source;
}


const Home = () => {
  const { searchTerm, filters } = useSearchContext();
  const [jobsWithRole, setJobsWithRole] = useState<Record<string, Array<JobType>> | null>(null);
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>('relevance');
  const [loading, setLoading] = useState<boolean>(true);
  const jobs = jobsWithRole ? jobsWithRole[selectedRole] : null;
  const roles = jobsWithRole ? Object.keys(jobsWithRole) : [];
  const toast = useToast();
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const requestIdRef = useRef(0);

  useEffect(() => {
    setLoading(true);
    const currentIdRef = ++requestIdRef.current;
    const fetchJobs = async () => {
      try {
        let searchQuery = '';
        if (searchTerm.length > 0) {
          searchQuery = `search_query=${encodeURIComponent(searchTerm)}&`;
        }
        if (filters.location) {
          searchQuery += `location=${encodeURIComponent(filters.location)}&`;
        }
        if (filters.source) {
          searchQuery += `source=${encodeURIComponent(filters.source)}&`;
        }
        if (filters.role) {
          searchQuery += `role=${encodeURIComponent(filters.role)}&`;
        }
        if (filters.min_experience) {
          searchQuery += `min_experience_years=${filters.min_experience}&`;
        }
        if (filters.max_experience) {
          searchQuery += `max_experience_years=${filters.max_experience}&`;
        }
        if (filters.remote) {
          searchQuery += `remote=true&`;
        }
        searchQuery += `sort_by=${sortBy}`;
        const endpoint = searchTerm.length > 0 || !filterNotSet(filters)
          ? `/job/search?${searchQuery}`
          : `/job/recommended?sort_by=${sortBy}`;
        const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}${endpoint}`);
        if (currentIdRef === requestIdRef.current) {
          setJobsWithRole(response.data);
          setSelectedRole(Object.keys(response.data)[0]);
          setLoading(false);
        }
      } catch (e) {
        if (currentIdRef === requestIdRef.current) {
          console.log(e);
          toast({
            position: "top-right",
            title: 'Cannot fetch jobs',
            description: "Some unexpected error occured. Please reload the page.",
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
        }
      }
    };

    fetchJobs();
  }, [debouncedSearchTerm, filters, sortBy]);
  return (
    <Container alignItems="center" margin="1% 15%" width="70%" maxWidth="100%">
        { searchTerm === "" ? ( selectedRole === "" ? <Text fontSize="lg">Recommended jobs according to your resume</Text> :
          <Flex align="center" wrap="wrap" gap={2}>
            <Text fontSize="lg">Recommended </Text>
            {roles && <Select
              onChange={(e) => setSelectedRole(e.target.value)}
              width="auto"
              size="sm"
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </Select>}
            <Text fontSize="lg"> jobs according to your resume</Text>
          </Flex>
        ) : (
          <Flex align="center" wrap="wrap" gap={2}>
            <Text fontSize="lg">Search results for </Text>
            {roles && <Select
              top="4px"
              onChange={(e) => setSelectedRole(e.target.value)}
              width="auto"
              size="sm"
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </Select>}
            <Text fontSize="lg"> jobs matching &ldquo;{searchTerm}&rdquo;</Text>
          </Flex>
        )}
      <Divider margin="24px 0"/>
        <HStack>
          <Text size="sm">Sort by </Text>
          <Select size="sm" w="240px" onChange={(e) => setSortBy(e.target.value)}>
            <option value="relevance">Relevance</option>
            <option value="inc_experience">Experience (Low to High)</option>
            <option value="desc_experience">Experience (High to Low)</option>
            <option value="salary">Average Salary</option>
          </Select>
        </HStack>
        {
          !loading ? (jobs?.map(job => <JobCard key={job.url} job={job} />) || <Text>No jobs found!</Text>) : (
            <>
              <Skeleton
                p={4}
                borderRadius="2xl"
                margin="24px 0"
                isLoaded={!loading}
                height="137px"
              />
              <Skeleton
                p={4}
                borderRadius="2xl"
                margin="24px 0"
                isLoaded={!loading}
                height="137px"
              />
              <Skeleton
                p={4}
                borderRadius="2xl"
                margin="24px 0"
                isLoaded={!loading}
                height="137px"
              />
            </>
          )
        }
    </Container>
  );
}

const HomePage = () => (
  <AuthProvider>
    <Home />
  </AuthProvider>
)

export default HomePage;
