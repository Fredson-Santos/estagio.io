import { createHmac, timingSafeEqual } from 'node:crypto';

const SESSION_COOKIE_NAME = 'admin_session';
const SESSION_MAX_AGE_SECONDS = 7 * 24 * 60 * 60;
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX_ATTEMPTS = 5;

export function getAdminPassword(): string {
  if (typeof process !== 'undefined' && process.env && process.env.ADMIN_PASSWORD) {
    return process.env.ADMIN_PASSWORD;
  }
  return import.meta.env.ADMIN_PASSWORD || '';
}

export function getAdminSecret(): string {
  if (typeof process !== 'undefined' && process.env && process.env.ADMIN_SECRET) {
    return process.env.ADMIN_SECRET;
  }
  return import.meta.env.ADMIN_SECRET || '';
}

function toBase64Url(input: Buffer | string): string {
  return Buffer.from(input).toString('base64url');
}

function fromBase64Url(input: string): Buffer {
  return Buffer.from(input, 'base64url');
}

export function signToken(payload: object, secret: string): string {
  const json = JSON.stringify(payload);
  const payloadB64 = toBase64Url(json);
  const signature = createHmac('sha256', secret).update(payloadB64).digest();
  const signatureB64 = signature.toString('base64url');
  return `${payloadB64}.${signatureB64}`;
}

export function createSessionToken(secret: string): string {
  const exp = Math.floor(Date.now() / 1000) + SESSION_MAX_AGE_SECONDS;
  return signToken({ exp }, secret);
}

export function verifyToken(token: string, secret: string): boolean {
  const parts = token.split('.');
  if (parts.length !== 2) return false;

  const [payloadB64, signatureB64] = parts;
  if (!payloadB64 || !signatureB64) return false;

  const expectedSignature = createHmac('sha256', secret).update(payloadB64).digest();
  const providedSignature = fromBase64Url(signatureB64);

  if (expectedSignature.length !== providedSignature.length) return false;

  if (!timingSafeEqual(expectedSignature, providedSignature)) return false;

  let payload: { exp?: number };
  try {
    payload = JSON.parse(fromBase64Url(payloadB64).toString('utf8'));
  } catch {
    return false;
  }

  if (typeof payload.exp !== 'number') return false;
  if (payload.exp <= Math.floor(Date.now() / 1000)) return false;

  return true;
}

export function isAuthenticated(cookies: { get: (key: string) => { value: string } | undefined }, secret: string): boolean {
  const cookie = cookies.get(SESSION_COOKIE_NAME);
  if (!cookie || !cookie.value) return false;
  return verifyToken(cookie.value, secret);
}

export function setSessionCookie(cookies: { set: (key: string, value: string, options?: Record<string, unknown>) => void }, token: string): void {
  cookies.set(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    path: '/',
    maxAge: SESSION_MAX_AGE_SECONDS,
  });
}

export function clearSessionCookie(cookies: { delete: (key: string, options?: Record<string, unknown>) => void }): void {
  cookies.delete(SESSION_COOKIE_NAME, {
    path: '/',
  });
}

type CookieGetter = { get: (key: string) => { value: string } | undefined };
type CookieSetter = { set: (key: string, value: string, options?: Record<string, unknown>) => void };
type CookieDeleter = { delete: (key: string, options?: Record<string, unknown>) => void };

export function verifyPassword(password: string): boolean {
  const adminPassword = getAdminPassword();
  if (!adminPassword) return false;
  const a = Buffer.from(password);
  const b = Buffer.from(adminPassword);
  if (a.length !== b.length) {
    return timingSafeEqual(b, b) ? false : false;
  }
  return timingSafeEqual(a, b);
}

const rateLimitMap = new Map<string, number[]>();

export function checkRateLimit(ip: string): { allowed: boolean; retryAfter: number } {
  const now = Date.now();
  const windowStart = now - RATE_LIMIT_WINDOW_MS;

  const existing = rateLimitMap.get(ip) ?? [];
  const recent = existing.filter((timestamp) => timestamp > windowStart);

  if (recent.length >= RATE_LIMIT_MAX_ATTEMPTS) {
    const oldestRecent = recent[0];
    const retryAfter = Math.ceil((oldestRecent + RATE_LIMIT_WINDOW_MS - now) / 1000);
    rateLimitMap.set(ip, recent);
    return { allowed: false, retryAfter: Math.max(1, retryAfter) };
  }

  recent.push(now);
  rateLimitMap.set(ip, recent);
  return { allowed: true, retryAfter: 0 };
}

export { SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS, RATE_LIMIT_WINDOW_MS, RATE_LIMIT_MAX_ATTEMPTS };
