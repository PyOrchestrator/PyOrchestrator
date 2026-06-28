import type { editor } from "monaco-editor";

export const editorTheme: editor.IStandaloneThemeData = {
  base: "vs-dark",
  inherit: true,
  rules: [
    { token: "comment", foreground: "71717a", fontStyle: "italic" },
    { token: "keyword", foreground: "c084fc" },
    { token: "string", foreground: "34d399" },
    { token: "number", foreground: "fbbf24" },
    { token: "function", foreground: "22d3ee" },
  ],
  colors: {
    "editor.background": "#09090b",
    "editor.foreground": "#e4e4e7",
    "editor.lineHighlightBackground": "#18181b",
    "editor.selectionBackground": "#22d3ee33",
    "editor.inactiveSelectionBackground": "#22d3ee18",
    "editorLineNumber.foreground": "#52525b",
    "editorLineNumber.activeForeground": "#a1a1aa",
    "editorCursor.foreground": "#22d3ee",
    "editorIndentGuide.background": "#27272a",
    "editorIndentGuide.activeBackground": "#3f3f46",
    "editorWidget.background": "#18181b",
    "editorWidget.border": "#ffffff14",
    "minimap.background": "#09090b",
    "scrollbarSlider.background": "#ffffff14",
    "scrollbarSlider.hoverBackground": "#ffffff24",
  },
};

export function defineEditorTheme(monaco: typeof import("monaco-editor")) {
  monaco.editor.defineTheme("pyorch-dark", editorTheme);
}
