import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CompText MCP Agent Manager',
  description: 'Manage agents with Model Context Protocol connections',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
