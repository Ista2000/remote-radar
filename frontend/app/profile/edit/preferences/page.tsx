"use client";

import { useEffect, useState } from "react";
import { ChevronDownIcon } from "@chakra-ui/icons";
import {
  Button,
  FormControl,
  FormLabel,
  Switch,
  VStack,
  Spinner,
  FormErrorMessage,
  useToast,
  Box,
  Heading,
} from "@chakra-ui/react";
import axios from "axios";
import MultiSelect from "../../../components/MultiSelect";
import { useAuthContext } from "../../../hooks/useAuth";
import { AuthProvider } from "@/app/context/AuthContext";

interface Errors {
  all?: string;
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
  msg: string;
  type: string;
  url: string;
}

const EditPreferences = () => {
  const { user: authUser } = useAuthContext();
  const [user, setUser] = useState({
    preferred_roles: authUser?.preferred_roles ?? [],
    preferred_locations: authUser?.preferred_locations ?? [],
    preferred_sources: authUser?.preferred_sources ?? [],
    receive_email_alerts: authUser?.receive_email_alerts ?? true,
  });
  const [rls, setRls] = useState({
    roles: [] as string[],
    locations: {} as Record<string, string[]>,
    sources: [] as string[],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Errors | null>(null);
  const toast = useToast();

  useEffect(() => {
    const fetchRLS = async () => {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/rls/`);
      setRls({
        roles: response.data.roles,
        locations: response.data.locations,
        sources: response.data.sources,
      });
      setLoading(false);
    };
    fetchRLS();
  }, []);

  useEffect(() => setUser({
    preferred_roles: authUser?.preferred_roles ?? [],
    preferred_locations: authUser?.preferred_locations ?? [],
    preferred_sources: authUser?.preferred_sources ?? [],
    receive_email_alerts: authUser?.receive_email_alerts ?? true,
  }), [authUser]);

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    try {
      e.preventDefault();
      setLoading(true);
      setError(null);
      const formData = new FormData();
      formData.append("updated_user", JSON.stringify(user));
      const response = await axios.patch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      toast({
        position: "top-right",
        title: "Preferences updated",
        description: `Changes saved successfully for ${response.data.full_name}`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (e) {
      if (axios.isAxiosError(e)) {
        const details = e.response?.data?.detail;
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

  return (
    <VStack spacing={4} align="stretch">
      <Heading>Edit Preferences</Heading>
      <FormControl isInvalid={!!error?.preferred_roles}>
        <FormLabel>Preferred Roles</FormLabel>
        <MultiSelect
          name="preferred_roles"
          icon={<ChevronDownIcon />}
          placeholder="Select preferred roles"
          width="100%"
          onMultiSelectChange={(selected_roles) =>
            setUser({ ...user, preferred_roles: selected_roles })
          }
          defaultValue={user.preferred_roles}
        >
          {rls.roles.map((role) => (
            <option key={role} value={role}>{role}</option>
          ))}
        </MultiSelect>
        <FormErrorMessage>{error?.preferred_roles}</FormErrorMessage>
      </FormControl>

      <FormControl isInvalid={!!error?.preferred_locations}>
        <FormLabel>Preferred Locations</FormLabel>
        <MultiSelect
          name="preferred_locations"
          icon={<ChevronDownIcon />}
          placeholder="Select preferred locations"
          width="100%"
          onMultiSelectChange={(selected_locations) =>
            setUser({ ...user, preferred_locations: selected_locations })
          }
          defaultValue={user.preferred_locations}
        >
          {Object.entries(rls.locations).flatMap(([country, cities]) =>
            cities.map((city) => (
              <option key={`${city}, ${country}`} value={`${city}, ${country}`}>
                {`${city}, ${country}`}
              </option>
            ))
          )}
        </MultiSelect>
        <FormErrorMessage>{error?.preferred_locations}</FormErrorMessage>
      </FormControl>

      <FormControl isInvalid={!!error?.preferred_sources}>
        <FormLabel>Preferred Sources</FormLabel>
        <MultiSelect
          name="preferred_sources"
          icon={<ChevronDownIcon />}
          placeholder="Select preferred sources"
          width="100%"
          onMultiSelectChange={(selected_sources) =>
            setUser({ ...user, preferred_sources: selected_sources })
          }
          defaultValue={user.preferred_sources}
        >
          {rls.sources.map((source) => (
            <option key={source} value={source}>{source}</option>
          ))}
        </MultiSelect>
        <FormErrorMessage>{error?.preferred_sources}</FormErrorMessage>
      </FormControl>

      <FormControl display="flex" alignItems="center" isInvalid={!!error?.receive_email_alerts}>
        <FormLabel htmlFor="email-alerts" mb="0">
          Enable email alerts?
        </FormLabel>
        <Switch
          id="email-alerts"
          isChecked={user.receive_email_alerts}
          onChange={() =>
            setUser({ ...user, receive_email_alerts: !user.receive_email_alerts })
          }
        />
        <FormErrorMessage>{error?.receive_email_alerts}</FormErrorMessage>
      </FormControl>

      <Button colorScheme="teal" onClick={handleSubmit} isDisabled={loading}>
        {loading ? <Spinner size="sm" /> : "Save Preferences"}
      </Button>

      <FormControl isInvalid={!!error?.all}>
        <FormErrorMessage>{error?.all}</FormErrorMessage>
      </FormControl>
    </VStack>
  );
};

const EditPreferencesPage = () => (
  <AuthProvider>
    <Box maxW="lg" mx="auto" mt={10} p={6} boxShadow="md" borderRadius="md">
      <EditPreferences />
    </Box>
  </AuthProvider>
)

export default EditPreferencesPage;
