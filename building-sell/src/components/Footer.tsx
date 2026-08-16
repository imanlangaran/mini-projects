export default function Footer() {
  return (
    <footer className="border-t border-hairline bg-ink px-4 py-10 text-paper/60 sm:px-8 lg:px-12">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div className="label-mono flex items-center gap-3">
          <span className="grid h-5 w-5 place-items-center border border-paper/30">
            <span className="block h-1.5 w-1.5 bg-accent" />
          </span>
          MERIDIAN
        </div>
        <p className="label-mono">
          Denver, CO — <a className="underline-offset-4 hover:text-paper hover:underline" href="mailto:studio@meridian.build">studio@meridian.build</a>
        </p>
        <p className="label-mono">
          © {new Date().getFullYear()} Meridian Development Co.
        </p>
      </div>
    </footer>
  );
}