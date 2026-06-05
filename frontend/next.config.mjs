/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Server-side proxy target. Independent of the public API base so the browser
    // only ever needs port 3000 to be forwarded.
    const backend = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000";
    return [{ source: "/backend/:path*", destination: `${backend}/:path*` }];
  },
};

export default nextConfig;
