"use client"
import { Box, Card, Container } from "@chakra-ui/react";
import { AuthProvider } from "./context/AuthContext";

const Home = () => {
  return (
    <Container alignItems="center" margin="1% 15%" width="70%" maxWidth="100%">
      <Card padding="12px">
        <div>
          Home
        </div>
      </Card>
    </Container>
  );
}

const HomePage = () => (
  <AuthProvider>
    <Home />
  </AuthProvider>
)

export default HomePage;
