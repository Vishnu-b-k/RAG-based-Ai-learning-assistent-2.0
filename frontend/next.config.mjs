/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'ai-learning-assistant-backend-lyhw.onrender.com',
                port: '',
                pathname: '/images/**',
            },
        ],
    },
};

export default nextConfig;
