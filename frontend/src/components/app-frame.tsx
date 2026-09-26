import Link from "next/link";

export function AppFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#080808] text-[#F7F4EC]">
      <header className="border-b border-[#2F2D28]">
        <div className="mx-auto flex max-w-[1120px] items-end justify-between gap-4 px-4 py-4 sm:px-6">
          <Link href="/" className="block">
            <p className="font-mono text-[11px] tracking-[0.22em] text-[#D5A942]">
              MULANOUS LITE
            </p>
            <p className="mt-1 text-sm text-[#A5A198]">Operational decision</p>
          </Link>
          <p className="font-mono text-[11px] tracking-[0.16em] text-[#D5A942]">
            SYNTHETIC DEMO
          </p>
        </div>
      </header>
      <main className="mx-auto max-w-[1120px] px-4 py-8 sm:px-6">{children}</main>
    </div>
  );
}
