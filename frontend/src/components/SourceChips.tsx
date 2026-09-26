export function SourceChips({ names }: { names: readonly string[] }) {
  return (
    <p className="source-chips">
      {names.map((name) => (
        <span key={name}>{name.toUpperCase()}</span>
      ))}
    </p>
  )
}
