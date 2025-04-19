import { ColorModeScript } from '@chakra-ui/react';
import { ChakraProviders } from './components/ChakraProviders';
import { Metadata } from 'next';
import theme from './theme';

export const metadata: Metadata = {
  title: 'RemoteRadar',
  description: 'Find and apply to remote jobs easily',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ChakraProviders>{children}</ChakraProviders>
      </body>
    </html>
  );
}