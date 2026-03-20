from datetime import datetime, timezone


def format_markdown(md, sector=""):
    """clean up the AI output and slap a footer on it"""
    md = md.strip()

    # collapse runs of blank lines (AI sometimes goes overboard)
    lines = md.split("\n")
    out = []
    blanks = 0
    for line in lines:
        if line.strip() == "":
            blanks += 1
            if blanks <= 2:
                out.append(line)
        else:
            blanks = 0
            out.append(line)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    footer = (
        f"\n\n---\n"
        f"*Report generated on {ts} | "
        f"Sector: {sector.title() if sector else 'N/A'} | "
        f"Trade Opportunities API v1.0*\n"
    )
    return "\n".join(out) + footer
