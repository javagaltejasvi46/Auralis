import React from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { COLORS } from '../config';

interface SummaryRendererProps {
  summary: string;
  style?: any;
}

export const SummaryRenderer: React.FC<SummaryRendererProps> = ({ summary, style }) => {
  // Parse the summary and render with formatting
  const renderFormattedText = () => {
    const parts: JSX.Element[] = [];
    let currentIndex = 0;
    let key = 0;

    // Split by markdown bold (**text**)
    const boldRegex = /\*\*(.*?)\*\*/g;
    // Split by red markers ({{RED:text}})
    const redRegex = /\{\{RED:(.*?)\}\}/g;

    let lastIndex = 0;
    const text = summary;

    // Process the text
    const processedParts: Array<{ text: string; bold?: boolean; red?: boolean }> = [];
    
    // First, find all bold and red markers
    const allMatches: Array<{ start: number; end: number; text: string; type: 'bold' | 'red' }> = [];
    
    // Find bold matches
    let match;
    while ((match = boldRegex.exec(text)) !== null) {
      allMatches.push({
        start: match.index,
        end: match.index + match[0].length,
        text: match[1],
        type: 'bold'
      });
    }
    
    // Find red matches
    while ((match = redRegex.exec(text)) !== null) {
      allMatches.push({
        start: match.index,
        end: match.index + match[0].length,
        text: match[1],
        type: 'red'
      });
    }
    
    // Sort by start position
    allMatches.sort((a, b) => a.start - b.start);
    
    // Build the parts array
    let currentPos = 0;
    allMatches.forEach((match) => {
      // Add text before this match
      if (currentPos < match.start) {
        const normalText = text.substring(currentPos, match.start);
        if (normalText) {
          processedParts.push({ text: normalText });
        }
      }
      
      // Add the matched text with formatting
      processedParts.push({
        text: match.text,
        bold: match.type === 'bold',
        red: match.type === 'red'
      });
      
      currentPos = match.end;
    });
    
    // Add remaining text
    if (currentPos < text.length) {
      const remainingText = text.substring(currentPos);
      if (remainingText) {
        processedParts.push({ text: remainingText });
      }
    }
    
    // Render the parts
    return (
      <Text style={[styles.summaryText, style]}>
        {processedParts.map((part, index) => {
          if (part.red) {
            return (
              <Text key={index} style={styles.redText}>
                {part.text}
              </Text>
            );
          } else if (part.bold) {
            return (
              <Text key={index} style={styles.boldText}>
                {part.text}
              </Text>
            );
          } else {
            return <Text key={index}>{part.text}</Text>;
          }
        })}
      </Text>
    );
  };

  return <View>{renderFormattedText()}</View>;
};

const styles = StyleSheet.create({
  summaryText: {
    fontSize: 15,
    color: COLORS.textOnDarkTeal,
    lineHeight: 22,
  },
  boldText: {
    fontWeight: 'bold',
    color: COLORS.textOnDarkTeal,
  },
  redText: {
    fontWeight: 'bold',
    color: '#FF3B30', // iOS red
    backgroundColor: 'rgba(255, 59, 48, 0.1)',
    paddingHorizontal: 4,
    paddingVertical: 2,
  },
});
