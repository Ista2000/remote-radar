"use client"
import { Container, Divider, Skeleton, Text } from "@chakra-ui/react";
import { AuthProvider } from "./context/AuthContext";
import { useEffect, useState } from "react";
import axios from "axios";
import JobCard, { JobType } from "./components/JobCard";
import { useSearchContext } from "./context/SearchContext";
import { useRouter } from "next/navigation";

const Home = () => {
  const { searchTerm } = useSearchContext();
  const [jobs, setJobs] = useState<Array<JobType> | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const endpoint = searchTerm
          ? `/job/search?search_query=${encodeURIComponent(searchTerm)}`
          : "/job/recommended";
        const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}${endpoint}`);
        setJobs(response.data);
      } catch (e) {
        console.log(e);
      }
    };

    fetchJobs();
  }, [searchTerm]);

  return (
    <Container alignItems="center" margin="1% 15%" width="70%" maxWidth="100%">
      <Text fontSize="lg">
        { searchTerm === "" ? "Recommended jobs according to your resume" : `Search results for "${searchTerm}"` }
      </Text>
      <Divider margin="24px 0"/>
        {
          jobs?.map(job => <JobCard key={job.id} job={job} />) ||
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
