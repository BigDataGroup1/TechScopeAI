/**
 * Utility functions for markdown processing
 */

/**
 * Strip markdown formatting from text
 * Used for PDF generation and plain text display
 */
export const stripMarkdown = (text) => {
  if (!text) return '';
  
  return String(text)
    // Remove headers (# ## ### ####)
    .replace(/^#{1,6}\s+(.+)$/gm, '$1')
    // Remove bold (**text** or __text__)
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/__(.+?)__/g, '$1')
    // Remove italic (*text* or _text_)
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/_(.+?)_/g, '$1')
    // Remove code blocks (```code```)
    .replace(/```[\s\S]*?```/g, '')
    // Remove inline code (`code`)
    .replace(/`([^`]+)`/g, '$1')
    // Remove links [text](url)
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
    // Remove images ![alt](url)
    .replace(/!\[([^\]]*)\]\([^\)]+\)/g, '')
    // Remove horizontal rules (--- or ***)
    .replace(/^[-*]{3,}$/gm, '')
    // Remove list markers (- * +)
    .replace(/^[\s]*[-*+]\s+/gm, '• ')
    // Remove numbered list markers (1. 2. etc)
    .replace(/^\d+\.\s+/gm, '')
    // Clean up multiple newlines
    .replace(/\n{3,}/g, '\n\n')
    // Trim whitespace
    .trim();
};
