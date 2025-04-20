"use client";

import { useState } from "react";
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Spinner,
  FormErrorMessage,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  useToast,
  Box,
  FormHelperText,
} from "@chakra-ui/react";
import axios from "axios";
import FileUpload from "../../components/FileUpload";
import { AuthProvider } from "../../context/AuthContext";

interface UserEdit {
  password?: string;
  repeat_password?: string;
  full_name?: string;
  experience_years?: number;
  receive_email_alerts?: boolean;
}

interface Errors {
  all?: string;
  password?: string;
  repeat_password?: string;
  full_name?: string;
  experience_years?: string;
  receive_email_alerts?: string;
}

interface ErrorDetail {
  ctx?: {
    error?: string,
    reason?: string
  };
  loc: Array<keyof Errors>;
  msg: string;
  type: string;
  url: string;
}

const EditUser = () => {
  const [user, setUser] = useState<UserEdit | null>(null);
  const [resume, setResume] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Errors | null>(null);
  const toast = useToast();

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    try {
      e.preventDefault();
      setLoading(true);
      setError(null);
      const formData = new FormData();
      formData.append("updated_user", JSON.stringify(user));
      console.log(JSON.stringify(user));
      if (resume) {
        formData.append("resume", resume);
      }

      const response = await axios.patch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      toast({
        position: "top-right",
        title: "Profile updated",
        description: `Changes saved successfully for ${response.data.full_name}`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (e) {
      if (axios.isAxiosError(e)) {
        const details = e.response?.data?.detail;
        console.log(details);
        if (typeof details === "string") {
          setError({ all: details });
        } else {
          setError(
            details.reduce((acc: Errors, detail: ErrorDetail) => {
              acc[detail.loc[0]] = detail.ctx?.error || detail.ctx?.reason || detail.msg;
              return acc;
            }, {} as Errors)
          );
        }
      } else {
        setError({ all: "An unexpected error occurred" });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(JSON.stringify(user));
    if (e.target.value === '') {
      setUser({ ...user, [e.target.name]: null });
    } else {
      setUser({ ...user, [e.target.name]: e.target.value });
    }
  };

  return (
    <VStack spacing={4} align="stretch">
      <FileUpload onFileSelect={file => setResume(file)} width="100%" height="100px" />

      <FormControl isInvalid={!!error?.password}>
        <FormLabel htmlFor="password">New Password</FormLabel>
        <Input name="password" type="password" onChange={handleChange} />
        <FormErrorMessage>{error?.password}</FormErrorMessage>
      </FormControl>

      <FormControl isInvalid={!!error?.repeat_password}>
        <FormLabel htmlFor="repeat_password">Repeat Password</FormLabel>
        <Input name="repeat_password" type="password" onChange={handleChange} />
        {!error?.repeat_password ?
            <FormHelperText>Enter your password again</FormHelperText> :
            <FormErrorMessage>{error?.repeat_password}</FormErrorMessage>
        }
      </FormControl>

      <FormControl isInvalid={!!error?.full_name}>
        <FormLabel htmlFor="full_name">Full name</FormLabel>
        <Input
          name="full_name"
          type="text"
          onChange={handleChange}
        />
        <FormErrorMessage>{error?.full_name}</FormErrorMessage>
      </FormControl>

      <FormControl isInvalid={!!error?.experience_years}>
        <FormLabel htmlFor="experience_years">Experience (in years)</FormLabel>
        <NumberInput
          onChange={(_, value) => setUser({ ...user, experience_years: value })}
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
        <FormErrorMessage>{error?.experience_years}</FormErrorMessage>
      </FormControl>

      <FormControl display="flex" alignItems="center" isInvalid={!!error?.receive_email_alerts}>
        <FormLabel htmlFor="email-alerts" mb="0">
          Enable email alerts?
        </FormLabel>
        <Switch
          id="email-alerts"
          isChecked={user?.receive_email_alerts || true}
          onChange={() =>
            setUser({ ...user, receive_email_alerts: !user?.receive_email_alerts })
          }
        />
        <FormErrorMessage>{error?.receive_email_alerts}</FormErrorMessage>
      </FormControl>

      <Button colorScheme="teal" onClick={handleSubmit} isDisabled={loading}>
        {loading ? <Spinner size="sm" /> : "Save Changes"}
      </Button>

      <FormControl isInvalid={!!error?.all}>
        <FormErrorMessage>{error?.all}</FormErrorMessage>
      </FormControl>
    </VStack>
  );
};

const EditUserPage = () => (
  <AuthProvider>
    <Box maxW="lg" mx="auto" mt={10} p={6} boxShadow="md" borderRadius="md">
      <EditUser />
    </Box>
  </AuthProvider>
)

export default EditUserPage;