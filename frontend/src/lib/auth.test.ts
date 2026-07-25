import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  signToken,
  verifyToken,
  createSessionToken,
  verifyPassword,
  checkRateLimit,
  isAuthenticated,
  setSessionCookie,
  clearSessionCookie,
  SESSION_COOKIE_NAME,
} from './auth';

const TEST_SECRET = 'test_secret_key_for_hmac_signing_unit_tests_only';

describe('signToken / verifyToken', () => {
  it('round-trips a valid token', () => {
    const payload = { exp: Math.floor(Date.now() / 1000) + 3600 };
    const token = signToken(payload, TEST_SECRET);
    expect(verifyToken(token, TEST_SECRET)).toBe(true);
  });

  it('rejects an expired token', () => {
    const payload = { exp: Math.floor(Date.now() / 1000) - 100 };
    const token = signToken(payload, TEST_SECRET);
    expect(verifyToken(token, TEST_SECRET)).toBe(false);
  });

  it('rejects a token signed with a different secret', () => {
    const payload = { exp: Math.floor(Date.now() / 1000) + 3600 };
    const token = signToken(payload, TEST_SECRET);
    expect(verifyToken(token, 'wrong_secret')).toBe(false);
  });

  it('rejects a tampered payload', () => {
    const payload = { exp: Math.floor(Date.now() / 1000) + 3600 };
    const token = signToken(payload, TEST_SECRET);
    const [payloadB64] = token.split('.');
    const tampered = Buffer.from(JSON.stringify({ exp: 1 })).toString('base64url');
    const tamperedToken = `${tampered}.${token.split('.')[1]}`;
    expect(payloadB64).not.toBe(tampered);
    expect(verifyToken(tamperedToken, TEST_SECRET)).toBe(false);
  });

  it('rejects a malformed token (wrong number of parts)', () => {
    expect(verifyToken('just_one_part', TEST_SECRET)).toBe(false);
    expect(verifyToken('a.b.c', TEST_SECRET)).toBe(false);
    expect(verifyToken('', TEST_SECRET)).toBe(false);
  });

  it('rejects a token with a payload that is not valid JSON', () => {
    const fakePayloadB64 = Buffer.from('not_json').toString('base64url');
    const sig = (() => {
      const { createHmac } = require('node:crypto');
      return createHmac('sha256', TEST_SECRET).update(fakePayloadB64).digest('base64url');
    })();
    const token = `${fakePayloadB64}.${sig}`;
    expect(verifyToken(token, TEST_SECRET)).toBe(false);
  });

  it('rejects a token with a non-number exp', () => {
    const payloadB64 = Buffer.from(JSON.stringify({ exp: 'not_a_number' })).toString('base64url');
    const { createHmac } = require('node:crypto');
    const sig = createHmac('sha256', TEST_SECRET).update(payloadB64).digest('base64url');
    const token = `${payloadB64}.${sig}`;
    expect(verifyToken(token, TEST_SECRET)).toBe(false);
  });

  it('rejects a token without exp field', () => {
    const payloadB64 = Buffer.from(JSON.stringify({ foo: 'bar' })).toString('base64url');
    const { createHmac } = require('node:crypto');
    const sig = createHmac('sha256', TEST_SECRET).update(payloadB64).digest('base64url');
    const token = `${payloadB64}.${sig}`;
    expect(verifyToken(token, TEST_SECRET)).toBe(false);
  });
});

describe('createSessionToken', () => {
  it('produces a verifiable token', () => {
    const token = createSessionToken(TEST_SECRET);
    expect(verifyToken(token, TEST_SECRET)).toBe(true);
  });
});

describe('verifyPassword', () => {
  beforeEach(() => {
    vi.stubEnv('ADMIN_PASSWORD', 'mypassword123');
  });

  it('returns true for correct password', () => {
    expect(verifyPassword('mypassword123')).toBe(true);
  });

  it('returns false for wrong password', () => {
    expect(verifyPassword('wrong')).toBe(false);
  });

  it('returns false when ADMIN_PASSWORD is not set', () => {
    vi.stubEnv('ADMIN_PASSWORD', '');
    expect(verifyPassword('anything')).toBe(false);
  });
});

