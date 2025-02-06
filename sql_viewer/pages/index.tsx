import Head from 'next/head';
import DatabaseViewer from '@/components/DatabaseViewer'

export default function Home() {
  return (
    <>
      <Head>
        <title>SQL Viewer</title>
      </Head>
      <DatabaseViewer display="SELECT id,subject,needs_escalation FROM tickets" query="SELECT id,subject,needs_escalation FROM tickets" />
    </>
  );
}
