/** @odoo-module **/

const KEYWORDS = [
    'def', 'class', 'import', 'from', 'return', 'if', 'elif', 'else',
    'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass',
    'lambda', 'yield', 'raise', 'assert', 'global', 'nonlocal', 'del',
    'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'
];

const BUILTINS = [
    'print', 'len', 'range', 'enumerate', 'zip', 'map', 'filter', 'list',
    'dict', 'set', 'tuple', 'int', 'float', 'str', 'bool', 'super',
    'isinstance', 'issubclass', 'type', 'dir', 'help', 'getattr', 'setattr', 'hasattr'
];

const ESCAPE_HTML = (str) => {
    return str.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
};

export function highlightPython(code) {
    if (!code) return "";

    // 1. Escape HTML first to prevent XSS and ensure layout safety
    // BUT we need to process tokens before escaping for complex regex...
    // ACTUALLY, usually better to tokenise, then escape content, then wrap.
    // Given our simple regex approach, we'll replace into placeholders or handle carefully.

    // Simplest approach: "Tokenize" execution by matching regexes and building the string.
    // But regex replacements on strings are easier if we are careful.

    // Let's go with a sequential token replacement approach using a master regex?
    // Or just simple replacements. The order matters (Strings usage first!).

    // NOTE: This is a "good enough" highlighter for a simple shell.

    let html = code;

    // We will use a placeholder temporary replacement strategy to avoid re-matching html
    // However, JS regex replace with a function is cleaner.

    // Order:
    // 1. Strings (Docstrings first, then single/double)
    // 2. Comments
    // 3. Keywords / Builtins
    // 4. Numbers
    // 5. Decorators

    // We cannot easily modify 'html' in place efficiently without breaking ranges.
    // So we'll iterate through the string and tokenize.

    // Actually, `Prism` does this well. Since we are custom, let's use a "Split and Map" strategy?
    // No, that's complex for a simple request.

    // Let's use the replacement approach but escape *during* replacement.
    // Wait, if we escape first: `print("a < b")` -> `print("a &lt; b")`
    // Then string regex `".*?"` might fail if it expects `<`.
    // Correct way: Match raw code, wrap match in span (with content escaped).

    // Master Regex for Python tokens (simplified)
    // 1. Triple-quoted strings:  /("""[\s\S]*?"""|'''[\s\S]*?''')/
    // 2. Comments:  /(#.*)$/m
    // 3. Strings:   /("|')((?:\\\1|(?:(?!\1).))*)\1/
    // 4. Numbers:   /\b\d+(\.\d+)?\b/
    // 5. Keywords:  /\b(def|class|...)\b/
    // 6. Decorators: /@\w+/

    // We must Combine them or run sequentially? 
    // Sequentially is dangerous (matching inside strings).
    // Combined regex is best.

    const tokenRegex = /("""[\s\S]*?"""|'''[\s\S]*?''')|(#.*$)|("|'|`)(?:\\\3|(?:(?!\3).))*\3|(\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z_]\w*\b)/gm;

    html = code.replace(tokenRegex, (match, tripleString, comment, string, number, word) => {
        if (tripleString) {
            return `<span class="s">${ESCAPE_HTML(tripleString)}</span>`;
        }
        if (comment) {
            return `<span class="c">${ESCAPE_HTML(comment)}</span>`;
        }
        if (string) {
            return `<span class="s">${ESCAPE_HTML(match)}</span>`; // match includes quotes
        }
        if (number) {
            return `<span class="n">${match}</span>`;
        }
        if (word) {
            if (KEYWORDS.includes(word)) {
                return `<span class="k">${word}</span>`;
            }
            if (BUILTINS.includes(word)) {
                return `<span class="nb">${word}</span>`;
            }
            if (word === 'self') {
                return `<span class="o">${word}</span>`;
            }
            return word; // Just a variable/identifier
        }
        return ESCAPE_HTML(match); // Fallback
    });

    // Decorators (special case, usually starts with @)
    // The main regex doesn't catch @word well as a block.
    // Let's run a separate pass for things NOT inside spans? 
    // Hard.

    // Better: Add decorator to main regex.
    // New Regex:
    // Group 1: Triple Strings
    // Group 2: Comments
    // Group 3: Strings
    // Group 4: Decorators (@xxxx)
    // Group 5: Numbers
    // Group 6: Words

    // Note: Regex order is priority.

    // We'll perform one master replace.
    // If it doesn't match a token (e.g. spaces, operators), it remains as is (but we must escape it!).
    // Wait, string.replace(regex) only replaces matches. The non-matches need escaping too!

    // So we need to: tokenize -> map -> join.

    const styles = {
        triple: 's',
        comment: 'c',
        string: 's',
        decorator: 'd',
        number: 'n',
        keyword: 'k',
        builtin: 'nb',
        self: 'o'
    };

    const re = /("""[\s\S]*?"""|'''[\s\S]*?''')|(#.*$)|("|')(?:\\\3|(?:(?!\3).))*\3|(@\w+)|(\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z_]\w*\b)/gm;

    let lastIndex = 0;
    let result = "";

    let match;
    while ((match = re.exec(code)) !== null) {
        // Text before match
        if (match.index > lastIndex) {
            result += ESCAPE_HTML(code.slice(lastIndex, match.index));
        }

        const fullMatch = match[0];

        // Determine type
        if (match[1]) { // Triple
            result += `<span class="${styles.triple}">${ESCAPE_HTML(fullMatch)}</span>`;
        } else if (match[2]) { // Comment
            result += `<span class="${styles.comment}">${ESCAPE_HTML(fullMatch)}</span>`;
        } else if (match[3]) { // String
            result += `<span class="${styles.string}">${ESCAPE_HTML(fullMatch)}</span>`;
        } else if (match[4]) { // Decorator
            result += `<span class="${styles.decorator}">${ESCAPE_HTML(fullMatch)}</span>`;
        } else if (match[5]) { // Number
            result += `<span class="${styles.number}">${fullMatch}</span>`; // numbers don't need escape usually
        } else if (match[6]) { // Word
            const w = fullMatch;
            if (KEYWORDS.includes(w)) {
                result += `<span class="${styles.keyword}">${w}</span>`;
            } else if (BUILTINS.includes(w)) {
                result += `<span class="${styles.builtin}">${w}</span>`;
            } else if (w === 'self') {
                result += `<span class="${styles.self}">${w}</span>`;
            } else {
                result += w;
            }
        }

        lastIndex = re.lastIndex;
    }

    // Remaining text
    if (lastIndex < code.length) {
        result += ESCAPE_HTML(code.slice(lastIndex));
    }

    return result;
}
