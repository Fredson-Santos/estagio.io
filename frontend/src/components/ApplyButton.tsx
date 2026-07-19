import React from 'react';

interface Props {
  jobId: string;
  sourceUrl: string;
}

export default function ApplyButton({ jobId, sourceUrl }: Props) {
  const handleApply = async () => {
    // Analytics interno
    try {
      // Endpoint que não existe ainda mas será útil pra fase 1.5
      console.log(`Log click for job: ${jobId}`);
    } catch (e) {
      console.error(e);
    }
    
    // Redireciona para fonte real
    window.open(sourceUrl, '_blank');
  };

  return (
    <button 
      onClick={handleApply}
      style={{
        backgroundColor: 'var(--c-primary)',
        color: 'var(--c-primary-foreground)',
        padding: '12px 24px',
        borderRadius: 'var(--radius)',
        fontSize: '16px',
        fontWeight: '600',
        border: 'none',
        cursor: 'pointer',
        transition: 'transform 0.1s ease',
      }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
      onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.98)'}
    >
      Candidatar-se agora
    </button>
  );
}
