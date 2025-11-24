import React, { useEffect, useState } from 'react';

const AsciiCart: React.FC = () => {
  // Configuração responsiva: Desktop (6x8) vs Mobile (4x5)
  const [dimensions, setDimensions] = useState({ rows: 6, cols: 8 });
  
  useEffect(() => {
    const handleResize = () => {
      // Breakpoint sm do Tailwind é 640px
      if (window.innerWidth < 640) {
        setDimensions({ rows: 4, cols: 5 }); // Versão "nota menor" otimizada
      } else {
        setDimensions({ rows: 6, cols: 8 });
      }
    };

    handleResize(); // Checagem inicial
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const { rows: ROWS, cols: COLS } = dimensions;
  const TOTAL_ITEMS = ROWS * COLS;
  
  const [items, setItems] = useState<boolean[]>([]);
  const [mode, setMode] = useState<'SELLING' | 'RESTOCKING'>('SELLING');

  // Ajusta o array de items quando as dimensões mudam
  useEffect(() => {
    setItems(Array(TOTAL_ITEMS).fill(true));
  }, [TOTAL_ITEMS]);

  useEffect(() => {
    // Velocidade da simulação
    const interval = setInterval(() => {
      setItems(prev => {
        // Se o tamanho do array não bate com o esperado (durante resize), não atualiza
        if (prev.length !== TOTAL_ITEMS) return prev;

        const next = [...prev];
        
        // Identifica candidatos para a ação atual
        const candidates = next
          .map((val, idx) => ({ val, idx }))
          .filter(item => mode === 'SELLING' ? item.val === true : item.val === false)
          .map(item => item.idx);

        // Se não há mais candidatos, troca o modo
        if (candidates.length === 0) {
          setMode(prevMode => prevMode === 'SELLING' ? 'RESTOCKING' : 'SELLING');
          return next;
        }

        // Escolhe um aleatório para alterar
        const randomIndex = candidates[Math.floor(Math.random() * candidates.length)];
        next[randomIndex] = !next[randomIndex];
        
        return next;
      });
    }, 100); // Velocidade da atualização (ms)

    return () => clearInterval(interval);
  }, [mode, TOTAL_ITEMS]);

  // Renderiza o item: Cheio [##] ou Vazio [..]
  // Fallback seguro para undefined durante transições de estado
  const r = (i: number) => (items[i] !== undefined && items[i]) ? '[##]' : '[..]';

  // Gera uma linha da gôndola
  const getRow = (rowIdx: number) => {
    const start = rowIdx * COLS;
    // Prevenção de erro de índice
    if (start >= items.length && items.length > 0) return ""; 
    return Array.from({ length: COLS }).map((_, k) => r(start + k)).join(' ');
  };

  // Geração Dinâmica da Arte ASCII baseada em COLS e ROWS
  // Largura do conteúdo = (4 chars * COLS) + (1 char espaço * (COLS-1)) = 5 * COLS - 1
  const contentWidth = (COLS * 5) - 1;
  
  const borderLine = '_'.repeat(contentWidth + 2); // +2 para os espaços laterais dentro dos pipes
  const dividerLine = '-'.repeat(contentWidth + 2);
  
  // Cálculo dinâmico para os pés ficarem proporcionais
  // Para 8 cols (w=39), gap ideal ~23. Para 5 cols (w=24), gap ideal ~8.
  const gapSize = Math.max(2, contentWidth - 16);
  const feetGap = ' '.repeat(gapSize);

  let gondolaArt = `\n   ${borderLine}\n`;
  
  for (let i = 0; i < ROWS; i++) {
    gondolaArt += `  | ${getRow(i)} |\n`;
    if (i < ROWS - 1) {
      gondolaArt += `  |${dividerLine}|\n`;
    }
  }
  
  gondolaArt += `  |${borderLine}|\n`;
  gondolaArt += `      |  |${feetGap}|  |\n`;
  gondolaArt += `     _|  |_${feetGap}_|  |_`;

  return (
    <div className="font-mono text-[10px] xs:text-xs sm:text-sm leading-none text-zinc-800/90 whitespace-pre select-none text-center font-bold transition-all duration-300">
      {gondolaArt}
    </div>
  );
};

export default AsciiCart;