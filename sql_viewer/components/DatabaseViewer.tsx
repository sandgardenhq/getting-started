import React, { useState } from 'react';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from './ui/card';
import { Database } from 'lucide-react';
import { Button } from "./ui/button";


function jsonStringify(value: any) {
  if (typeof value === 'boolean') {
    return value.toString().toUpperCase();
  }
  return value;
}

const DatabaseViewer = ({ query, display }: { query: string, display: string }) => {
  const [results, setResults] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const executeQuery = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error);
      }

      setResults(data.rows);
      setColumns(data.fields.map(f => f.name));

    } catch (error) {
      console.error(error);
      setResults([]);
      setColumns([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <Card className="max-w-4xl mx-auto mb-4">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Database className="h-6 w-6 text-gray-500" />
            <div>
              <CardTitle>PostgreSQL Table Viewer</CardTitle>
              <CardDescription>Connected to database: tickets</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 p-4 mb-4 rounded-md flex justify-between items-center">
            <code className="text-sm text-gray-800">
              {display}
            </code>
            <Button
              onClick={executeQuery}
              disabled={loading}
              className="ml-auto"
            >
              Execute Query
            </Button>
          </div>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card className="max-w-4xl mx-auto text-monospace">
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  {columns.map((column) => (
                    <th key={column} className="h-12 px-4 text-left align-middle font-medium text-gray-500">{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.map((row, i) => (
                  <tr className="border-b border-gray-200" key={i}>
                    {columns.map((column) => (
                      <td className="p-4 align-middle" key={column}>{jsonStringify(row[column])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )
      }
    </div >
  );
}

export default DatabaseViewer;
