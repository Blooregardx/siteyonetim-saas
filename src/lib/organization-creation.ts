import { OrganizationKind, Prisma } from '@prisma/client';
import { audit, organizationAccess } from './security';

// Shared transaction helpers: callers authenticate/verify the actor before entering.
export async function createOrganizationIn(tx: Prisma.TransactionClient, userId: string, name: string, kind: OrganizationKind) {
 const organization = await tx.organization.create({data:{name:name.trim(),kind,memberships:{create:{userId,role:'ADMIN'}}}});
 await audit(tx,userId,'ORGANIZATION_CREATE',organization.id,organization.id);
 return organization;
}
export async function createSiteIn(tx: Prisma.TransactionClient, userId: string, organizationId: string, input: {name:string;address?:string;description?:string}) {
 await organizationAccess(tx,userId,organizationId);
 const site = await tx.site.create({data:{organizationId,...input,name:input.name.trim()}});
 await audit(tx,userId,'SITE_CREATE',site.id,organizationId,site.id);
 return site;
}
