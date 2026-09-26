import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"
import "@fontsource/inter/400.css"
import "@fontsource/inter/500.css"
import "@fontsource/ibm-plex-mono/400.css"

import { App } from "./App"
import "./styles.css"

const root = document.getElementById("root")
if (!root) {
  throw new Error("Root element missing")
}

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
