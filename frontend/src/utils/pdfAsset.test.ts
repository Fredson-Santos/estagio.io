import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';

describe('PDF Download Asset (IA_no_dia_a_dia.pdf)', () => {
  const publicDir = path.join(process.cwd(), 'public');
  const originalPdfPath = path.join(publicDir, 'IA_no_dia_a_dia.pdf');
  const slugPdfPath = path.join(publicDir, 'ia-no-dia-a-dia.pdf');

  it('garante que o arquivo IA_no_dia_a_dia.pdf existe na pasta public', () => {
    expect(fs.existsSync(originalPdfPath)).toBe(true);
  });

  it('garante que o arquivo é um PDF válido começando com header %PDF-', () => {
    const buffer = Buffer.alloc(5);
    const fd = fs.openSync(originalPdfPath, 'r');
    fs.readSync(fd, buffer, 0, 5, 0);
    fs.closeSync(fd);

    expect(buffer.toString('utf-8')).toBe('%PDF-');
  });

  it('garante que o arquivo possui tamanho compatível e não está vazio', () => {
    const stats = fs.statSync(originalPdfPath);
    expect(stats.size).toBeGreaterThan(100_000); // ~600KB esperado
  });

  it('garante disponibilidade de alias com slug amigável (ia-no-dia-a-dia.pdf)', () => {
    expect(fs.existsSync(slugPdfPath)).toBe(true);
    const originalStats = fs.statSync(originalPdfPath);
    const slugStats = fs.statSync(slugPdfPath);
    expect(slugStats.size).toBe(originalStats.size);
  });
});