describe('checkRateLimit', () => {
  const testIp = 'test-ip-rate-limit';

  it('allows up to 5 attempts', () => {
    for (let i = 0; i < 5; i++) {
      const result = checkRateLimit(`${testIp}-a`);
      expect(result.allowed).toBe(true);
      expect(result.retryAfter).toBe(0);
    }
  });

  it('blocks the 6th attempt', () => {
    const ip = `${testIp}-b`;
    for (let i = 0; i < 5; i++) {
      checkRateLimit(ip);
    }
    const result = checkRateLimit(ip);
    expect(result.allowed).toBe(false);
    expect(result.retryAfter).toBeGreaterThan(0);
  });

  it('reports a positive retryAfter when blocked', () => {
    const ip = `${testIp}-c`;
    for (let i = 0; i < 5; i++) {
      checkRateLimit(ip);
    }
    const blocked = checkRateLimit(ip);
    expect(blocked.allowed).toBe(false);
    expect(blocked.retryAfter).toBeGreaterThanOrEqual(1);
    expect(blocked.retryAfter).toBeLessThanOrEqual(60);
  });

  it('isolates rate limits per IP', () => {
    const ip1 = `${testIp}-d1`;
    const ip2 = `${testIp}-d2`;
    for (let i = 0; i < 5; i++) {
      checkRateLimit(ip1);
    }
    const blocked = checkRateLimit(ip1);
    const allowed = checkRateLimit(ip2);
    expect(blocked.allowed).toBe(false);
    expect(allowed.allowed).toBe(true);
  });
});

describe('isAuthenticated (cookie mock)', () => {
  it('returns true when cookie has a valid token', () => {
    const token = createSessionToken(TEST_SECRET);
    const cookies = {
      get: (_key: string) => ({ value: token }),
    };
    expect(isAuthenticated(cookies as any, TEST_SECRET)).toBe(true);
  });

  it('returns false when cookie is absent', () => {
    const cookies = { get: (_key: string) => undefined };
    expect(isAuthenticated(cookies as any, TEST_SECRET)).toBe(false);
  });

  it('returns false when cookie has an invalid token', () => {
    const cookies = { get: (_key: string) => ({ value: 'invalid.token' }) };
    expect(isAuthenticated(cookies as any, TEST_SECRET)).toBe(false);
  });
});

describe('setSessionCookie / clearSessionCookie', () => {
  it('setSessionCookie calls cookies.set with httpOnly, secure, sameSite=strict', () => {
    const setCalls: Array<{ key: string; value: string; options: Record<string, unknown> }> = [];
    const cookies = {
      set: (key: string, value: string, options?: Record<string, unknown>) => {
        setCalls.push({ key, value, options: options ?? {} });
      },
      delete: (_key: string, _options?: Record<string, unknown>) => {},
    };
    const token = 'some_token';
    setSessionCookie(cookies as any, token);
    expect(setCalls).toHaveLength(1);
    expect(setCalls[0].key).toBe(SESSION_COOKIE_NAME);
    expect(setCalls[0].value).toBe(token);
    expect(setCalls[0].options.httpOnly).toBe(true);
    expect(setCalls[0].options.secure).toBe(true);
    expect(setCalls[0].options.sameSite).toBe('strict');
    expect(setCalls[0].options.path).toBe('/');
    expect(setCalls[0].options.maxAge).toBeGreaterThan(0);
  });

  it('clearSessionCookie calls cookies.delete with path', () => {
    const deleteCalls: Array<{ key: string; options: Record<string, unknown> }> = [];
    const cookies = {
      set: (_key: string, _value: string, _options?: Record<string, unknown>) => {},
      delete: (key: string, options?: Record<string, unknown>) => {
        deleteCalls.push({ key, options: options ?? {} });
      },
    };
    clearSessionCookie(cookies as any);
    expect(deleteCalls).toHaveLength(1);
    expect(deleteCalls[0].key).toBe(SESSION_COOKIE_NAME);
    expect(deleteCalls[0].options.path).toBe('/');
  });
});
