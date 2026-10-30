import { PrismaClient } from "@prisma/client";
import { cleanupExpired } from "../src/lib/cleanup";
if (!process.argv.includes("--apply")) throw new Error("Explicit --apply required; use a dedicated maintenance role and approved database");
const db = new PrismaClient();
try { console.log(await cleanupExpired(db)); } finally { await db.$disconnect(); }
