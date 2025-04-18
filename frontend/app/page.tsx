"use client"
import { AuthProvider } from "./context/AuthContext";

const Home = () => {
  return (
    <div>Home</div>
  );
}

const HomePage = () => (
  <AuthProvider>
    <Home />
  </AuthProvider>
)

export default HomePage;
