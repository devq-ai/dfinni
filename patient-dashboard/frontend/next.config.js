/** @type {import('next').NextConfig} */
const { config } = require('dotenv');
const path = require('path');

// Load environment variables from parent directory
config({ path: path.resolve(__dirname, '../../../.env') });

const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
}

module.exports = nextConfig