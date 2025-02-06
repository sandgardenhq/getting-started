import { Pool } from 'pg';
import { NextApiRequest, NextApiResponse } from 'next';

const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  ssl: false,
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { query } = req.body;

  try {
    const result = await pool.query(query);
    res.status(200).json({
      rows: result.rows,
      fields: result.fields.map(f => ({
        name: f.name,
        dataType: f.dataTypeID
      }))
    });
  } catch (error: any) {
    console.error(error);
    res.status(400).json({ error: error });
  }
}
