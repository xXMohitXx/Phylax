import React from 'react';
import { Terminal } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
  highlightedLines?: number[];
}

export function CodeBlock({ code, language = 'python', title, highlightedLines = [] }: CodeBlockProps) {
  const lines = code.trim().split(/\r?\n/);

  return (
    <div className="rounded-xl overflow-hidden border border-black/30 bg-code-bg shadow-2xl backdrop-blur-sm">

      <div className="flex items-center justify-between px-4 py-3 border-b border-black/40 bg-coffee-bean">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-porcelain/20"></div>
            <div className="w-3 h-3 rounded-full bg-porcelain/20"></div>
            <div className="w-3 h-3 rounded-full bg-porcelain/20"></div>
          </div>
          {title && <span className="ml-2 text-xs font-mono text-porcelain/60">{title}</span>}
        </div>

        {language && (
          <div className="flex items-center gap-1.5 text-xs font-mono text-porcelain/40">
            {language === 'bash' ? <Terminal className="w-3.5 h-3.5" /> : null}
            <span>{language}</span>
          </div>
        )}
      </div>

      <div className="p-3 md:p-4 overflow-x-auto text-xs md:text-sm font-mono leading-relaxed text-porcelain">
        {lines.map((line, i) => {
          const isHighlighted = highlightedLines.includes(i + 1);
          // Escape HTML characters to prevent < and > (e.g., in type hints -> or imports) being treated as actual HTML tags.
          const escapedLine = line
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

          // Extremely basic static syntax highlighting for python/yaml look
          let formattedLine = escapedLine
            .replace(/(&quot;.*?&quot;|'.*?')/g, '<span class="text-beige">$1</span>') // Strings (now handling &quot; from escaping, but strings with single or double quotes)
            .replace(/(".*?"|'.*?')/g, '<span class="text-beige">$1</span>') // Strings (covering unescaped quotes just in case)
            .replace(/(@\w+)/g, '<span class="text-lime-cream">$1</span>') // Decorators
            .replace(/\b(from|import|def|return|with|as)\b:?/g, '<span class="text-porcelain/60">$1</span>') // Keywords
            .replace(/\b(must_include|must_not_include|provider|dataset|cases|input|expectations|max_latency_ms)\b:/g, '<span class="text-lime-cream">$1:</span>') // Yaml keys
            .replace(/\b(phylax|trace|expect)\b/g, '<span class="text-porcelain/80 font-bold">$1</span>'); // Phylax specific

          return (
            <div
              key={i}
              className={`px-4 -mx-4 flex gap-4 ${isHighlighted ? 'bg-lime-cream/10 border-l-2 border-lime-cream' : 'border-l-2 border-transparent'}`}
            >
              <span className="select-none text-porcelain/30 font-mono w-4 text-right flex-shrink-0">
                {i + 1}
              </span>
              <span className="whitespace-pre" dangerouslySetInnerHTML={{ __html: formattedLine || ' ' }} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
