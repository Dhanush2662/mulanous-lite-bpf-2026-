import { Route, Routes, useParams } from "react-router-dom"

import { AttentionTodayPage } from "./pages/AttentionTodayPage"
import { CaseBriefPage } from "./pages/CaseBriefPage"

export function App() {
  return (
    <Routes>
      <Route path="/" element={<AttentionTodayPage />} />
      <Route path="/cases/:caseId" element={<CaseRoute />} />
    </Routes>
  )
}

function CaseRoute() {
  const { caseId = "" } = useParams()
  return <CaseBriefPage key={caseId} />
}
