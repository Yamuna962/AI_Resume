import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Avoid 308 redirects on /api/v1/* that drop Authorization headers
  skipTrailingSlashRedirect: true,
  devIndicators: {},
  // API proxy handled by src/app/api/v1/[...path]/route.ts (preserves Authorization header)
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  allowedDevOrigins: [
    "localhost",
    "localhost:3000",
    "localhost:3001",
    "127.0.0.1",
    "127.0.0.1:3000",
    "192.168.1.15",
    "192.168.1.15:3000",
    "192.168.1.15:3001",
    "192.168.29.229",
    "192.168.29.229:3000",
    "192.168.29.229:3001",
  ],
};

export default nextConfig;
