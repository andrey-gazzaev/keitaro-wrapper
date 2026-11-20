import { useEffect, useState } from 'react';

/** Text that changes only after it has stayed still for `delay` milliseconds. */
export function useDebounce(value: string, delay: number): string {
  const [settled, setSettled] = useState(value);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSettled(value);
    }, delay);

    return () => {
      window.clearTimeout(timer);
    };
  }, [value, delay]);

  return settled;
}
