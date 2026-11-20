import { RouterProvider } from 'react-router-dom';
import { Providers } from './providers';
import { rootRouter } from './router';

/** Application shell. */
export function App() {
  return (
    <Providers>
      <RouterProvider router={rootRouter} />
    </Providers>
  );
}
