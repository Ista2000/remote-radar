"use client"

import { useState } from "react";
import { ChevronDownIcon } from "@chakra-ui/icons"
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Spinner,
  FormErrorMessage,
  FormHelperText,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  useToast,
} from "@chakra-ui/react";
import axios from "axios";
import MultiSelect from "../components/MultiSelect";
import FileUpload from "../components/FileUpload";

interface UserCreate {
  email: string;
  password: string;
  password_repeat: string;
  full_name: string;
  experience_years: number;
  preferred_roles: Array<string>;
  preferred_locations: Array<string>;
  preferred_sources: Array<string>;
  receive_email_alerts: boolean;
}

const Signup = ({onSignupSuccess}: {onSignupSuccess: () => void}) => {
  const [user, setUser] = useState<UserCreate>({
    email: '',
    password: '',
    password_repeat: '',
    full_name: '',
    experience_years: 0,
    preferred_roles: [],
    preferred_locations: [],
    preferred_sources: [],
    receive_email_alerts: true,
  });
  const [resume, setResume] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    try {
      e.preventDefault();
      setLoading(true);
      setError(null);
      const {password_repeat, ...userData} = user;
      const formData = new FormData();
      formData.append('user', JSON.stringify(userData));
      if (resume) {
        formData.append('resume', resume);
      }
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      onSignupSuccess();
      toast({
        position: "top-right",
        title: 'Signup success',
        description: `Successfully created account for ${response.data.full_name}. Please login to continue.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });


    } catch (e) {
      if (axios.isAxiosError(e)) {
        setError(e.response?.data?.detail || "Failed to create user");
      } else {
        console.log(e);
        setError("An unexpected error occured")
      }
    } finally {
      setLoading(false);
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  }

  return (
  <VStack spacing={4} align="stretch">
    <FileUpload onFileSelect={file => setResume(file)}/>

    <FormControl isRequired>
      <FormLabel htmlFor="email">Email</FormLabel>
      <Input name="email" type="email" onChange={handleChange} />
    </FormControl>

    <FormControl isRequired>
      <FormLabel htmlFor="password">Password</FormLabel>
      <Input name="password" type="password" onChange={handleChange} />
    </FormControl>

    <FormControl isRequired>
      <FormLabel htmlFor="password_repeat">Repeat Password</FormLabel>
      <Input name="password_repeat" type="password_repeat" onChange={handleChange} />
      <FormHelperText>Enter your password again</FormHelperText>
    </FormControl>

    <FormControl isRequired>
      <FormLabel htmlFor="full_name">Full name</FormLabel>
      <Input name="full_name" type="full_name" onChange={handleChange} />
    </FormControl>

    <FormControl>
      <FormLabel htmlFor="experience_years">Experience (in years)</FormLabel>
      <NumberInput name="experience_years" onChange={(_, v) => setUser({...user, experience_years: v})} >
        <NumberInputField />
        <NumberInputStepper>
          <NumberIncrementStepper />
          <NumberDecrementStepper />
        </NumberInputStepper>
      </NumberInput>
    </FormControl>

    <FormControl>
      <FormLabel htmlFor="preferred_roles">Preferred roles</FormLabel>
        <MultiSelect
          name="preferred_roles"
          icon={<ChevronDownIcon />}
          placeholder="Select preferred roles"
          width="100%"
          onMultiSelectChange={
            selected_roles =>
              setUser({...user, preferred_roles: selected_roles})
          }
        >
          <option value='Software Engineer'>Software Engineer</option>
          <option value='Software Engineer 2'>Software Engineer 2</option>
          <option value='Software Engineer 3'>Software Engineer 3</option>
          <option value='Teacher'>Teacher</option>
          <option value='Artist'>Artist</option>
        </MultiSelect>
    </FormControl>

    <FormControl>
      <FormLabel htmlFor="preferred_location">Preferred locations</FormLabel>
        <MultiSelect
          name="preferred_locations"
          icon={<ChevronDownIcon />}
          placeholder="Select preferred locations"
          width="100%"
          onMultiSelectChange={
            selected_locations =>
              setUser({...user, preferred_locations: selected_locations})
          }
        >
          <option value='India'>India</option>
          <option value='United States'>United States</option>
          <option value='United Kingdom'>United Kingdom</option>
          <option value='Remote'>Remote</option>
        </MultiSelect>
    </FormControl>

    <FormControl>
      <FormLabel htmlFor="preferred_sources">Preferred Sources</FormLabel>
        <MultiSelect
          name="preferred_sources"
          icon={<ChevronDownIcon />}
          placeholder="Select preferred sources"
          width="100%"
          onMultiSelectChange={
            selected_sources => setUser({...user, preferred_sources: selected_sources})
          }
        >
          <option value='LinkedIn'>LinkedIn</option>
          <option value='Wellfound'>Wellfound</option>
          <option value='Indeed'>Indeed</option>
        </MultiSelect>
    </FormControl>

    <FormControl display='flex' alignItems='center'>
      <FormLabel htmlFor='email-alerts' mb='0'>
        Enable email alerts?
      </FormLabel>
      <Switch id='email-alerts' onChange={e => setUser({...user, receive_email_alerts: !user.receive_email_alerts})} defaultChecked/>
    </FormControl>

    <Button colorScheme="teal" onClick={handleSubmit} isDisabled={loading}>
      {loading ? <Spinner size="sm" /> : "Sign up"}
    </Button>

    <FormControl isInvalid={!!error}>
      <FormErrorMessage>
        {error}
      </FormErrorMessage>
    </FormControl>
  </VStack>
  );
};

export default Signup;