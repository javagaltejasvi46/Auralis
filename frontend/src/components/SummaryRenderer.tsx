import React from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { COLORS } from '../config';

interface SummaryRendererProps {
  summary: string;
  style?: any;
}

export const SummaryRenderer: React.FC<SummaryRendererProps> = ({
  summary,
  style,
}) => {
  // Parse the summary and render with formatting
  const renderFormattedText = () => {
    if (!summary) return null;

    let text = summary;

    // First, normalize different RED formats to a standard format
    // Handle {{RED}}text{{/REDC}} or {{RED}}text{{/RED}} format
    text = text.replace(/\{\{RED\}\}([^{]*)\{\{\/REDC?\}\}/gi, '{{RED:$1}}');

    // Handle {{red:text}} format (already correct, just normalize case)
    text = text.replace(/\{\{red:/gi, '{{RED:');

    // Add newlines before each section header for better formatting
    text = text.replace(/\s*\*\*([^*]+):\*\*/g, '\n**$1:**');
    
    // Remove leading newline if present
    text = text.replace(/^\n/, '');

    // Split by lines first to handle newlines properly
    const lines = text.split('\n');
    
    const elements: JSX.Element[] = [];
    
    lines.forEach((line, lineIndex) => {
      if (lineIndex > 0) {
        // Add line break between lines
        elements.push(<Text key={`br-${lineIndex}`}>{'\n'}</Text>);
      }
      
      // Process each line for bold and red markers
      const parts: Array<{ text: string; bold?: boolean; red?: boolean }> = [];
      const combinedRegex = /(\*\*([^*]+)\*\*|\{\{RED:([^}]+)\}\})/gi;

      let lastIndex = 0;
      let match;

      while ((match = combinedRegex.exec(line)) !== null) {
        // Add text before this match
        if (lastIndex < match.index) {
          const normalText = line.substring(lastIndex, match.index);
          if (normalText) {
            parts.push({ text: normalText });
          }
        }

        // Determine if it's bold or red
        if (match[2]) {
          // Bold match (**text**)
          parts.push({ text: match[2], bold: true });
        } else if (match[3]) {
          // Red match ({{RED:text}})
          parts.push({ text: match[3], red: true });
        }

        lastIndex = match.index + match[0].length;
      }

      // Add remaining text
      if (lastIndex < line.length) {
        const remainingText = line.substring(lastIndex);
        if (remainingText) {
          parts.push({ text: remainingText });
        }
      }

      // If no matches found, just add the plain text
      if (parts.length === 0 && line) {
        parts.push({ text: line });
      }

      // Render the parts for this line
      parts.forEach((part, partIndex) => {
        const key = `${lineIndex}-${partIndex}`;
        if (part.red) {
          elements.push(
            <Text key={key} style={styles.redText}>
              {part.text}
            </Text>
          );
        } else if (part.bold) {
          elements.push(
            <Text key={key} style={styles.boldText}>
              {part.text}
            </Text>
          );
        } else {
          elements.push(<Text key={key}>{part.text}</Text>);
        }
      });
    });

    return <Text style={[styles.summaryText, style]}>{elements}</Text>;
  };

  return <View>{renderFormattedText()}</View>;
};

// Helper function to strip formatting for editing
export const stripFormatting = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\{\{RED:([^}]+)\}\}/gi, '$1')
    .replace(/\{\{RED\}\}([^{]*)\{\{\/REDC?\}\}/gi, '$1');
};

// Helper function to check if text has formatting
export const hasFormatting = (text: string): boolean => {
  if (!text) return false;
  return (
    /\*\*[^*]+\*\*/.test(text) ||
    /\{\{RED:[^}]+\}\}/i.test(text) ||
    /\{\{RED\}\}[^{]*\{\{\/REDC?\}\}/i.test(text)
  );
};

const styles = StyleSheet.create({
  summaryText: {
    fontSize: 15,
    color: COLORS.textOnDarkTeal,
    lineHeight: 26,
  },
  boldText: {
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  redText: {
    fontWeight: 'bold',
    color: '#FF4444',
    backgroundColor: 'rgba(255, 68, 68, 0.2)',
  },
});
