import { HomePage } from '@/views';
import { Providers } from './providers';

/** Application shell. */
export function App() {
  return (
    <Providers>
      <HomePage />
    </Providers>
  );
}
