import { defineMiddleware } from 'astro:middleware';
import { isAuthenticated, getAdminSecret } from './lib/auth';

export const onRequest = defineMiddleware((context, next) => {
  const { pathname } = context.url;

  if (!pathname.startsWith('/admin')) {
    return next();
  }

  if (pathname === '/admin/login' || pathname === '/admin/logout') {
    if (pathname === '/admin/login' && isAuthenticated(context.cookies, getAdminSecret())) {
      return context.redirect('/admin/dashboard', 302);
    }
    return next();
  }

  if (pathname === '/admin' || pathname === '/admin/') {
    return context.redirect('/admin/dashboard', 302);
  }

  if (!isAuthenticated(context.cookies, getAdminSecret())) {
    if (pathname.startsWith('/admin/api/')) {
      return new Response(JSON.stringify({ detail: 'Não autorizado' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return context.redirect('/admin/login', 302);
  }

  return next();
});
