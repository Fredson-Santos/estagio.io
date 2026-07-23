import DOMPurify from 'isomorphic-dompurify';

const ALLOWED_TAGS = [
  'p', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'strong', 'em', 'b', 'i', 'br', 'span', 'div', 'a',
];

const ALLOWED_ATTR = ['href', 'target', 'rel', 'class'];

export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):)/i,
  });
}
