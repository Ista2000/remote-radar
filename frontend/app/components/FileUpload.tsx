"use client"

import { Button, Input, FormLabel, Box } from "@chakra-ui/react"
import { useRef, useState } from "react"

const FileUpload = ({
  onFileSelect,
}: {
  onFileSelect: (file: File | null) => void
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFileName(file?.name || null);
    onFileSelect(file);
  }

  const openFileDialog = () => {
    inputRef.current?.click();
  }

  return (
    <Box>
      <Input
        type="file"
        ref={inputRef}
        display="none"
        onChange={handleFileChange}
      />
      <Button onClick={openFileDialog} colorScheme="teal" variant="outline">
        Upload Resume
      </Button>
      {fileName && (
        <FormLabel mt={2} fontSize="sm" color="gray.600">
          Selected: {fileName}
        </FormLabel>
      )}
    </Box>
  );
}

export default FileUpload;
