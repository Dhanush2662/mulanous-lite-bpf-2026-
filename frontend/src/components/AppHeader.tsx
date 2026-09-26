import { Link } from "react-router-dom"

export function AppHeader() {
  return (
    <header className="topbar">
      <Link to="/" className="brand">
        MULANOUS LITE
      </Link>
      <Link to="/" className="home-link">
        HOME
      </Link>
      <p className="demo-mark">SYNTHETIC DEMO</p>
    </header>
  )
}
