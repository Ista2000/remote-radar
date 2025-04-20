"use client"

import { useEffect, useState } from "react";
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
  repeat_password: string;
  full_name: string;
  experience_years: number;
  preferred_roles: Array<string>;
  preferred_locations: Array<string>;
  preferred_sources: Array<string>;
  receive_email_alerts: boolean;
}

interface Errors {
  all?: string;
  email?: string;
  password?: string;
  repeat_password?: string;
  full_name?: string;
  experience_years?: string;
  preferred_roles?: string;
  preferred_locations?: string;
  preferred_sources?: string;
  receive_email_alerts?: string;
}

interface ErrorDetail {
  ctx?: {
    error?: string,
    reason?: string
  };
  loc: Array<keyof Errors>;
  input?: string;
  msg: string;
  type: string;
  url: string;
}

interface SignupProps {
  onSignupSuccess: () => void;
}

const Signup = ({onSignupSuccess}: SignupProps) => {
  const [user, setUser] = useState<UserCreate>({
    email: '',
    password: '',
    repeat_password: '',
    full_name: '',
    experience_years: 0,
    preferred_roles: [],
    preferred_locations: [],
    preferred_sources: [],
    receive_email_alerts: true,
  });
  const [resume, setResume] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Errors | null>(null);
  const [rls, setRls] = useState<
    {roles: Array<string>, locations: Record<string, Array<string>>, sources: Array<string>}
  >({roles: [], locations: {}, sources: []});
  const toast = useToast();

  useEffect(() => {
    const fetchRLS = async () => {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/rls/`);
      setRls({
        roles: response?.data?.roles,
        locations: response?.data?.locations,
        sources: response?.data?.sources,
      })
      setLoading(false);
    };
    fetchRLS();
  }, []);

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    try {
      e.preventDefault();
      setLoading(true);
      setError(null);
      const formData = new FormData();
      formData.append('user', JSON.stringify(user));
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
        const details = e.response?.data?.detail;
        if (typeof details === 'string') {
          setError({all: details || "Failed to create user"});
        } else {
          setError(
            details.reduce((acc: Errors, detail: ErrorDetail) => {
              console.log(detail);
              acc[detail.loc[0]] = detail.ctx?.error || detail.ctx?.reason || detail.msg;
              return acc;
            }, {} as Errors)
          );
        }
      } else {
        console.log(e);
        setError({all: "An unexpected error occured"})
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
    <FileUpload onFileSelect={file => setResume(file)} width="100%" height="100px"/>

    <FormControl isInvalid={!!error?.email} isRequired marginTop="24px">
      <FormLabel htmlFor="email">Email</FormLabel>
      <Input name="email" type="email" onChange={handleChange} />
      <FormErrorMessage>{error?.email}</FormErrorMessage>
    </FormControl>

    <FormControl isInvalid={!!error?.password} isRequired>
      <FormLabel htmlFor="password">Password</FormLabel>
      <Input name="password" type="password" onChange={handleChange} />
      <FormErrorMessage>{error?.password}</FormErrorMessage>
    </FormControl>

    <FormControl isInvalid={!!error?.repeat_password} isRequired>
      <FormLabel htmlFor="repeat_password">Repeat Password</FormLabel>
      <Input name="repeat_password" type="password" onChange={handleChange} />
      {!error?.repeat_password ?
          <FormHelperText>Enter your password again</FormHelperText> :
          <FormErrorMessage>{error?.repeat_password}</FormErrorMessage>
      }
    </FormControl>

    <FormControl isInvalid={!!error?.full_name} isRequired>
      <FormLabel htmlFor="full_name">Full name</FormLabel>
      <Input name="full_name" type="full_name" onChange={handleChange} />
      <FormErrorMessage>{error?.full_name}</FormErrorMessage>
    </FormControl>

    <FormControl isInvalid={!!error?.experience_years}>
      <FormLabel htmlFor="experience_years">Experience (in years)</FormLabel>
      <NumberInput name="experience_years" onChange={(_, v) => setUser({...user, experience_years: v})} >
        <NumberInputField />
        <NumberInputStepper>
          <NumberIncrementStepper />
          <NumberDecrementStepper />
        </NumberInputStepper>
      </NumberInput>
      <FormErrorMessage>{error?.experience_years}</FormErrorMessage>
    </FormControl>

    <FormControl isInvalid={!!error?.preferred_roles}>
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
        {rls.roles.map(role => (
          <option value={role} key={role}>{role}</option>
        ))}
      </MultiSelect>
      <FormErrorMessage>{error?.preferred_roles}</FormErrorMessage>
    </FormControl>

    <FormControl isInvalid={!!error?.preferred_locations}>
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
        {Object.entries(rls.locations).flatMap(([country, cities]) => cities.map(city => (
          <option value={`${city}, ${country}`} key={`${city}, ${country}`}>{`${city}, ${country}`}</option>
        )))}
      </MultiSelect>
      <FormErrorMessage>{error?.preferred_locations}</FormErrorMessage>
    </FormControl>

    <FormControl isInvalid={!!error?.preferred_sources}>
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
        {rls.sources.map(source => (
          <option value={source} key={source}>{source}</option>
        ))}
      </MultiSelect>
      <FormErrorMessage>{error?.preferred_sources}</FormErrorMessage>
    </FormControl>

    <FormControl display='flex' alignItems='center' isInvalid={!!error?.receive_email_alerts}>
      <FormLabel htmlFor='email-alerts' mb='0'>
        Enable email alerts?
      </FormLabel>
      <Switch id='email-alerts' onChange={() => setUser({...user, receive_email_alerts: !user.receive_email_alerts})} defaultChecked/>
      <FormErrorMessage>{error?.receive_email_alerts}</FormErrorMessage>
    </FormControl>

    <Button colorScheme="teal" onClick={handleSubmit} isDisabled={loading}>
      {loading ? <Spinner size="sm" /> : "Sign up"}
    </Button>

    <FormControl isInvalid={!!error?.all}>
      <FormErrorMessage>{error?.all}</FormErrorMessage>
    </FormControl>
  </VStack>
  );
};

export default Signup;