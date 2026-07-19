import React, { useState, useRef, useEffect } from 'react';

function CustomSelect({ 
  label, 
  options 
}: { 
  label: string; 
  options: { value: string; label: string }[] 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState('');
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedLabel = options.find(o => o.value === selected)?.label || label;
  const isActive = selected !== '';

  return (
    <div className="select-wrapper custom-select-container" ref={wrapperRef} style={{ position: 'relative' }}>
      <button 
        type="button" 
        className={`custom-select-btn ${isActive ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          appearance: 'none',
          height: '36px',
          padding: '0 14px',
          fontSize: '14px',
          borderRadius: '9999px',
          color: isActive ? 'var(--c-foreground)' : 'var(--c-muted-foreground)',
          borderColor: isActive ? 'var(--c-primary)' : 'var(--c-border)',
          borderWidth: '1px',
          borderStyle: 'solid',
          background: 'var(--c-card)',
          cursor: 'pointer',
          minWidth: '120px',
          gap: '8px'
        }}
      >
        <span>{selectedLabel}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transition: 'transform 0.2s', transform: isOpen ? 'rotate(180deg)' : 'none' }}>
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      {isOpen && (
        <div className="custom-select-menu" style={{
          position: 'absolute',
          top: 'calc(100% + 4px)',
          left: 0,
          minWidth: '100%',
          backgroundColor: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: '12px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          zIndex: 50,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          padding: '4px'
        }}>
          {options.map(opt => (
            <div 
              key={opt.value}
              className={`custom-select-option ${selected === opt.value ? 'selected' : ''}`}
              onClick={() => {
                setSelected(selected === opt.value ? '' : opt.value);
                setIsOpen(false);
              }}
              style={{
                padding: '8px 12px',
                fontSize: '14px',
                color: selected === opt.value ? '#ffffff' : 'var(--c-foreground)',
                backgroundColor: selected === opt.value ? 'var(--c-primary)' : 'transparent',
                cursor: 'pointer',
                borderRadius: '8px',
                transition: 'background-color 0.15s'
              }}
              onMouseEnter={(e) => {
                if (selected !== opt.value) e.currentTarget.style.backgroundColor = 'var(--c-secondary)';
              }}
              onMouseLeave={(e) => {
                if (selected !== opt.value) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function FilterBar() {
  const [filtersOpen, setFiltersOpen] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  return (
    <div className="filter-bar-wrapper">
      <button
        type="button"
        className={`filter-toggle-btn ${filtersOpen ? 'active' : ''}`}
        onClick={() => setFiltersOpen(!filtersOpen)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          height: '36px',
          padding: '0 16px',
          fontSize: '14px',
          fontWeight: 500,
          borderRadius: '9999px',
          border: `1px solid ${filtersOpen ? 'var(--c-primary)' : 'var(--c-border)'}`,
          background: filtersOpen ? 'var(--c-primary)' : 'var(--c-card)',
          color: filtersOpen ? 'var(--c-primary-foreground)' : 'var(--c-muted-foreground)',
          cursor: 'pointer',
          transition: 'all 0.2s',
          marginBottom: filtersOpen ? '12px' : '0',
          fontFamily: 'inherit',
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="4" y1="21" x2="4" y2="14"></line>
          <line x1="4" y1="10" x2="4" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12" y2="3"></line>
          <line x1="20" y1="21" x2="20" y2="16"></line>
          <line x1="20" y1="12" x2="20" y2="3"></line>
          <line x1="1" y1="14" x2="7" y2="14"></line>
          <line x1="9" y1="8" x2="15" y2="8"></line>
          <line x1="17" y1="16" x2="23" y2="16"></line>
        </svg>
        <span>filtrar</span>
        <svg 
          width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" 
          style={{ transition: 'transform 0.2s', transform: filtersOpen ? 'rotate(180deg)' : 'none' }}
        >
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      <div
        ref={contentRef}
        style={{
          overflow: filtersOpen ? 'visible' : 'hidden',
          transition: 'max-height 0.3s ease, opacity 0.2s ease',
          maxHeight: filtersOpen ? '300px' : '0',
          opacity: filtersOpen ? 1 : 0,
        }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          flexWrap: 'wrap',
        }}>
          <CustomSelect 
            label="modalidade" 
            options={[
              { value: 'presencial', label: 'Presencial' },
              { value: 'hibrido', label: 'Híbrido' },
              { value: 'remoto', label: 'Remoto' }
            ]} 
          />

          <span style={{ 
            width: '1px', 
            height: '20px', 
            backgroundColor: 'var(--c-border)', 
            margin: '0 4px',
            flexShrink: 0,
          }} />

          <CustomSelect 
            label="área" 
            options={[
              { value: 'ti', label: 'Tecnologia' },
              { value: 'mkt', label: 'Marketing' }
            ]} 
          />
          <CustomSelect 
            label="cidade" 
            options={[
              { value: 'sp', label: 'São Paulo' },
              { value: 'campinas', label: 'Campinas' }
            ]} 
          />
          <CustomSelect 
            label="fonte" 
            options={[
              { value: 'gupy', label: 'Gupy' },
              { value: 'ciee', label: 'CIEE' }
            ]} 
          />
        </div>
      </div>
    </div>
  );
}
