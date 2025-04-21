"use client";
import { createContext, useContext, useState, ReactNode } from "react";

export type FilterType = {
  location: string | null;
  role: string | null;
  source: string | null;
  min_experience: number;
  max_experience: number | null;
  remote: boolean;
};

type SearchContextType = {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  filters: FilterType;
  setFilters: (filter: FilterType) => void;
};

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider = ({ children }: { children: ReactNode }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState<FilterType>({
    location: null,
    role: null,
    source: null,
    min_experience: 0,
    max_experience: null,
    remote: false,
  });

  return (
    <SearchContext.Provider value={{ searchTerm, setSearchTerm, filters, setFilters }}>
      {children}
    </SearchContext.Provider>
  );
};

export const useSearchContext = () => {
  const context = useContext(SearchContext);
  if (!context) throw new Error("useSearchContext must be used within SearchProvider");
  return context;
};