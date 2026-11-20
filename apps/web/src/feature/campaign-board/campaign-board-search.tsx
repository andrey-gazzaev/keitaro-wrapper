import type { ChangeEvent } from 'react';
import { Field, Input } from '@/ui';

type CampaignBoardSearchProps = {
  /** Search text. Empty when the field is blank. */
  readonly value: string;

  /** Stores the next search text. */
  readonly onChange: (value: string) => void;
};

/** Name or id field for the campaign board. */
export function CampaignBoardSearch({ value, onChange }: CampaignBoardSearchProps) {
  function onInput(event: ChangeEvent<HTMLInputElement>) {
    onChange(event.target.value);
  }

  return (
    <Field label="Поиск кампаний">
      <Input value={value} placeholder="Имя или id" onChange={onInput} />
    </Field>
  );
}
