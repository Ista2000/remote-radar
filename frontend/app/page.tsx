"use client"
import { Container, Divider, Skeleton, Text } from "@chakra-ui/react";
import { AuthProvider } from "./context/AuthContext";
import { useEffect, useState } from "react";
import axios from "axios";
import JobCard, { JobType } from "./components/JobCard";

const Home = () => {
  const [jobs, setJobs] = useState<Array<JobType> | null>(null);
  useEffect(() => {
    const getJobs = async () => {
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/job/recommended`,
        )
        setJobs(response.data);
      } catch (e) {
        console.log(e);
      }
    };

    getJobs();
  }, []);
  return (
    <Container alignItems="center" margin="1% 15%" width="70%" maxWidth="100%">
      <Text fontSize="lg">Recommended jobs according to your resume</Text>
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
