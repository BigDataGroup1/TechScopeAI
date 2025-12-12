import React from 'react';

interface ContentRendererProps {
  content: string;
  accentColor?: 'purple' | 'blue' | 'green' | 'orange' | 'teal' | 'indigo';
}

const colorClasses = {
  purple: {
    heading: 'text-purple-800',
    headingBg: 'bg-purple-100',
    headingBorder: 'border-purple-200',
    strong: 'text-purple-700',
    label: 'bg-purple-100 text-purple-700',
    icon: 'text-purple-500',
    bullet: 'text-purple-400',
    roleCard: 'bg-gradient-to-r from-purple-50 to-violet-50 border-purple-200',
  },
  blue: {
    heading: 'text-blue-800',
    headingBg: 'bg-blue-100',
    headingBorder: 'border-blue-200',
    strong: 'text-blue-700',
    label: 'bg-blue-100 text-blue-700',
    icon: 'text-blue-500',
    bullet: 'text-blue-400',
    roleCard: 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200',
  },
  green: {
    heading: 'text-green-800',
    headingBg: 'bg-green-100',
    headingBorder: 'border-green-200',
    strong: 'text-green-700',
    label: 'bg-green-100 text-green-700',
    icon: 'text-green-500',
    bullet: 'text-green-400',
    roleCard: 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200',
  },
  orange: {
    heading: 'text-orange-800',
    headingBg: 'bg-orange-100',
    headingBorder: 'border-orange-200',
    strong: 'text-orange-700',
    label: 'bg-orange-100 text-orange-700',
    icon: 'text-orange-500',
    bullet: 'text-orange-400',
    roleCard: 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200',
  },
  teal: {
    heading: 'text-teal-800',
    headingBg: 'bg-teal-100',
    headingBorder: 'border-teal-200',
    strong: 'text-teal-700',
    label: 'bg-teal-100 text-teal-700',
    icon: 'text-teal-500',
    bullet: 'text-teal-400',
    roleCard: 'bg-gradient-to-r from-teal-50 to-emerald-50 border-teal-200',
  },
  indigo: {
    heading: 'text-indigo-800',
    headingBg: 'bg-indigo-100',
    headingBorder: 'border-indigo-200',
    strong: 'text-indigo-700',
    label: 'bg-indigo-100 text-indigo-700',
    icon: 'text-indigo-500',
    bullet: 'text-indigo-400',
    roleCard: 'bg-gradient-to-r from-indigo-50 to-violet-50 border-indigo-200',
  },
};

