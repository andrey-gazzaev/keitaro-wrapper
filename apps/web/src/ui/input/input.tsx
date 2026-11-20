import { memo, type ChangeEvent } from 'react';

type InputProps = {
  /** Current text. Absent on an uncontrolled input. */
  readonly value?: string;

  /** Initial text. Absent when the input is controlled. */
  readonly defaultValue?: string;

  /** Grey text shown while the input is empty. Absent when the field has none. */
  readonly placeholder?: string;

  /** Virtual keyboard. Absent for the default keyboard. */
  readonly inputMode?: 'numeric' | 'text';

  /** Submitted name. Absent when the surrounding form does not read this input by name. */
  readonly name?: string;

  /** Accessible name. Absent when a visible label names the input. */
  readonly 'aria-label'?: string;

  /** Stores the next text. Absent when the input is uncontrolled. */
  readonly onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
};

/** One text control. */
export const Input = memo(function Input({
  value,
  defaultValue,
  placeholder,
  inputMode,
  name,
  'aria-label': ariaLabel,
  onChange,
}: InputProps) {
  const controlled = value !== undefined;

  return (
    <input
      value={controlled ? value : undefined}
      defaultValue={controlled ? undefined : defaultValue}
      placeholder={placeholder}
      inputMode={inputMode}
      name={name}
      aria-label={ariaLabel}
      onChange={onChange}
    />
  );
});
