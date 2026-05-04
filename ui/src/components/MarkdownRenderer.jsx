import React, { useState, useEffect, useRef } from 'react';

/**
 * A sophisticated Markdown renderer with GPT-style typing animation.
 * Handles paragraphs, bold text, bullet points, and tables.
 */
const MarkdownRenderer = ({ content, animate = false }) => {
  const [displayedText, setDisplayedText] = useState(animate ? "" : content);
  const [isTyping, setIsTyping] = useState(animate);
  const contentRef = useRef(content);

  useEffect(() => {
    contentRef.current = content;
    if (!animate || !content) {
      setDisplayedText(content);
      return;
    }
    
    setDisplayedText("");
    setIsTyping(true);
    let index = 0;
    
    // Faster typing for longer texts to keep user engaged
    const speed = content.length > 500 ? 5 : 10; 
    
    const interval = setInterval(() => {
      const currentContent = contentRef.current;
      setDisplayedText((prev) => currentContent.slice(0, index + 2));
      index += 2;
      
      if (index >= currentContent.length) {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, speed);
    
    return () => clearInterval(interval);
  }, [content, animate]);

  const textToRender = displayedText || "";
  if (!textToRender && !isTyping) return null;

  // Parser Logic
  const lines = textToRender.split('\n');
  const blocks = [];
  let currentTable = null;

  lines.forEach((line) => {
    const trimmed = line.trim();
    
    // 1. Table Detection (| Cell | Cell |)
    if (trimmed.startsWith('|') && trimmed.includes('|')) {
      // Skip divider lines (|---|---|)
      if (trimmed.match(/^\|[\s-|-]*\|$/)) return;

      const cells = trimmed
        .split('|')
        .filter((c, idx, arr) => (idx > 0 && idx < arr.length - 1))
        .map(c => c.trim());

      if (!currentTable) {
        currentTable = { header: cells, rows: [] };
      } else {
        currentTable.rows.push(cells);
      }
      return;
    } else if (currentTable) {
      // End of table
      blocks.push({ type: 'table', data: currentTable });
      currentTable = null;
    }

    // 2. Empty Lines
    if (!trimmed) {
      blocks.push({ type: 'spacer' });
      return;
    }

    // 3. Bullet points (* or -)
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
      blocks.push({ type: 'bullet', content: trimmed.substring(2) });
    } 
    // 4. Numbered lists (1. )
    else if (trimmed.match(/^\d+\.\s/)) {
      blocks.push({ type: 'bullet', content: trimmed.replace(/^\d+\.\s/, ''), prefix: trimmed.match(/^\d+\./)[0] });
    }
    // 5. Standard Paragraph
    else {
      blocks.push({ type: 'paragraph', content: trimmed });
    }
  });

  // Push last table if exists
  if (currentTable) blocks.push({ type: 'table', data: currentTable });

  // Inline formatting (Bold only for simplicity and stability)
  const formatText = (text) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-bold text-slate-900 dark:text-slate-100">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className="relative">
      <div className="space-y-3 font-sans">
        {blocks.map((block, i) => {
          if (block.type === 'spacer') return <div key={i} className="h-2" />;
          
          if (block.type === 'bullet') {
            return (
              <div key={i} className="flex gap-3 pl-1 mb-1">
                <span className="text-primary font-bold min-w-[12px]">{block.prefix || "•"}</span>
                <span className="text-[13px] leading-relaxed text-slate-700 dark:text-slate-300">
                  {formatText(block.content)}
                </span>
              </div>
            );
          }

          if (block.type === 'table') {
            return (
              <div key={i} className="overflow-x-auto my-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <table className="w-full text-left text-[12px] border-collapse">
                  <thead className="bg-slate-50 dark:bg-slate-800/50">
                    <tr>
                      {block.data.header.map((h, j) => (
                        <th key={j} className="p-3 font-bold border-b border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {block.data.rows.map((row, j) => (
                      <tr key={j} className="border-b border-slate-100 dark:border-slate-800/50 last:border-none hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                        {row.map((cell, k) => (
                          <td key={k} className="p-3 text-slate-700 dark:text-slate-300">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          }

          return (
            <p key={i} className="text-[13px] leading-relaxed text-slate-700 dark:text-slate-300">
              {formatText(block.content)}
            </p>
          );
        })}
      </div>
      
      {/* Typing Cursor */}
      {isTyping && (
        <span className="inline-block w-1.5 h-4 ml-1 bg-primary/60 animate-pulse align-middle"></span>
      )}
    </div>
  );
};

export default MarkdownRenderer;
