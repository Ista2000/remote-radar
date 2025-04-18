"use client"
import { SmallCloseIcon } from "@chakra-ui/icons";
import { Container, Select, SelectProps, Tag, TagLabel, TagLeftIcon } from "@chakra-ui/react";
import { MouseEventHandler, ChangeEvent, useState } from "react";

interface MultiSelectProps extends SelectProps {
  onMultiSelectChange?: (selected: string[]) => void;
}

const MultiSelect = (props: MultiSelectProps) => {
  const [selectedItems, setSelectedItems] = useState<Array<string>>([]);
  const { onMultiSelectChange, ...selectProps } = props;

  const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value && !selectedItems.includes(value)) {
      const updated = [...selectedItems, value];
      setSelectedItems(updated);
      onMultiSelectChange?.(updated);
    }
  };
  const handleUnselect = (item: string) => {
    const updated = selectedItems.filter(i => i !== item);
    setSelectedItems(updated);
    onMultiSelectChange?.(updated);
  };

  return (
    <Container padding={0}>
      <Select {...selectProps} onChange={handleSelect} value={props.placeholder}>
          {props.children}
      </Select>
      {
        selectedItems.map(item => (
          <Tag
            size='md'
            key={item}
            variant='subtle'
            colorScheme='teal'
            onClick={e => {
              e.preventDefault();
              handleUnselect(item);
            }}
            marginRight="8px"
            marginTop="10px"
            style={{cursor: "pointer"}}
          >
            <TagLeftIcon boxSize='12px' as={SmallCloseIcon} />
            <TagLabel>{item}</TagLabel>
          </Tag>
        ))
      }
    </Container>
  );
};

export default MultiSelect;
