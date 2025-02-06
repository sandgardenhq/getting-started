import Head from 'next/head';
import DatabaseViewer from '@/components/DatabaseViewer'

export default function Details() {
  return (
    <>
      <Head>
        <title>SQL Viewer</title>
      </Head>
      <DatabaseViewer
        display="SELECT * FROM messages"
        query="SELECT tickets.id, tickets.subject, messages.sender_type, messages.content FROM messages JOIN tickets ON messages.ticket_id = tickets.id ORDER BY tickets.id, messages.id"
      />
    </>
  );
}
