import { Link } from "react-router-dom"

export function AppHeader() {
  return (
    <header className="topbar">
      <Link to="/" className="home-link">
        HOME
      </Link>
    </header>
  )
}
