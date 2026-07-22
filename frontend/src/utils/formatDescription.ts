/**
 * Formata descrições brutas de vagas (com HTML codificado, entidades &nbsp;, títulos grudados, 
 * frases coladas sem espaço/quebra) em um HTML estruturado, com títulos de seções, parágrafos e tópicos (bullet points).
 */

function unescapeHtml(text: string): string {
  return text
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&rsquo;/gi, "'")
    .replace(/&ldquo;/gi, '"')
    .replace(/&rdquo;/gi, '"');
}

export function formatJobDescription(rawText: string): string {
  if (!rawText) return '';

  let text = unescapeHtml(rawText);

  // 1. Se contiver tags de parágrafo/lista ricas do HTML original, sanitiza e limpa apenas quebras
  const hasRichHtml = /<(p|ul|ol|li|h1|h2|h3)\b/i.test(text);

  if (!hasRichHtml) {
    // Substituir tags soltas de quebra de linha por \n
    text = text.replace(/<br\s*\/?>/gi, '\n');
    text = text.replace(/<\/(p|div|li|h1|h2|h3|h4|h5|h6|tr)>/gi, '\n');
    text = text.replace(/<[^>]+>/g, '');

    // 2. Limpar títulos duplicados grudados (ex: "Requisitos e qualificaçõesRequisitos e qualificações")
    text = text.replace(/(Responsabilidades e atribuições){2,}/gi, 'Responsabilidades e atribuições');
    text = text.replace(/(Requisitos e qualificações){2,}/gi, 'Requisitos e qualificações');
    text = text.replace(/(Informações adicionais){2,}/gi, 'Informações adicionais');

    // 3. Destacar cabeçalhos conhecidos
    const sectionHeaders = [
      'Responsabilidades e atribuições',
      'Responsabilidades',
      'Atividades',
      'Principais atividades',
      'Principais responsabilidades',
      'Requisitos e qualificações',
      'Requisitos',
      'Pré-requisitos',
      'O que buscamos',
      'O que você precisa ter',
      'Perfil desejado',
      'Diferenciais',
      'Desejável',
      'Informações adicionais',
      'Benefícios',
      'O que oferecemos',
      'Nossos benefícios',
      'Sobre a empresa',
      'Sobre nós',
      'Quem somos',
    ];
    sectionHeaders.sort((a, b) => b.length - a.length);

    sectionHeaders.forEach((header) => {
      const regexBefore = new RegExp(`([^\\n])\\s*(${header})`, 'gi');
      text = text.replace(regexBefore, '$1\n\n$2');

      const regexAfter = new RegExp(`(${header})\\s*([A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ])`, 'gi');
      text = text.replace(regexAfter, '$1\n\n$2');
    });

    // 4. Separar frases grudadas onde uma minúscula/pontuação é colada em uma maiúscula (ex: NegóciosAplicar -> Negócios\n• Aplicar)
    text = text.replace(/([a-z0-9à-ú\.\!\?\:\)\;])([A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ])/g, '$1\n• $2');

    // 5. Normalizar marcadores de tópicos
    text = text.replace(/;\s*([A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ])/g, ';\n• $1');
    text = text.replace(/([^\n])\s*([•\-\*])\s*/g, '$1\n• ');
  }

  // 6. Dividir em linhas para gerar HTML bem estruturado
  const lines = text.split('\n').map((l) => l.trim()).filter((l) => l.length > 0);

  const sectionHeadersLower = [
    'responsabilidades e atribuições', 'responsabilidades', 'atividades', 'principais atividades', 'principais responsabilidades',
    'requisitos e qualificações', 'requisitos', 'pré-requisitos', 'o que buscamos', 'o que você precisa ter', 'perfil desejado',
    'diferenciais', 'desejável', 'informações adicionais', 'benefícios', 'o que oferecemos', 'nossos benefícios', 'sobre a empresa', 'sobre nós', 'quem somos'
  ];

  let htmlResult = '';
  let inList = false;

  lines.forEach((line) => {
    const cleanLineLower = line.toLowerCase().replace(/^[•\-\*]\s*/, '').trim();
    const isHeader = sectionHeadersLower.some((h) => cleanLineLower === h || cleanLineLower.startsWith(h + ':'));

    if (isHeader) {
      if (inList) {
        htmlResult += '</ul>';
        inList = false;
      }
      const headerTitle = line.replace(/^[•\-\*]\s*/, '').trim();
      htmlResult += `<h3 class="text-headline-sm font-bold text-on-surface mt-6 mb-3 pt-3 border-t border-outline-variant/30">${headerTitle}</h3>`;
    } else if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
      if (!inList) {
        htmlResult += '<ul class="list-disc pl-5 my-3 space-y-1.5 text-on-surface-variant font-body-md">';
        inList = true;
      }
      const itemContent = line.replace(/^[•\-\*]\s*/, '').replace(/;$/, '');
      htmlResult += `<li class="leading-relaxed">${itemContent}</li>`;
    } else {
      if (inList) {
        htmlResult += '</ul>';
        inList = false;
      }
      htmlResult += `<p class="mb-3 text-on-surface-variant font-body-md leading-relaxed">${line}</p>`;
    }
  });

  if (inList) {
    htmlResult += '</ul>';
  }

  return htmlResult;
}
