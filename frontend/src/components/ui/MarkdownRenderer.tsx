import React from 'react';

/**
 * A robust Markdown renderer for AI-generated audit content.
 * Handles: Bold, Italic, Inline Code, Headings, Tables, Lists, Horizontal Rules, Emoji.
 */
export default function MarkdownRenderer({ content }: { content: string | null }) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // --- Horizontal Rule ---
    if (/^[-*]{3,}$/.test(trimmed)) {
      elements.push(<hr key={i} className="my-6 border-t border-indigo-500/20" />);
      i++;
      continue;
    }

    // --- Heading 3 ---
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h3 key={i} className="text-base font-bold text-white mt-6 mb-3 tracking-tight flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
          {parseInline(trimmed.slice(4))}
        </h3>
      );
      i++;
      continue;
    }

    // --- Heading 2 ---
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h2 key={i} className="text-lg font-black text-indigo-300 mt-8 mb-4 tracking-tight uppercase border-b border-indigo-500/20 pb-2">
          {parseInline(trimmed.slice(3))}
        </h2>
      );
      i++;
      continue;
    }

    // --- Heading 1 ---
    if (trimmed.startsWith('# ')) {
      elements.push(
        <h1 key={i} className="text-xl font-black text-white mt-6 mb-4 tracking-tight">
          {parseInline(trimmed.slice(2))}
        </h1>
      );
      i++;
      continue;
    }

    // --- Table ---
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }
      if (tableLines.length >= 2) {
        elements.push(renderTable(tableLines, elements.length));
      }
      continue;
    }

    // --- Ordered List ---
    if (/^\d+[\.\)]\s/.test(trimmed)) {
      const listItems: string[] = [];
      while (i < lines.length && /^\d+[\.\)]\s/.test(lines[i].trim())) {
        listItems.push(lines[i].trim().replace(/^\d+[\.\)]\s/, ''));
        i++;
      }
      elements.push(
        <ol key={`ol-${elements.length}`} className="my-3 space-y-2 pl-1">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex gap-3 text-sm leading-relaxed text-gray-300">
              <span className="text-indigo-500 font-bold shrink-0 font-mono text-xs mt-0.5">{idx + 1}.</span>
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // --- Unordered List ---
    if (/^[-*•]\s/.test(trimmed)) {
      const listItems: string[] = [];
      while (i < lines.length && /^[-*•]\s/.test(lines[i].trim())) {
        listItems.push(lines[i].trim().replace(/^[-*•]\s/, ''));
        i++;
      }
      elements.push(
        <ul key={`ul-${elements.length}`} className="my-3 space-y-2 pl-1">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex gap-3 text-sm leading-relaxed text-gray-300">
              <span className="text-indigo-500 font-bold shrink-0 mt-1">•</span>
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // --- Empty line ---
    if (trimmed === '') {
      elements.push(<div key={i} className="h-2" />);
      i++;
      continue;
    }

    // --- Default: Paragraph ---
    elements.push(
      <p key={i} className="text-gray-300 leading-relaxed text-sm my-1.5">
        {parseInline(trimmed)}
      </p>
    );
    i++;
  }

  return <div className="markdown-ai-body">{elements}</div>;
}

function renderTable(tableLines: string[], keyBase: number): React.ReactNode {
  const parseRow = (line: string): string[] =>
    line.split('|').slice(1, -1).map(c => c.trim());

  const headers = parseRow(tableLines[0]);
  // Check if line 2 is a separator (like |---|---|)
  const isSeparator = /^[\s|:-]+$/.test(tableLines[1]);
  const dataStart = isSeparator ? 2 : 1;
  const rows = tableLines.slice(dataStart).map(parseRow);

  return (
    <div key={`table-${keyBase}`} className="my-5 overflow-x-auto rounded-xl border border-white/10 bg-black/30">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="bg-indigo-500/10 border-b border-white/10">
            {headers.map((h, i) => (
              <th key={i} className="px-4 py-3 text-indigo-400 font-bold uppercase tracking-wider text-[10px] font-mono whitespace-nowrap">
                {parseInline(h)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {rows.map((row, ri) => (
            <tr key={ri} className="hover:bg-white/[0.03] transition-colors">
              {row.map((cell, ci) => (
                <td key={ci} className="px-4 py-3 text-gray-300 leading-relaxed text-[12px]">
                  {parseInline(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Parse inline markdown: **bold**, *italic*, `code`, and regular text */
function parseInline(text: string): React.ReactNode {
  if (!text) return null;

  // Split by bold, italic, and code patterns
  const tokens: React.ReactNode[] = [];
  // Regex: match **bold**, *italic*, `code`
  const regex = /(\*\*.*?\*\*|\*.*?\*|`[^`]+`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    // Add text before this match
    if (match.index > lastIndex) {
      tokens.push(text.slice(lastIndex, match.index));
    }

    const matched = match[0];
    if (matched.startsWith('**') && matched.endsWith('**')) {
      tokens.push(
        <strong key={`b-${match.index}`} className="text-white font-semibold">
          {matched.slice(2, -2)}
        </strong>
      );
    } else if (matched.startsWith('`') && matched.endsWith('`')) {
      tokens.push(
        <code key={`c-${match.index}`} className="px-1.5 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-mono text-[11px]">
          {matched.slice(1, -1)}
        </code>
      );
    } else if (matched.startsWith('*') && matched.endsWith('*')) {
      tokens.push(
        <em key={`i-${match.index}`} className="text-gray-200 italic">
          {matched.slice(1, -1)}
        </em>
      );
    }

    lastIndex = match.index + matched.length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    tokens.push(text.slice(lastIndex));
  }

  return tokens.length === 1 ? tokens[0] : <>{tokens}</>;
}
