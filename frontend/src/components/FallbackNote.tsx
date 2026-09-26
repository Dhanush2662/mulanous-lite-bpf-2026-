export function FallbackNote({ source, text }: { source: "api" | "fallback"; text: string }) {
  if (source !== "fallback") {
    return null
  }
  return <p className="fallback-note">{text}</p>
}
