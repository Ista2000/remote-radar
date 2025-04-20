"use client"
import { Container, Divider, Flex, Select, Skeleton, Text, useToast } from "@chakra-ui/react";
import { AuthProvider } from "./context/AuthContext";
import { useEffect, useState } from "react";
import axios from "axios";
import JobCard, { JobType } from "./components/JobCard";
import { FilterType, useSearchContext } from "./context/SearchContext";

const filterNotSet = (filter: FilterType): boolean => {
  return !filter.location && !filter.experience && !filter.remote && !filter.role && !filter.source;
}

const Home = () => {
  const { searchTerm, filters } = useSearchContext();
  const [jobsWithRole, setJobsWithRole] = useState<Record<string, Array<JobType>> | null>(null);
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const jobs = jobsWithRole ? jobsWithRole[selectedRole] : null;
  const roles = jobsWithRole ? Object.keys(jobsWithRole) : [];
  const toast = useToast();

  useEffect(() => {
    setLoading(true);
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
        if (filters.experience) {
          searchQuery += `experience_years=${filters.experience}&`;
        }
        if (filters.remote) {
          searchQuery += `remote=true&`;
        }
        const endpoint = searchTerm.length > 0 || !filterNotSet(filters)
          ? `/job/search?${searchQuery}`
          : "/job/recommended";
        const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}${endpoint}`);
        setJobsWithRole(response.data);
        setSelectedRole(Object.keys(response.data)[0]);
        setLoading(false);
      } catch (e) {
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
    };

    fetchJobs();
  }, [searchTerm, filters]);

  return (
    <Container alignItems="center" margin="1% 15%" width="70%" maxWidth="100%">
        { searchTerm === "" ? ( selectedRole === "" ? <Text fontSize="lg">Recommended jobs according to your resume</Text> :
          <Flex align="center" wrap="wrap" gap={2}>
            <Text fontSize="lg">Recommended </Text>
            <Select
              onChange={(e) => setSelectedRole(e.target.value)}
              width="auto"
              size="sm"
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </Select>
            <Text fontSize="lg"> jobs according to your resume</Text>
          </Flex>
        ) : (
          <Flex align="center" wrap="wrap" gap={2}>
            <Text size="lg">Search results for </Text>
            <Select
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
            </Select>
            <Text size="lg"> jobs matching &ldquo;{searchTerm}&rdquo;</Text>
          </Flex>
        )}
      <Divider margin="24px 0"/>
        {
          !loading ? (jobs?.map(job => <JobCard key={job.url} job={job} />) || <Text>No jobs found!</Text>) : (
            <>
              <Skeleton
                p={4}
                borderRadius="2xl"
                margin="24px 0"
                isLoaded={!!jobs}
                height="137px"
              />
              <Skeleton
                p={4}
                borderRadius="2xl"
                margin="24px 0"
                isLoaded={!!jobs}
                height="137px"
              />
              <Skeleton
                p={4}
                borderRadius="2xl"
                margin="24px 0"
                isLoaded={!!jobs}
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
