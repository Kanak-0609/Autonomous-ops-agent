import type { NextApiRequest, NextApiResponse } from "next";
import { getAuth } from "@clerk/nextjs/server";
import { Client } from "pg";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { userId, sessionClaims } = getAuth(req);

  if (!userId) {
    return res.status(401).json({ error: "Not signed in" });
  }

  const email = (sessionClaims?.email as string) || `user-${userId}@unknown.com`;
  const slug = `clerk-${userId}`.toLowerCase();
  const name = email.split("@")[0];

  const client = new Client({ connectionString: process.env.DATABASE_URL });
  await client.connect();

  try {
    const existing = await client.query(
      "SELECT id, name, slug FROM organizations WHERE slug = $1",
      [slug]
    );

    if (existing.rows.length > 0) {
      return res.status(200).json(existing.rows[0]);
    }

    const created = await client.query(
      "INSERT INTO organizations (name, slug) VALUES ($1, $2) RETURNING id, name, slug",
      [name, slug]
    );

    const org = created.rows[0];

    await client.query(
      `INSERT INTO company_config (organization_id, services, standard_rate, onboarding_rate, availability, response_policy)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [
        org.id,
        "Update this in your settings",
        "Update this in your settings",
        "Update this in your settings",
        "Update this in your settings",
        "Be warm and professional.",
      ]
    );

    return res.status(200).json(org);
  } finally {
    await client.end();
  }
}