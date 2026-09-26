import { CaseBrief } from "@/features/case-brief/case-brief";

export default async function CasePage({
  params,
}: {
  params: Promise<{ caseId: string }>;
}) {
  const { caseId } = await params;
  return <CaseBrief caseId={caseId} />;
}
