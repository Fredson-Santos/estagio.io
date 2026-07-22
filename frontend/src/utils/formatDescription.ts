/**
 * Formata descrições brutas de vagas (com HTML codificado, entidades &nbsp;, títulos grudados e listas separadas por ponto-e-vírgula)
 * em um HTML limpo, estruturado e com tipografia legível.
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

  // 1. Decodificar entidades HTML
  let text = unescapeHtml(rawText);

  // 2. Substituir tags HTML de quebra por quebras de linha
  text = text.replace(/<br\s*\/?>/gi, '\n');
  text = text.replace(/<\/(p|div|li|h1|h2|h3|h4|h5|h6|tr)>/gi, '\n');
  text = text.replace(/<[^>]+>/g, ''); // Remove outras tags sobressalentes

  // 3. Remover títulos duplicados grudados (ex: "Requisitos e qualificaçõesRequisitos e qualificações")
  text = text.replace(/(Responsabilidades e atribuições){2,}/gi, 'Responsabilidades e atribuições');
  text = text.replace(/(Requisitos e qualificações){2,}/gi, 'Requisitos e qualificações');
  text = text.replace(/(Informações adicionais){2,}/gi, 'Informações adicionais');

  // 4. Inserir quebras de linha antes de títulos conhecidos quando grudados ao texto anterior
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

  // Ordena por tamanho decrescente para priorizar termos mais específicos ("Responsabilidades e atribuições" antes de "Responsabilidades")
  sectionHeaders.sort((a, b) => b.length - a.length);

  sectionHeaders.forEach((header) => {
    // Procura o cabeçalho se grudado no caractere anterior sem espaço
    const regexBefore = new RegExp(`([^\\n])\\s*(${header})`, 'gi');
    text = text.replace(regexBefore, '$1\n\n$2');

    // Procura o texto grudado DEPOIS do cabeçalho sem espaço (ex: "Responsabilidades e atribuiçõesApoiar")
    const regexAfter = new RegExp(`(${header})\\s*([A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ])`, 'gi');
    text = text.replace(regexAfter, '$1\n$2');
  });

  // 5. Quebrar itens de lista separados por ponto-e-vírgula em novas linhas se começarem com letra maiúscula
  // Ex: "cotação de produtos;Atuar ativamente...;Auxiliar..." -> "cotação de produtos;\n• Atuar ativamente...\n• Auxiliar..."
  text = text.replace(/;\s*([A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ])/g, ';\n• $1');

  // 6. Normalizar marcadores de tópicos (•, -, *, 1.) em novas linhas
  text = text.replace(/([^\n])\s*([•\-\*])\s*/g, '$1\n• ');

  // 7. Processar linha por linha para construir o HTML limpo
  const lines = text.split('\n').map((l) => l.trim()).filter((l) => l.length > 0);

  let htmlResult = '';
  let inList = false;

  lines.forEach((line) => {
    // Verifica se a linha é um título de seção
    const isHeader = sectionHeaders.some((h) => line.toLowerCase() === h.toLowerCase() || line.toLowerCase().startsWith(h.toLowerCase() + ':'));

    if (isHeader) {
      if (inList) {
        htmlResult += '</ul>';
        inList = false;
      }
      htmlResult += `<h3 class="text-headline-sm font-bold text-on-surface mt-6 mb-3 pt-2 border-t border-outline-variant/30">${line}</h3>`;
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
