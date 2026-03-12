/**
 * Detect if text contains RTL (right-to-left) languages like Hebrew or Arabic
 */
export function isRTL(text: string): boolean {
  // Hebrew: \u0590-\u05FF
  // Arabic: \u0600-\u06FF
  // Farsi: \u06A0-\u06FF
  const rtlRegex = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F]/;
  return rtlRegex.test(text);
}

/**
 * Detect dominant language direction in text (RTL or LTR)
 * Counts RTL characters and returns true if they dominate
 */
export function detectTextDirection(text: string): 'rtl' | 'ltr' {
  const rtlChars = (text.match(/[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F]/g) || []).length;
  const ltrChars = (text.match(/[a-zA-Z0-9]/g) || []).length;

  // If more than 30% of characters are RTL, consider it RTL
  const total = rtlChars + ltrChars;
  return total > 0 && rtlChars > total * 0.3 ? 'rtl' : 'ltr';
}
