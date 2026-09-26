import { Button } from "@/components/ui/button";

export function StatusNotice({
  title,
  detail,
  onRetry,
  alert = false,
}: {
  title: string;
  detail?: string;
  onRetry?: () => void;
  alert?: boolean;
}) {
  return (
    <div
      className="border border-[#2F2D28] bg-[#0B0B0C] px-5 py-6"
      role={alert ? "alert" : "status"}
    >
      <p className="text-base text-[#F7F4EC]">{title}</p>
      {detail ? <p className="mt-2 text-sm text-[#A5A198]">{detail}</p> : null}
      {onRetry ? (
        <Button className="mt-4" variant="outline" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}
