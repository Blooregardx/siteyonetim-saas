import { test } from "node:test";
import assert from "node:assert/strict";
import { PrismaClient } from "@prisma/client";
import { management } from "../src/lib/management";

// Fail closed: this suite must never run with the application's production URL.
const url = process.env.TEST_DATABASE_URL;
if (!url || !['localhost', '127.0.0.1'].includes(new URL(url).hostname) || new URL(url).pathname !== '/siteyonetim_test') throw new Error('Dedicated local TEST_DATABASE_URL required');
const db = new PrismaClient({ datasourceUrl: url });
test('organizasyon ayrımı, yetki, kayıtlar ve eşzamanlı tahsilat', async () => {
  const suffix = crypto.randomUUID();
  const user = await db.user.create({ data: { email: `${suffix}@example.invalid`, name: 'Test', emailVerifiedAt: new Date() } });
  const api = management(db, async () => ({ userId: user.id }));
  const organization = await api.createOrganization('Test şirketi', 'COMPANY');
  const site = await api.createSite(organization.id, 'Yetkili site');
  await db.organizationMembership.update({ where: { organizationId_userId: { organizationId: organization.id, userId: user.id } }, data: { role: 'MANAGER' } });
  const other = await db.site.create({ data: { name: 'Başka organizasyon' } });
  try {
    await assert.rejects(management(db, async () => null).dashboard(site.id), /UNAUTHENTICATED/);
    await assert.rejects(api.dashboard(other.id), /FORBIDDEN/);
    assert.equal((await api.portfolio(organization.id)).sites[0].id, site.id);
    await assert.rejects(management(db, async () => ({ userId: 'outsider' })).portfolio(organization.id), /FORBIDDEN/);
    const block = await api.createBlock(site.id, 'A');
    const unit = await api.createUnit(site.id, block.id, '1');
    await assert.rejects(db.unit.create({ data: { siteId: other.id, blockId: block.id, number: '2' } }));
    await api.recordOccupant(site.id, unit.id, 'Örnek Malik', 'OWNER', new Date('2026-10-01'));
    await api.recordOccupant(site.id, unit.id, 'Örnek Kiracı', 'TENANT', new Date('2026-10-01'));
    await assert.rejects(api.createCharge(site.id, unit.id, '2026-13', 10000, new Date()), /INVALID_CHARGE/);
    await assert.rejects(management(db, async () => ({ userId: 'forged-user' })).createCharge(site.id, unit.id, '2026-10', 10000, new Date()), /FORBIDDEN/);
    const charge = await api.createCharge(site.id, unit.id, '2026-10', 10000, new Date('2026-10-01'));
    await assert.rejects(api.createCharge(site.id, unit.id, '2026-10', 10000, new Date()));
    const results = await Promise.allSettled([api.collect(site.id, charge.id, 6000, 'one'), api.collect(site.id, charge.id, 6000, 'two')]);
    assert.equal(results.filter(r => r.status === 'fulfilled').length, 1);
    assert.match(String((results.find(r => r.status === 'rejected') as PromiseRejectedResult).reason), /OVERPAYMENT/);
    const receipt = (results.find(r => r.status === 'fulfilled') as PromiseFulfilledResult<{id:string;idempotencyKey:string}>).value;
    assert.equal((await api.collect(site.id, charge.id, 6000, receipt.idempotencyKey)).id, receipt.id);
    await assert.rejects(api.collect(site.id, charge.id, 1, receipt.idempotencyKey), /IDEMPOTENCY_CONFLICT/);
    await db.membership.create({ data: { siteId: other.id, userId: user.id, role: 'RESIDENT' } });
    await assert.rejects(api.createBlock(other.id, 'X'), /FORBIDDEN/);
    await assert.rejects(api.createCharge(other.id, unit.id, '2026-11', 100, new Date()), /FORBIDDEN/);
    const retries = await Promise.all([api.collect(site.id, charge.id, 4000, 'final'), api.collect(site.id, charge.id, 4000, 'final')]);
    assert.equal(retries[0].id, retries[1].id);
    const data = await api.dashboard(site.id);
    assert.equal(data.units[0].occupants.length, 2);
    assert.equal(data.charges[0].payments.reduce((sum, p) => sum + p.amountKurus, 0), 10000);
  } finally {
    // Only records belonging to this unique fixture are removed.
    await db.payment.deleteMany({ where: { siteId: site.id } });
    await db.charge.deleteMany({ where: { siteId: site.id } });
    await db.occupancy.deleteMany({ where: { siteId: site.id } });
    await db.unit.deleteMany({ where: { siteId: site.id } });
    await db.block.deleteMany({ where: { siteId: site.id } });
    await db.membership.deleteMany({ where: { userId: user.id } });
    await db.site.deleteMany({ where: { id: { in: [site.id, other.id] } } });
    await db.organizationMembership.deleteMany({ where: { organizationId: organization.id } });
    await db.organization.delete({ where: { id: organization.id } });
    await db.user.delete({ where: { id: user.id } });
    await db.$disconnect();
  }
});