const ContentRenderer: React.FC<ContentRendererProps> = ({ content, accentColor = 'purple' }) => {
  if (!content) return null;
  
  const colors = colorClasses[accentColor];
  
  // Parse and render inline formatting
  const renderInline = (text: string): React.ReactNode => {
    // Handle bold text with **text**
    const parts = text.split(/\*\*(.*?)\*\*/g);
    if (parts.length > 1) {
      return parts.map((part, i) => 
        i % 2 === 1 
          ? <strong key={i} className={`font-semibold ${colors.strong}`}>{part}</strong> 
          : <span key={i}>{part}</span>
      );
    }
    return text;
  };

  // Split content into sections by numbered roles (e.g., "1. Role Name")
  const parseContent = () => {
    const lines = content.split('\n');
    const elements: React.ReactElement[] = [];
    let currentSection: { title: string; content: string[] } | null = null;
    let introLines: string[] = [];
    let isInIntro = true;

    lines.forEach((line) => {
      const trimmed = line.trim();
      
      // Check for numbered section header (e.g., "1. Senior Machine Learning Engineer")
      const numberedHeaderMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
      
      if (numberedHeaderMatch && !trimmed.includes('**') && trimmed.length < 80) {
        isInIntro = false;
        // Save previous section
        if (currentSection) {
          elements.push(renderSection(currentSection, elements.length));
        }
        currentSection = {
          title: `${numberedHeaderMatch[1]}. ${numberedHeaderMatch[2]}`,
          content: []
        };
      } else if (isInIntro && trimmed) {
        introLines.push(trimmed);
      } else if (currentSection && trimmed) {
        currentSection.content.push(trimmed);
      }
    });

    // Don't forget the last section
    if (currentSection) {
      elements.push(renderSection(currentSection, elements.length));
    }

    return { introLines, elements };
  };

  const renderSection = (section: { title: string; content: string[] }, key: number) => {
    const fields: { label: string; value: string }[] = [];
    let currentLabel = '';
    let currentValue: string[] = [];
    const bulletPoints: string[] = [];

    section.content.forEach(line => {
      // Check for labeled field like "**Why This Role Is Needed:**"
      const labelMatch = line.match(/^\*\*([^*]+):\*\*\s*(.*)$/);
      
      if (labelMatch) {
        // Save previous field
        if (currentLabel) {
          fields.push({ label: currentLabel, value: currentValue.join(' ') });
        }
        currentLabel = labelMatch[1];
        currentValue = labelMatch[2] ? [labelMatch[2]] : [];
      } else if (line.startsWith('- ') || line.startsWith('• ') || line.startsWith('* ')) {
        // Bullet point within a field
        const bulletText = line.replace(/^[-•*]\s*/, '');
        if (currentLabel) {
          bulletPoints.push(bulletText);
        }
      } else if (currentLabel && line) {
        // Continuation of current field
        currentValue.push(line);
      }
    });

    // Save last field
    if (currentLabel) {
      fields.push({ label: currentLabel, value: currentValue.join(' ') });
    }

    return (
      <div key={key} className={`${colors.roleCard} rounded-xl p-5 border mb-4 shadow-sm`}>
        <h3 className={`text-lg font-bold ${colors.heading} mb-4 pb-2 border-b ${colors.headingBorder}`}>
          {section.title}
        </h3>
        
        <div className="space-y-3">
          {fields.map((field, i) => (
            <div key={i}>
              <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${colors.label} mb-1`}>
                {field.label}
              </span>
              <p className="text-slate-700 text-sm leading-relaxed mt-1">
                {field.value}
              </p>
            </div>
          ))}
          
          {bulletPoints.length > 0 && (
            <ul className="mt-2 space-y-1">
              {bulletPoints.map((point, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className={`${colors.bullet} mt-1`}>•</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  };

  const { introLines, elements } = parseContent();

  // If no numbered sections found, fall back to simple rendering
  if (elements.length === 0) {
    return renderSimple(content, colors);
  }

  return (
    <div className="space-y-4">
      {/* Intro paragraph */}
      {introLines.length > 0 && (
        <div className="mb-6">
          {introLines.map((line, i) => (
            <p key={i} className="text-slate-700 leading-relaxed mb-2">
              {renderInline(line)}
            </p>
          ))}
        </div>
      )}
      
      {/* Role cards */}
      {elements}
    </div>
  );
};

// Fallback simple renderer for non-structured content
const renderSimple = (content: string, colors: typeof colorClasses.purple) => {
  const lines = content.split('\n');
  const elements: React.ReactElement[] = [];
  let listItems: string[] = [];
  let listType: 'ul' | 'ol' | null = null;

  const flushList = () => {
    if (listItems.length > 0 && listType) {
      const ListTag = listType === 'ol' ? 'ol' : 'ul';
      elements.push(
        <ListTag 
          key={elements.length} 
          className={`${listType === 'ol' ? 'list-decimal' : 'list-disc'} list-inside space-y-2 mb-4 ml-2`}
        >
          {listItems.map((item, i) => (
            <li key={i} className="text-slate-700 leading-relaxed">{item}</li>
          ))}
        </ListTag>
      );
      listItems = [];
      listType = null;
    }
  };

  const renderInline = (text: string): React.ReactNode => {
    const parts = text.split(/\*\*(.*?)\*\*/g);
    if (parts.length > 1) {
      return parts.map((part, i) => 
        i % 2 === 1 
          ? <strong key={i} className={`font-semibold ${colors.strong}`}>{part}</strong> 
          : <span key={i}>{part}</span>
      );
    }
    return text;
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    
    if (trimmed.length === 0) {
      flushList();
      return;
    }
    
    // Headers
    if (trimmed.startsWith('#### ')) {
      flushList();
      elements.push(
        <h4 key={index} className={`text-base font-semibold ${colors.heading} mt-4 mb-2`}>
          {trimmed.replace('#### ', '')}
        </h4>
      );
    } else if (trimmed.startsWith('### ')) {
      flushList();
      elements.push(
        <h3 key={index} className={`text-lg font-semibold ${colors.heading} mt-5 mb-3`}>
          {trimmed.replace('### ', '')}
        </h3>
      );
    } else if (trimmed.startsWith('## ')) {
      flushList();
      elements.push(
        <h2 key={index} className={`text-xl font-bold text-slate-800 mt-6 mb-4 pb-2 border-b ${colors.headingBorder}`}>
          {trimmed.replace('## ', '')}
        </h2>
      );
    } else if (trimmed.startsWith('# ')) {
      flushList();
      elements.push(
        <h1 key={index} className="text-2xl font-bold text-slate-900 mb-4">
          {trimmed.replace('# ', '')}
        </h1>
      );
    }
    // Numbered list
    else if (/^\d+\.\s/.test(trimmed)) {
      if (listType !== 'ol') {
        flushList();
        listType = 'ol';
      }
      listItems.push(trimmed.replace(/^\d+\.\s/, ''));
    }
    // Bullet list
    else if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
      if (listType !== 'ul') {
        flushList();
        listType = 'ul';
      }
      listItems.push(trimmed.replace(/^[-*•]\s/, ''));
    }
    // Regular paragraph
    else {
      flushList();
      elements.push(
        <p key={index} className="text-slate-700 mb-3 leading-relaxed">
          {renderInline(trimmed)}
        </p>
      );
    }
  });
  
  flushList();
  return <div className="space-y-1">{elements}</div>;
};

export default ContentRenderer;
