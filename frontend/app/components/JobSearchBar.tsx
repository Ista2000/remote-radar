import {
  Box,
  Flex,
  InputGroup,
  Input,
  InputLeftElement,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Switch,
  Text,
  VStack,
  useColorModeValue,
  HStack,
  Button,
  RangeSlider,
  RangeSliderTrack,
  RangeSliderThumb,
  RangeSliderFilledTrack,
  FlexProps,
} from "@chakra-ui/react";
import { SearchIcon, ChevronDownIcon, SettingsIcon } from "@chakra-ui/icons";
import { useEffect, useState } from "react";
import axios from "axios";
import { useSearchContext } from "../context/SearchContext";

const JobSearchBar = (props: FlexProps) => {
  const [filtersOpen, setFiltersOpen] = useState(false);
  const { searchTerm, filters, setSearchTerm, setFilters } = useSearchContext();
  const textColor = useColorModeValue("gray.800", "gray.100");
  const [rls, setRls] = useState<
    {roles: Array<string>, locations: Record<string, Array<string>>, sources: Array<string>}
  >({roles: [], locations: {}, sources: []});

  useEffect(() => {
    const fetchRLS = async () => {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/rls/`);
      setRls({
        roles: response?.data?.roles ?? [],
        locations: response?.data?.locations ?? {},
        sources: response?.data?.sources ?? [],
      });
    };
    fetchRLS();
  }, []);

  return (
    <Flex
      {...props}
      align="center"
      alignSelf="center"
      justify="space-between"
      px={6}
      py={3}
      bg={useColorModeValue("whiteAlpha.900", "gray.800")}
      borderBottom="1px solid"
      borderColor={useColorModeValue("gray.200", "whiteAlpha.200")}
      borderRadius="lg"
      color={textColor}
    >
      {/* Search Input */}
      <InputGroup opacity={filtersOpen ? 0.4 : 1} pointerEvents={filtersOpen ? "none" : "auto"}>
        <InputLeftElement pointerEvents="none">
          <SearchIcon color="teal.400" />
        </InputLeftElement>
        <Input
          placeholder="Search jobs..."
          borderRadius="xl"
          bg={useColorModeValue("white", "gray.700")}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          focusBorderColor="teal.400"
          _placeholder={{ color: "gray.400" }}
        />
      </InputGroup>

      {/* Filters Button */}
      <Menu isOpen={filtersOpen} onClose={() => setFiltersOpen(false)}>
        <MenuButton
          as={IconButton}
          icon={<SettingsIcon />}
          variant="ghost"
          aria-label="Filter"
          onClick={() => setFiltersOpen(!filtersOpen)}
          ml={4}
        />
        <MenuList minW="300px" p={4}>
          <VStack align="start" spacing={4}>
            {/* Role Filter */}
            <FilterMenu
              title="Role"
              items={rls.roles}
              selected={filters.role}
              onSelect={(role) => setFilters({ ...filters, role })}
              onUnselect={() => setFilters({...filters, role: null})}
            />

            {/* Location Filter */}
            <FilterMenu
              title="Location"
              items={
                Object.entries(rls.locations).flatMap(([country, cities]) =>
                  cities.map((city) => `${city}, ${country}`)
                )
              }
              selected={filters.location}
              onSelect={(location) => setFilters({ ...filters, location })}
              onUnselect={() => setFilters({...filters, location: null})} />

            {/* Source Filter */}
            <FilterMenu
              title="Source"
              items={rls.sources}
              selected={filters.source}
              onSelect={(source) => setFilters({ ...filters, source })}
              onUnselect={() => setFilters({...filters, source: null})}
            />

            {/* Experience Slider */}
            <Box w="100%">
              <Text fontSize="sm" mb={1}>Experience (yrs): {filters.min_experience} - {filters.max_experience ? filters.max_experience : "15+"}</Text>
              <RangeSlider
                aria-label={["experience-slider-min", "experience-slider-max"]}
                onChangeEnd={([min_val, max_val]) => setFilters({ ...filters,  min_experience: min_val, max_experience: max_val === 15 ? null : max_val })}
                defaultValue={[0, 15]}
                min={0}
                max={15}
              >
                <RangeSliderTrack>
                  <RangeSliderFilledTrack bg="teal.400" />
                </RangeSliderTrack>
                <RangeSliderThumb index={0}/>
                <RangeSliderThumb index={1}/>
              </RangeSlider>
            </Box>

            {/* Remote Switch */}
            <HStack justify="space-between" w="100%">
              <Text fontSize="sm">Remote Only</Text>
              <Switch
                colorScheme="teal"
                isChecked={filters.remote}
                onChange={(e) => setFilters({ ...filters, remote: e.target.checked })}
              />
            </HStack>

            {/* Clear filters */}
            <Button
              w="100%"
              colorScheme="teal"
              onClick={() => setFilters({
                location: null,
                role: null,
                source: null,
                min_experience: 0,
                max_experience: null,
                remote: false,
              })}
            >
              Clear all filters
            </Button>
          </VStack>
        </MenuList>
      </Menu>
    </Flex>
  );
}

type FilterMenuProps = {
  title: string;
  items: Array<string>;
  selected: string | null;
  onSelect: (item: string) => void;
  onUnselect: () => void;
};

const FilterMenu = ({ title, items, selected, onSelect, onUnselect } : FilterMenuProps) => {
  return (
    <Menu>
      <MenuButton
        w="100%"
        textAlign="left"
        py={2}
        px={3}
        borderRadius="md"
        bg={useColorModeValue("gray.100", "gray.700")}
        _hover={{ bg: useColorModeValue("gray.200", "gray.600") }}
      >
        <Flex align="center" justify="space-between">
          <Text fontSize="sm">{selected || `Select ${title.toLowerCase()}`}</Text>
          <ChevronDownIcon />
        </Flex>
      </MenuButton>
      <MenuList zIndex="dropdown">
        <MenuItem key={"None"} onClick={onUnselect}>
          Do not filter by {title}
        </MenuItem>
        {items.map((item) => (
          <MenuItem key={item} onClick={() => onSelect(item)}>
            {item}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
};

export default JobSearchBar;
