import { ZodError } from 'zod';
export function invalidDashboardRequest(error:unknown){return error instanceof ZodError||(error instanceof Error&&['INVALID_FILTER','FORBIDDEN','EMAIL_UNVERIFIED','UNAUTHENTICATED'].includes(error.message));}
