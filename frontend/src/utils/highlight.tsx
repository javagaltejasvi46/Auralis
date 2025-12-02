import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { COLORS } from '../config';
import { MatchPosition } from '../types';

/**
 * Find all positions where query matches in text (case-insensitive).
 */
export function findMatchPositions(text: string, query: string): MatchPosition[] {
  if (!text || !query || query.length < 2) {
    return [];
  }

  const positions: MatchPosition[] = [];
  const textLower = text.toLowerCase();
  const queryLower = query.toLowerCase();

  let start = 0;
  while (true) {
    const pos = textLower.indexOf(queryLower, start);
    if (pos === -1) break;
    positions.push({ start: pos, end: pos + query.length });
    start = pos + 1;
  }

  return positions;
}

/**
 * Highlight matching portions of text based on query.
 * Returns React nodes with highlighted spans.
 */
export function highlightText(
  text: string,
  query: string,
  highlightStyle?: object
): React.ReactNode {
  if (!text) return null;
  if (!query || query.length < 2) return text;

  const positions = findMatchPositions(text, query);
  
  if (positions.length === 0) {
    return text;
  }

  const parts: React.ReactNode[] = [];
  let lastEnd = 0;

  positions.forEach((pos, index) => {
    // Add text before the match
    if (pos.start > lastEnd) {
      parts.push(
        <Text key={`text-${index}`}>
          {text.substring(lastEnd, pos.start)}
        </Text>
      );
    }

    // Add highlighted match
    parts.push(
      <Text key={`highlight-${index}`} style={[styles.highlight, highlightStyle]}>
        {text.substring(pos.start, pos.end)}
      </Text>
    );

    lastEnd = pos.end;
  });

  // Add remaining text after last match
  if (lastEnd < text.length) {
    parts.push(
      <Text key="text-end">
        {text.substring(lastEnd)}
      </Text>
    );
  }

  return parts;
}

/**
 * Highlight text using pre-computed match positions from API.
 */
export function highlightWithPositions(
  text: string,
  positions: MatchPosition[],
  highlightStyle?: object
): React.ReactNode {
  if (!text) return null;
  if (!positions || positions.length === 0) return text;

  // Sort positions by start index
  const sortedPositions = [...positions].sort((a, b) => a.start - b.start);
  
  const parts: React.ReactNode[] = [];
  let lastEnd = 0;

  sortedPositions.forEach((pos, index) => {
    // Validate position bounds
    if (pos.start < 0 || pos.end > text.length || pos.start >= pos.end) {
      return;
    }

    // Add text before the match
    if (pos.start > lastEnd) {
      parts.push(
        <Text key={`text-${index}`}>
          {text.substring(lastEnd, pos.start)}
        </Text>
      );
    }

    // Add highlighted match
    parts.push(
      <Text key={`highlight-${index}`} style={[styles.highlight, highlightStyle]}>
        {text.substring(pos.start, pos.end)}
      </Text>
    );

    lastEnd = pos.end;
  });

  // Add remaining text after last match
  if (lastEnd < text.length) {
    parts.push(
      <Text key="text-end">
        {text.substring(lastEnd)}
      </Text>
    );
  }

  return parts.length > 0 ? parts : text;
}

const styles = StyleSheet.create({
  highlight: {
    backgroundColor: 'rgba(133, 163, 179, 0.3)',
    color: COLORS.buttonBackground,
    fontWeight: '600',
  },
});
