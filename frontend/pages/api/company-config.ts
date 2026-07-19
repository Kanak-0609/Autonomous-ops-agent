import type { NextApiRequest, NextApiResponse } from "next";
import { getAuth } from "@clerk/nextjs/server";
import { Client } from "pg";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { userId } = getAuth(req);

  if (!userId) {
    return res.status(401).json({ error: "Not signed in" });
  }

  const slug = `clerk-${userId}`.toLowerCase();

  const client = new Client({ connectionString: process.env.DATABASE_URL });
  await client.connect();

  try {
    const orgResult = await client.query(
      "SELECT id FROM organizations WHERE slug = $1",
      [slug]
    );

    if (orgResult.rows.length === 0) {
      return res.status(404).json({ error: "Organization not found. Load the dashboard first." });
    }

    const organizationId = orgResult.rows[0].id;

    if (req.method === "GET") {
      const configResult = await client.query(
        "SELECT * FROM company_config WHERE organization_id = $1",
        [organizationId]
      );
      return res.status(200).json(configResult.rows[0] || null);
    }

    if (req.method === "POST") {
      const { services, standard_rate, onboarding_rate, availability, response_policy } = req.body;

      await client.query(
        `INSERT INTO company_config (organization_id, services, standard_rate, onboarding_rate, availability, response_policy, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, now())
         ON CONFLICT (organization_id) DO UPDATE SET
           services = EXCLUDED.services,
           standard_rate = EXCLUDED.standard_rate,
           onboarding_rate = EXCLUDED.onboarding_rate,
           availability = EXCLUDED.availability,
           response_policy = EXCLUDED.response_policy,
           updated_at = now()`,
        [organizationId, services, standard_rate, onboarding_rate, availability, response_policy]
      );

      return res.status(200).json({ success: true });
    }

    return res.status(405).json({ error: "Method not allowed" });
  } finally {
    await client.end();
  }
}